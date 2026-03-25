"""Data import views - handle file uploads and bulk data imports"""

import os
import tempfile
import re
from io import StringIO
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.management import call_command
from django.core.exceptions import ValidationError
import pandas as pd

from data_management_app.forms import ImportDataForm
from bank_statement_app.models import BankStatement
from data_management_app.models import Supplier, Staff
from dashboard_app.utils.decorators import regular_user_cannot_edit
from dashboard_app.utils.activity_logging import log_custom_action


DATA_TYPE_MODEL_NAMES = {
    'supplier': 'Supplier',
    'bank_statement': 'BankStatement',
    'master_fund_monitoring': 'MasterFundMonitoring',
    'staff': 'Staff',
}


def _log_import_activity(request, uploaded_file, data_type, result, skip_errors, sheet_name=None, skip_rows=0):
    """Create a single activity log entry for each import attempt."""
    model_name = DATA_TYPE_MODEL_NAMES.get(data_type, data_type)
    status_text = 'successful' if result.get('success') else 'failed'
    total_rows = result.get('total_rows', 0)
    created = result.get('created', 0)
    updated = result.get('updated', 0)
    skipped = result.get('skipped', 0)
    errors = result.get('errors', 0)

    description = (
        f"{model_name} import {status_text}. "
        f"File: {uploaded_file.name}. "
        f"Total: {total_rows}, Created: {created}, Updated: {updated}, "
        f"Skipped: {skipped}, Errors: {errors}. "
        f"Skip errors: {'Yes' if skip_errors else 'No'}, "
        f"Sheet: {sheet_name or 'Default'}, Skip rows: {skip_rows}."
    )

    if errors and result.get('error_details'):
        first_error = result['error_details'][0]
        description += f" First error: {first_error}"

    log_custom_action(
        request=request,
        action='IMPORT',
        model_name=model_name,
        object_repr=uploaded_file.name,
        description=description,
    )


def sanitize_name(name):
    """
    Clean name by removing numbers and truly invalid characters.
    Preserves: letters (including accented), spaces, hyphens, periods, apostrophes
    """
    if not name:
        return name
    
    name = str(name).strip()
    
    # Remove numbers
    name = re.sub(r'\d', '', name)
    
    # Remove other invalid characters (keep letters including accented, spaces, hyphens, periods, apostrophes)
    # This pattern removes anything that's not: letter (including accented), space, hyphen, period, apostrophe, or high-value Unicode
    name = re.sub(r"[^a-zA-Z\s\-\.'\u0080-\uFFFF]", '', name)
    
    # Clean up multiple spaces
    name = re.sub(r'\s+', ' ', name)
    
    return name.strip()


@regular_user_cannot_edit
def import_data(request):
    """Display import form and handle file uploads"""
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            data_type = form.cleaned_data['data_type']
            skip_errors = form.cleaned_data['skip_errors']
            sheet_name = form.cleaned_data.get('sheet_name', '').strip() or None
            skip_rows = form.cleaned_data.get('skip_rows', 0) or 0
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(uploaded_file.name)[1]
            ) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
            
            try:
                # Process the import
                result = process_import(data_type, tmp_path, skip_errors, sheet_name, skip_rows)

                # Record import attempt in activity logs with summary details.
                _log_import_activity(
                    request,
                    uploaded_file,
                    data_type,
                    result,
                    skip_errors,
                    sheet_name,
                    skip_rows,
                )
                
                # Store result in session for display
                request.session['import_result'] = result
                
                return redirect('import_result')
            
            except Exception as e:
                log_custom_action(
                    request=request,
                    action='IMPORT',
                    model_name=DATA_TYPE_MODEL_NAMES.get(data_type, data_type),
                    object_repr=uploaded_file.name,
                    description=f"{DATA_TYPE_MODEL_NAMES.get(data_type, data_type)} import failed. "
                                f"File: {uploaded_file.name}. Error: {str(e)}",
                )
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'dashboard_app/import/import_form.html', {'form': form})
            
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    
    else:
        form = ImportDataForm()
    
    context = {
        'form': form,
        'page_title': 'Import Data',
    }
    return render(request, 'dashboard_app/import/import_form.html', context)


def import_result(request):
    """Display import results"""
    result = request.session.pop('import_result', None)
    
    if not result:
        messages.warning(request, 'No import results found.')
        return redirect('import_data')
    
    summary_cards = [
        {
            'label': 'Total Rows',
            'value': result.get('total_rows', 0),
            'description': 'Rows in file',
            'is_currency': False,
        },
        {
            'label': 'Created',
            'value': result.get('created', 0),
            'description': 'New records added',
            'is_currency': False,
        },
        {
            'label': 'Errors',
            'value': result.get('errors', 0),
            'description': 'Failed to import',
            'is_currency': False,
        },
    ]

    if result.get('updated'):
        summary_cards.insert(
            2,
            {
                'label': 'Updated',
                'value': result.get('updated', 0),
                'description': 'Updated existing',
                'is_currency': False,
            },
        )

    context = {
        'result': result,
        'page_title': 'Import Results',
        'summary_cards': summary_cards,
    }
    return render(request, 'dashboard_app/import/import_result.html', context)


def process_import(data_type, file_path, skip_errors, sheet_name=None, skip_rows=0):
    """
    Process the import based on data type
    Returns a dictionary with import results
    """
    
    if data_type == 'supplier':
        return process_supplier_import(file_path, skip_errors, sheet_name, skip_rows)
    elif data_type == 'bank_statement':
        return process_bank_statement_import(file_path, skip_errors, sheet_name, skip_rows)
    elif data_type == 'master_fund_monitoring':
        return process_master_fund_monitoring_import(file_path, skip_errors, sheet_name, skip_rows)
    elif data_type == 'staff':
        return process_staff_import(file_path, skip_errors, sheet_name, skip_rows)
    else:
        raise ValueError(f'Unknown data type: {data_type}')


def process_supplier_import(file_path, skip_errors, sheet_name=None, skip_rows=0):
    """Process supplier data import"""
    try:
        # Handle Excel files with sheet selection
        if file_path.endswith(('.xlsx', '.xls')):
            # Try to read with specified sheet name and skip_rows
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
            except ValueError as e:
                # Sheet not found - try to list available sheets
                if sheet_name:
                    available_sheets = pd.ExcelFile(file_path).sheet_names
                    raise ValueError(
                        f'Sheet "{sheet_name}" not found.\n'
                        f'Available sheets: {", ".join(available_sheets)}'
                    )
                else:
                    raise
        else:
            df = pd.read_csv(file_path, skiprows=skip_rows)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f'Error reading file: {str(e)}')
    
    if len(df) == 0:
        raise ValueError('File is empty')
    
    # Normalize column names
    normalized_cols = []
    for col in df.columns:
        col_str = str(col).lower().strip()
        normalized_cols.append(col_str)
    df.columns = normalized_cols
    
    # Standardize supplier column names (handle variations like spaces and different naming)
    supplier_col_mapping = {
        'philgeps registration': 'philgeps_registration',
        'contact number': 'contact_number',
    }
    
    # Handle unnamed columns - the blank column should be vat_status (between tin and philgeps_registration)
    actual_cols = list(df.columns)
    col_mapping = {}
    
    # Apply standard variations mapping
    for old_col, new_col in supplier_col_mapping.items():
        if old_col in actual_cols:
            col_mapping[old_col] = new_col
    
    # Handle unnamed columns - find position and assign vat_status if in expected position
    unnamed_cols = [col for col in actual_cols if col.startswith('unnamed:')]
    if unnamed_cols:
        # If we have a TIN column and an unnamed column after it, that unnamed is vat_status
        try:
            tin_idx = actual_cols.index('tin')
            for unnamed_col in unnamed_cols:
                unnamed_idx = actual_cols.index(unnamed_col)
                if unnamed_idx == tin_idx + 1:
                    col_mapping[unnamed_col] = 'vat_status'
        except ValueError:
            pass
    
    if col_mapping:
        df = df.rename(columns=col_mapping)
    
    # Validate required columns
    if 'supplier' not in df.columns:
        found_cols = list(df.columns)
        raise ValueError(
            f'Missing required column: "supplier"\n'
            f'Found columns: {", ".join(found_cols)}'
        )
    
    result = {
        'data_type': 'Suppliers',
        'total_rows': len(df),
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'error_details': [],
        'success': False,
    }
    
    for idx, row in df.iterrows():
        try:
            row_num = idx + 2  # +2 for header and 0-indexing
            
            # Skip empty rows
            if pd.isna(row['supplier']) or str(row['supplier']).strip() == '':
                result['skipped'] += 1
                continue
            
            # Prepare supplier data
            supplier_data = {
                'supplier': str(row['supplier']).strip(),
            }
            
            # Add optional fields with defaults to prevent NOT NULL constraint violations
            if 'tin' in row and pd.notna(row['tin']):
                supplier_data['tin'] = str(row['tin']).strip()
            else:
                supplier_data['tin'] = ''
            
            # Always include vat_status, default to '—' if missing or invalid
            if 'vat_status' in row and pd.notna(row['vat_status']):
                vat = str(row['vat_status']).strip()
                if vat in ['NV', 'V', '—']:
                    supplier_data['vat_status'] = vat
                else:
                    supplier_data['vat_status'] = '—'
            else:
                supplier_data['vat_status'] = '—'
            
            if 'philgeps_registration' in row and pd.notna(row['philgeps_registration']):
                supplier_data['philgeps_registration'] = str(row['philgeps_registration']).strip()
            else:
                supplier_data['philgeps_registration'] = ''
            
            if 'address' in row and pd.notna(row['address']):
                supplier_data['address'] = str(row['address']).strip()
            else:
                supplier_data['address'] = ''
            
            if 'propprietor' in row and pd.notna(row['propprietor']):
                supplier_data['propprietor'] = str(row['propprietor']).strip()
            else:
                supplier_data['propprietor'] = ''
            
            # Always include contact_number, use empty string if missing
            if 'contact_number' in row and pd.notna(row['contact_number']):
                supplier_data['contact_number'] = str(row['contact_number']).strip()
            else:
                supplier_data['contact_number'] = ''
            
            # Create or update supplier
            # Use supplier name as unique identifier
            supplier_name = supplier_data['supplier']
            
            supplier, created = Supplier.objects.update_or_create(
                supplier=supplier_name,
                defaults={k: v for k, v in supplier_data.items() 
                         if k != 'supplier'}
            )
            
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        
        except ValidationError as e:
            result['errors'] += 1
            error_msg = str(e) if isinstance(e, str) else ', '.join(e.messages)
            result['error_details'].append({
                'row': row_num,
                'error': error_msg,
            })
            if not skip_errors:
                raise ValueError(f"Row {row_num}: {error_msg}")
        
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append({
                'row': row_num,
                'error': str(e),
            })
            if not skip_errors:
                raise ValueError(f"Row {row_num}: {str(e)}")
    
    result['success'] = result['errors'] == 0
    return result


def process_staff_import(file_path, skip_errors, sheet_name=None, skip_rows=0):
    """Process staff data import - expects a file with staff names in a single column"""
    try:
        # Handle Excel files with sheet selection
        if file_path.endswith(('.xlsx', '.xls')):
            # Try to read with specified sheet name and skip_rows
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows, header=None)
            except ValueError as e:
                # If sheet not found, try with None (first sheet)
                if 'not found' in str(e).lower():
                    df = pd.read_excel(file_path, sheet_name=0, skiprows=skip_rows, header=None)
                else:
                    raise
        else:
            df = pd.read_csv(file_path, skiprows=skip_rows, header=None)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f'Error reading file: {str(e)}')
    
    if len(df) == 0:
        raise ValueError('File is empty')
    
    # Use first column for staff names
    staff_column = df.iloc[:, 0]
    
    result = {
        'data_type': 'Staff',
        'total_rows': len(df),
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'error_details': [],
        'success': False,
    }
    
    for idx, name in staff_column.items():
        try:
            row_num = idx + 1 + skip_rows
            
            # Skip empty rows
            if pd.isna(name) or str(name).strip() == '':
                result['skipped'] += 1
                continue
            
            # Clean and prepare staff name
            staff_name = str(name).strip()
            
            if not staff_name:
                result['skipped'] += 1
                continue
            
            # Parse full name into first, middle initial, and last name
            # Format: "First Middle Initial Last" where Middle Initial is 1-2 letters
            # Examples:
            # - "John Michael G. Smith" → First: John Michael, Middle: G, Last: Smith
            # - "Maria Elena D Rodriguez" → First: Maria Elena, Middle: D, Last: Rodriguez
            # - "Smith, John Michael G." → Last: Smith, First: John Michael, Middle: G
            
            staff_name = str(name).strip()
            first_name = ''
            middle_initial = ''
            last_name = ''
            
            # Check if name has comma (Format: "Last, First Middle Initial")
            if ',' in staff_name:
                parts = staff_name.split(',')
                if len(parts) >= 2:
                    last_name = parts[0].strip()
                    rest = parts[1].strip()
                    
                    # Parse first and middle from remaining part
                    # Look for a 1-2 letter word as middle initial
                    name_words = rest.split()
                    
                    # Find middle initial (1-2 letter word)
                    middle_idx = -1
                    for i, word in enumerate(name_words):
                        word_clean = word.rstrip('.')
                        if len(word_clean) <= 2:
                            middle_idx = i
                            middle_initial = word_clean
                            break
                    
                    if middle_idx >= 0:
                        # Everything before middle initial is first name
                        first_name = ' '.join(name_words[:middle_idx])
                        # Everything after middle initial is additional last name parts
                        if middle_idx + 1 < len(name_words):
                            extra = ' '.join(name_words[middle_idx + 1:])
                            last_name = f"{last_name}, {extra}"
                    else:
                        # No middle initial found, split differently
                        if len(name_words) == 1:
                            first_name = name_words[0]
                        else:
                            first_name = ' '.join(name_words[:-1])
            else:
                # Format: "First Middle Initial Last"
                name_words = staff_name.split()
                
                # Find middle initial (1-2 letter word) - typically toward the end
                middle_idx = -1
                for i, word in enumerate(name_words):
                    word_clean = word.rstrip('.')
                    if len(word_clean) <= 2:
                        middle_idx = i
                        middle_initial = word_clean
                        break
                
                if middle_idx >= 0 and middle_idx > 0 and middle_idx < len(name_words) - 1:
                    # Valid middle initial found with words before and after
                    first_name = ' '.join(name_words[:middle_idx])
                    last_name = ' '.join(name_words[middle_idx + 1:])
                else:
                    # No valid middle initial, parse as: First ... Last
                    if len(name_words) == 1:
                        first_name = name_words[0]
                        last_name = name_words[0]
                    elif len(name_words) == 2:
                        first_name = name_words[0]
                        last_name = name_words[1]
                    else:
                        # Multiple words: first is first, last is last, rest go with first
                        first_name = ' '.join(name_words[:-1])
                        last_name = name_words[-1]
            
            # Sanitize all names to remove accents, numbers, and invalid characters
            first_name = sanitize_name(first_name)
            last_name = sanitize_name(last_name)
            middle_initial = sanitize_name(middle_initial)
            
            # Validate names
            if not first_name or len(first_name) < 2:
                raise ValueError(f'Invalid first name: "{first_name}" (minimum 2 characters required)')
            if not last_name or len(last_name) < 2:
                raise ValueError(f'Invalid last name: "{last_name}" (minimum 2 characters required)')
            
            # Create or update staff record
            staff, created = Staff.objects.update_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'middle_initial': middle_initial}
            )
            
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append({
                'row': row_num,
                'error': str(e),
            })
            if not skip_errors:
                raise ValueError(f"Row {row_num}: {str(e)}")
    
    result['success'] = result['errors'] == 0
    return result


def process_bank_statement_import(file_path, skip_errors, sheet_name=None, skip_rows=0):
    """Process bank statement data import"""
    try:
        # Handle Excel files with sheet selection
        if file_path.endswith(('.xlsx', '.xls')):
            # Try to read with specified sheet name and skip_rows
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
            except ValueError as e:
                # Sheet not found - try to list available sheets
                if sheet_name:
                    available_sheets = pd.ExcelFile(file_path).sheet_names
                    raise ValueError(
                        f'Sheet "{sheet_name}" not found.\n'
                        f'Available sheets: {", ".join(available_sheets)}'
                    )
                else:
                    raise
        else:
            df = pd.read_csv(file_path, skiprows=skip_rows)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f'Error reading file: {str(e)}')
    
    if len(df) == 0:
        raise ValueError('File is empty')
    
    # Normalize column names
    normalized_cols = []
    for col in df.columns:
        col_str = str(col).lower().strip()
        normalized_cols.append(col_str)
    df.columns = normalized_cols
    
    # Standardize bank statement column names (handle variations)
    bank_col_mapping = {
        'check no.': 'check_number',
        'check no': 'check_number',
    }
    
    # Apply standard variations mapping
    col_mapping = {}
    for old_col, new_col in bank_col_mapping.items():
        if old_col in df.columns:
            col_mapping[old_col] = new_col
    
    if col_mapping:
        df = df.rename(columns=col_mapping)
    
    # Validate required columns
    required_cols = ['date', 'description', 'balance']
    found_cols = list(df.columns)
    missing = [col for col in required_cols if col not in found_cols]
    if missing:
        raise ValueError(
            f'Missing required columns: {", ".join(missing)}\n'
            f'Found columns: {", ".join(found_cols)}\n'
            f'Make sure column names are: date, description, balance'
        )
    
    from datetime import datetime
    from decimal import Decimal
    
    result = {
        'data_type': 'Bank Statements',
        'total_rows': len(df),
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'error_details': [],
        'success': False,
    }
    
    for idx, row in df.iterrows():
        try:
            row_num = idx + 2
            
            # Skip empty rows
            if pd.isna(row['description']) or str(row['description']).strip() == '':
                result['skipped'] += 1
                continue
            
            # Parse date
            if pd.isna(row['date']):
                raise ValueError('Date cannot be empty')
            
            try:
                if isinstance(row['date'], str):
                    date_str = row['date'].strip()
                    # Try multiple common date formats
                    date_formats = [
                        '%Y-%m-%d',      # YYYY-MM-DD
                        '%m/%d/%y',      # M/D/YY or MM/DD/YY
                        '%m/%d/%Y',      # M/D/YYYY or MM/DD/YYYY
                        '%m-%d-%y',      # M-D-YY or MM-DD-YY
                        '%m-%d-%Y',      # M-D-YYYY or MM-DD-YYYY
                        '%d/%m/%y',      # D/M/YY or DD/MM/YY
                        '%d/%m/%Y',      # D/M/YYYY or DD/MM/YYYY
                    ]
                    date_obj = None
                    for date_format in date_formats:
                        try:
                            date_obj = datetime.strptime(date_str, date_format).date()
                            break
                        except ValueError:
                            continue
                    
                    if date_obj is None:
                        # Last resort: try pandas date parser
                        date_obj = pd.to_datetime(date_str).date()
                else:
                    date_obj = pd.to_datetime(row['date']).date()
            except Exception as e:
                raise ValueError(f"Invalid date format '{row['date']}'. Supported formats: YYYY-MM-DD, MM/DD/YYYY, MM/DD/YY")
            
            # Parse balance with consistent rounding
            try:
                balance = Decimal(str(row['balance']).replace(',', '')).quantize(Decimal('0.01'))
            except Exception as e:
                raise ValueError(f"Invalid balance '{row['balance']}'. Must be a number")
            
            # Parse debit and credit
            debit = Decimal('0')
            credit = Decimal('0')
            
            if 'debit' in row and pd.notna(row['debit']):
                try:
                    debit = Decimal(str(row['debit']).replace(',', ''))
                except:
                    raise ValueError(f"Invalid debit amount '{row['debit']}'")
            
            if 'credit' in row and pd.notna(row['credit']):
                try:
                    credit = Decimal(str(row['credit']).replace(',', ''))
                except:
                    raise ValueError(f"Invalid credit amount '{row['credit']}'")
            
            # Validate debit/credit logic
            if debit > 0 and credit > 0:
                raise ValueError('Cannot have both debit and credit. Only one should have a value.')
            
            if debit == 0 and credit == 0:
                raise ValueError('At least one of debit or credit must be non-zero.')
            
            # Prepare data
            stmt_data = {
                'date': date_obj,
                'description': str(row['description']).strip(),
                'balance': balance,
                'debit': debit if debit > 0 else Decimal('0'),
                'credit': credit if credit > 0 else Decimal('0'),
            }
            
            if 'check_number' in row and pd.notna(row['check_number']):
                # Convert to string, removing .0 if it's a numeric value
                check_num = row['check_number']
                if isinstance(check_num, float) and check_num == int(check_num):
                    stmt_data['check_number'] = str(int(check_num))
                else:
                    stmt_data['check_number'] = str(check_num).strip()
            else:
                stmt_data['check_number'] = ''
            
            if 'status' in row and pd.notna(row['status']):
                status = str(row['status']).strip()
                if status in ['Cleared', 'On Process']:
                    stmt_data['status'] = status
            
            # Create or update bank statement
            # Use date, description, check_number, debit, and credit as unique identifiers
            lookup_fields = {
                'date': stmt_data['date'],
                'description': stmt_data['description'],
                'debit': stmt_data['debit'],
                'credit': stmt_data['credit'],
            }
            
            # Add check_number to lookup only if it's not empty
            if stmt_data['check_number']:
                lookup_fields['check_number'] = stmt_data['check_number']
            
            # Try to get existing record
            try:
                statement = BankStatement.objects.get(**lookup_fields)
                created = False
                
                # On re-import, only update status field (don't touch balance or lookup fields)
                if 'status' in stmt_data:
                    BankStatement.objects.filter(pk=statement.pk).update(status=stmt_data['status'])
                    
            except BankStatement.DoesNotExist:
                created = True
                # Create new record with all fields including balance
                statement = BankStatement.objects.create(**stmt_data)
                # Keep imported balance exactly as provided in the file.
                BankStatement.objects.filter(pk=statement.pk).update(balance=stmt_data['balance'])
            
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        
        except ValidationError as e:
            result['errors'] += 1
            error_msg = str(e) if isinstance(e, str) else ', '.join(e.messages)
            result['error_details'].append({
                'row': row_num,
                'error': error_msg,
            })
            if not skip_errors:
                raise ValueError(f"Row {row_num}: {error_msg}")
        
        except ValueError as e:
            result['errors'] += 1
            result['error_details'].append({
                'row': row_num,
                'error': str(e),
            })
            if not skip_errors:
                raise
    
    result['success'] = result['errors'] == 0
    return result


def process_master_fund_monitoring_import(file_path, skip_errors, sheet_name=None, skip_rows=0):
    """Process Master Fund Monitoring data import"""
    from data_management_app.models import (
        Division,
        ExpenseCategory,
        ExpenseObject,
        FundSource,
        NegosyoCenter,
        PurchaseType,
    )
    from mater_fundmonitor_app.models import MasterFundMonitoring
    
    # Helper function to round Decimal to 2 decimal places
    def round_decimal(value):
        """Round Decimal value to 2 decimal places"""
        if isinstance(value, Decimal):
            return value.quantize(Decimal('0.01'))
        return value
    
    try:
        # Handle Excel files with sheet selection
        if file_path.endswith(('.xlsx', '.xls')):
            # Try to read with specified sheet name and skip_rows
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
            except ValueError as e:
                # Sheet not found - try to list available sheets
                if sheet_name:
                    available_sheets = pd.ExcelFile(file_path).sheet_names
                    raise ValueError(
                        f'Sheet "{sheet_name}" not found.\n'
                        f'Available sheets: {", ".join(available_sheets)}'
                    )
                else:
                    raise
        else:
            df = pd.read_csv(file_path, skiprows=skip_rows)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f'Error reading file: {str(e)}')
    
    if len(df) == 0:
        raise ValueError('File is empty')
    
    # Normalize column names to lowercase and remove special characters like asterisks
    normalized_cols = []
    for col in df.columns:
        col_str = str(col).lower().strip()
        # Remove asterisks and other common markers from column names
        col_str = col_str.replace('*', '').strip()
        normalized_cols.append(col_str)
    df.columns = normalized_cols
    
    # Standardize column name variations
    mfm_col_mapping = {
        'month': 'month',
        'division': 'division',
        'fund source': 'fund_source',
        'fund_source': 'fund_source',
        'mooe': 'mooe',
        'nc': 'nc',
        'date': 'date',
        'payee': 'payee',
        'particulars': 'particulars',
        'tin (auto)': 'tin',
        'tin': 'tin',
        'tax type': 'tax_type',
        'purchase type': 'purchase_type',
        'purchases': 'purchases',
        'downloads': 'downloads',
        'payments': 'payments',
        'dv no.': 'dv_number',
        'dv no': 'dv_number',
        'dv number': 'dv_number',
        'cheque no.': 'cheque_number',
        'cheque no': 'cheque_number',
        'cheque number': 'cheque_number',
        'cleared date': 'cleared_date',
        'account title': 'account_title',
        'goods (5%)': 'goods_5_percent',
        'services (5%)': 'services_5_percent',
        'goods & sevices (3%)': 'goods_services_3_percent',
        'goods & services (3%)': 'goods_services_3_percent',
        'goods (1%)': 'goods_1_percent',
        'services (2%)': 'services_2_percent',
        'rental (5%)': 'rental_5_percent',
        'prof. fee (10%)': 'prof_fee_10_percent',
        'professional fee (10%)': 'prof_fee_10_percent',
        'expense classification': 'expense_classification',
        'cheque status': 'cheque_status',
        'staff': 'staff',
    }
    
    # Apply column mapping
    col_mapping = {}
    for old_col, new_col in mfm_col_mapping.items():
        if old_col in df.columns:
            col_mapping[old_col] = new_col
    
    if col_mapping:
        df = df.rename(columns=col_mapping)
    
    # Validate required columns
    required_cols = ['date', 'payee', 'particulars']
    found_cols = list(df.columns)
    missing = [col for col in required_cols if col not in found_cols]
    if missing:
        raise ValueError(
            f'Missing required columns: {", ".join(missing)}\n'
            f'Found columns: {", ".join(found_cols)}\n'
            f'Make sure to include: date, payee, particulars'
        )
    
    result = {
        'data_type': 'Master Fund Monitoring',
        'total_rows': len(df),
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'error_details': [],
        'success': False,
        'debug': [],  # Add debug info
    }
    
    # Add column debug info
    result['debug'].append(f"Columns found: {list(df.columns)}")
    
    for idx, row in df.iterrows():
        try:
            row_num = idx + 2  # +2 for header and 0-indexing
            
            # Skip empty rows
            if pd.isna(row['payee']) or str(row['payee']).strip() == '':
                result['skipped'] += 1
                continue
            
            
            # Parse date
            if pd.isna(row['date']):
                raise ValueError('Date cannot be empty')
            
            try:
                if isinstance(row['date'], str):
                    date_str = row['date'].strip()
                    # Try multiple common date formats
                    date_formats = [
                        '%Y-%m-%d',      # YYYY-MM-DD
                        '%m/%d/%y',      # M/D/YY or MM/DD/YY
                        '%m/%d/%Y',      # M/D/YYYY or MM/DD/YYYY
                        '%m-%d-%y',      # M-D-YY or MM-DD-YY
                        '%m-%d-%Y',      # M-D-YYYY or MM-DD-YYYY
                        '%d/%m/%y',      # D/M/YY or DD/MM/YY
                        '%d/%m/%Y',      # D/M/YYYY or DD/MM/YYYY
                    ]
                    date_obj = None
                    for date_format in date_formats:
                        try:
                            date_obj = datetime.strptime(date_str, date_format).date()
                            break
                        except ValueError:
                            continue
                    
                    if date_obj is None:
                        # Last resort: try pandas date parser
                        date_obj = pd.to_datetime(date_str).date()
                else:
                    date_obj = pd.to_datetime(row['date']).date()
            except Exception as e:
                raise ValueError(f"Invalid date format '{row['date']}'. Supported formats: YYYY-MM-DD, MM/DD/YYYY, MM/DD/YY")
            
            # Get or create payee (Supplier)
            payee_name = str(row['payee']).strip()
            try:
                payee = Supplier.objects.get(supplier=payee_name)
            except Supplier.DoesNotExist:
                # Create supplier if not exists
                payee = Supplier.objects.create(supplier=payee_name)
            
            # Prepare monitoring data
            particulars = str(row['particulars']).strip() if pd.notna(row['particulars']) else ''
            
            # Ensure particulars meets minimum 5 character requirement
            # If empty or too short, provide a default value
            if len(particulars) < 5:
                particulars = 'Transaction'  # Default value when particulars is blank or too short
            
            mfm_data = {
                'date': date_obj,
                'payee': payee,
                'particulars': particulars,
            }
            
            # Optional: Division
            if 'division' in row and pd.notna(row['division']):
                try:
                    div_value = str(row['division']).strip()
                    # Try exact match first, then case-insensitive, then partial match
                    division = Division.objects.filter(name__iexact=div_value).first()
                    if not division:
                        # Try partial match
                        division = Division.objects.filter(name__icontains=div_value).first()
                    if division:
                        mfm_data['division'] = division
                except Exception:
                    pass
            
            # Optional: Fund Source
            if 'fund_source' in row and pd.notna(row['fund_source']):
                try:
                    fs_value = str(row['fund_source']).strip()
                    # Try exact match first, then case-insensitive, then partial match
                    # FundSource uses 'name' field, not 'source'
                    fund_source = FundSource.objects.filter(name__iexact=fs_value).first()
                    if not fund_source:
                        # Try partial match
                        fund_source = FundSource.objects.filter(name__icontains=fs_value).first()
                    if fund_source:
                        mfm_data['fund_source'] = fund_source
                except Exception:
                    pass
            
            # Optional: MOOE
            if 'mooe' in row and pd.notna(row['mooe']):
                mooe_value = str(row['mooe']).strip()
                if mooe_value:
                    mfm_data['mooe'] = mooe_value
            
            # Optional: NC (Negosyo Center)
            if 'nc' in row and pd.notna(row['nc']):
                try:
                    nc_value = str(row['nc']).strip()
                    # Try exact match first, then case-insensitive, then partial match
                    nc = NegosyoCenter.objects.filter(name__iexact=nc_value).first()
                    if not nc:
                        # Try partial match
                        nc = NegosyoCenter.objects.filter(name__icontains=nc_value).first()
                    if nc:
                        mfm_data['nc'] = nc
                except Exception:
                    pass
            
            # Optional: TIN - convert 0 to "—"
            if 'tin' in row and pd.notna(row['tin']):
                tin_val = str(row['tin']).strip()
                if tin_val and tin_val != '0':
                    mfm_data['tin'] = tin_val
                else:
                    mfm_data['tin'] = '—'
            
            # Optional: Tax Type - default to "—" if empty or 0
            if 'tax_type' in row and pd.notna(row['tax_type']):
                tax_val = str(row['tax_type']).strip()
                if tax_val and tax_val != '0':
                    mfm_data['tax_type'] = tax_val
                else:
                    mfm_data['tax_type'] = '—'
            else:
                mfm_data['tax_type'] = '—'
            
            # Optional: Purchase Type
            if 'purchase_type' in row and pd.notna(row['purchase_type']):
                try:
                    pt_value = str(row['purchase_type']).strip()
                    # Try exact match first, then case-insensitive, then partial match
                    purchase_type = PurchaseType.objects.filter(name__iexact=pt_value).first()
                    if not purchase_type:
                        # Try partial match
                        purchase_type = PurchaseType.objects.filter(name__icontains=pt_value).first()
                    if purchase_type:
                        mfm_data['purchase_type'] = purchase_type
                except Exception:
                    pass
            
            # Optional: Financial fields
            if 'payments' in row and pd.notna(row['payments']):
                try:
                    mfm_data['payments'] = round_decimal(Decimal(str(row['payments']).replace(',', '')))
                except:
                    pass
            
            if 'downloads' in row and pd.notna(row['downloads']):
                try:
                    mfm_data['downloads'] = round_decimal(Decimal(str(row['downloads']).replace(',', '')))
                except:
                    pass
            
            # Optional: DV Number
            if 'dv_number' in row and pd.notna(row['dv_number']):
                dv_num = row['dv_number']
                if isinstance(dv_num, float) and dv_num == int(dv_num):
                    mfm_data['dv_number'] = str(int(dv_num))
                else:
                    mfm_data['dv_number'] = str(dv_num).strip()
            
            # Optional: Cheque Number
            if 'cheque_number' in row and pd.notna(row['cheque_number']):
                cheque_num = row['cheque_number']
                if isinstance(cheque_num, float) and cheque_num == int(cheque_num):
                    mfm_data['cheque_number'] = str(int(cheque_num))
                else:
                    mfm_data['cheque_number'] = str(cheque_num).strip()
            
            # Optional: Cleared Date
            if 'cleared_date' in row and pd.notna(row['cleared_date']):
                try:
                    if isinstance(row['cleared_date'], str):
                        date_str = row['cleared_date'].strip()
                        # Try multiple common date formats
                        date_formats = [
                            '%Y-%m-%d',      # YYYY-MM-DD
                            '%m/%d/%y',      # M/D/YY or MM/DD/YY
                            '%m/%d/%Y',      # M/D/YYYY or MM/DD/YYYY
                            '%m-%d-%y',      # M-D-YY or MM-DD-YY
                            '%m-%d-%Y',      # M-D-YYYY or MM-DD-YYYY
                            '%d/%m/%y',      # D/M/YY or DD/MM/YY
                            '%d/%m/%Y',      # D/M/YYYY or DD/MM/YYYY
                        ]
                        for date_format in date_formats:
                            try:
                                mfm_data['cleared_date'] = datetime.strptime(date_str, date_format).date()
                                break
                            except ValueError:
                                continue
                        else:
                            # Last resort: try pandas date parser
                            mfm_data['cleared_date'] = pd.to_datetime(date_str).date()
                    else:
                        mfm_data['cleared_date'] = pd.to_datetime(row['cleared_date']).date()
                except:
                    pass
            
            # Optional: Account Title (ExpenseObject)
            if 'account_title' in row and pd.notna(row['account_title']):
                try:
                    acc_value = str(row['account_title']).strip()
                    # Strip code prefix like "(5020101000)." from the beginning
                    import re
                    acc_value_clean = re.sub(r'^\(\d+\)\.\s*', '', acc_value).strip()
                    # Try exact match first on cleaned value
                    account = ExpenseObject.objects.filter(name__iexact=acc_value_clean).first()
                    if not account:
                        # Try partial match on cleaned value
                        account = ExpenseObject.objects.filter(name__icontains=acc_value_clean).first()
                    if not account and acc_value != acc_value_clean:
                        # Try original value as fallback
                        account = ExpenseObject.objects.filter(name__iexact=acc_value).first()
                    if not account and acc_value != acc_value_clean:
                        account = ExpenseObject.objects.filter(name__icontains=acc_value).first()
                    if account:
                        mfm_data['account_title'] = account
                except Exception:
                    pass
            
            # Optional: Tax breakdown fields (first set)
            if 'goods_5_percent' in row and pd.notna(row['goods_5_percent']):
                try:
                    mfm_data['goods_5_percent'] = round_decimal(Decimal(str(row['goods_5_percent']).replace(',', '')))
                except:
                    pass
            
            if 'services_5_percent' in row and pd.notna(row['services_5_percent']):
                try:
                    mfm_data['services_5_percent'] = round_decimal(Decimal(str(row['services_5_percent']).replace(',', '')))
                except:
                    pass
            
            if 'goods_services_3_percent' in row and pd.notna(row['goods_services_3_percent']):
                try:
                    mfm_data['goods_services_3_percent'] = round_decimal(Decimal(str(row['goods_services_3_percent']).replace(',', '')))
                except:
                    pass
            
            if 'goods_1_percent' in row and pd.notna(row['goods_1_percent']):
                try:
                    mfm_data['goods_1_percent'] = round_decimal(Decimal(str(row['goods_1_percent']).replace(',', '')))
                except:
                    pass
            
            if 'services_2_percent' in row and pd.notna(row['services_2_percent']):
                try:
                    mfm_data['services_2_percent'] = round_decimal(Decimal(str(row['services_2_percent']).replace(',', '')))
                except:
                    pass
            
            if 'rental_5_percent' in row and pd.notna(row['rental_5_percent']):
                try:
                    mfm_data['rental_5_percent'] = round_decimal(Decimal(str(row['rental_5_percent']).replace(',', '')))
                except:
                    pass
            
            if 'prof_fee_10_percent' in row and pd.notna(row['prof_fee_10_percent']):
                try:
                    mfm_data['prof_fee_10_percent'] = round_decimal(Decimal(str(row['prof_fee_10_percent']).replace(',', '')))
                except:
                    pass
            
            # Optional: Expense Classification
            if 'expense_classification' in row and pd.notna(row['expense_classification']):
                try:
                    ec_value = str(row['expense_classification']).strip()
                    # Try exact match first, then case-insensitive, then partial match
                    expense_cat = ExpenseCategory.objects.filter(name__iexact=ec_value).first()
                    if not expense_cat:
                        # Try partial match
                        expense_cat = ExpenseCategory.objects.filter(name__icontains=ec_value).first()
                    if expense_cat:
                        mfm_data['expense_classification'] = expense_cat
                except Exception:
                    pass
            
            # Optional: Cheque Status
            if 'cheque_status' in row and pd.notna(row['cheque_status']):
                status = str(row['cheque_status']).strip()
                if status in ['Pending', 'Cleared']:
                    mfm_data['cheque_status'] = status
            
            # Optional: Staff
            if 'staff' in row and pd.notna(row['staff']):
                from data_management_app.models import Staff
                try:
                    staff_value = str(row['staff']).strip()
                    staff = None
                    
                    # Try exact match on first_name first
                    staff = Staff.objects.filter(first_name__iexact=staff_value).first()
                    if not staff:
                        # Try partial match on first_name
                        staff = Staff.objects.filter(first_name__icontains=staff_value).first()
                    if not staff:
                        # Try last_name
                        staff = Staff.objects.filter(last_name__iexact=staff_value).first()
                    if not staff:
                        # Try partial match on last_name
                        staff = Staff.objects.filter(last_name__icontains=staff_value).first()
                    if not staff:
                        # Try matching last name from full name (e.g., "Aizle B. Hilario" -> "Hilario")
                        name_parts = staff_value.split()
                        if len(name_parts) > 0:
                            # Try last word as last name
                            last_name_candidate = name_parts[-1]
                            staff = Staff.objects.filter(last_name__iexact=last_name_candidate).first()
                            if not staff:
                                staff = Staff.objects.filter(last_name__icontains=last_name_candidate).first()
                    if not staff:
                        # Try matching first word as first name
                        name_parts = staff_value.split()
                        if len(name_parts) > 0:
                            first_name_candidate = name_parts[0]
                            staff = Staff.objects.filter(first_name__iexact=first_name_candidate).first()
                            if not staff:
                                staff = Staff.objects.filter(first_name__icontains=first_name_candidate).first()
                    
                    if staff:
                        mfm_data['staff'] = staff
                except Exception:
                    pass
            
            # Create or update Master Fund Monitoring record
            # Use date, payee, particulars, payments, downloads, and cheque_number as unique identifiers to prevent duplicates
            lookup_fields = {
                'date': mfm_data['date'],
                'payee': mfm_data['payee'],
                'particulars': mfm_data['particulars'],
            }
            
            # Add payments and downloads to lookup if they exist
            if 'payments' in mfm_data:
                lookup_fields['payments'] = mfm_data['payments']
            if 'downloads' in mfm_data:
                lookup_fields['downloads'] = mfm_data['downloads']
            if 'cheque_number' in mfm_data:
                lookup_fields['cheque_number'] = mfm_data['cheque_number']
            
            mfm, created = MasterFundMonitoring.objects.update_or_create(
                **lookup_fields,
                defaults={k: v for k, v in mfm_data.items() 
                         if k not in lookup_fields}
            )
            mfm.full_clean()
            mfm.save()
            
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        
        except ValidationError as e:
            result['errors'] += 1
            error_msg = str(e) if isinstance(e, str) else ', '.join(e.messages)
            result['error_details'].append({
                'row': row_num,
                'error': error_msg,
            })
            if not skip_errors:
                raise ValueError(f"Row {row_num}: {error_msg}")
        
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append({
                'row': row_num,
                'error': str(e),
            })
            if not skip_errors:
                raise ValueError(f"Row {row_num}: {str(e)}")
    
    result['success'] = result['errors'] == 0
    
    # Format debug info for display
    if result['debug']:
        formatted_debug = []
        for item in result['debug']:
            if isinstance(item, dict):
                formatted_debug.append(str(item))
            else:
                formatted_debug.append(str(item))
        result['debug'] = formatted_debug
    
    return result

