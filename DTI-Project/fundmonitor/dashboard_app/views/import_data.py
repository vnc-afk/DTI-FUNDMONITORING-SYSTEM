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

from dashboard_app.forms import ImportDataForm
from dashboard_app.models import Supplier, BankStatement


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
                
                # Store result in session for display
                request.session['import_result'] = result
                
                return redirect('import_result')
            
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'import/import_form.html', {'form': form})
            
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
    return render(request, 'import/import_form.html', context)


def import_result(request):
    """Display import results"""
    result = request.session.pop('import_result', None)
    
    if not result:
        messages.warning(request, 'No import results found.')
        return redirect('import_data')
    
    context = {
        'result': result,
        'page_title': 'Import Results',
    }
    return render(request, 'import/import_result.html', context)


def process_import(data_type, file_path, skip_errors, sheet_name=None, skip_rows=0):
    """
    Process the import based on data type
    Returns a dictionary with import results
    """
    
    if data_type == 'supplier':
        return process_supplier_import(file_path, skip_errors, sheet_name, skip_rows)
    elif data_type == 'bank_statement':
        return process_bank_statement_import(file_path, skip_errors, sheet_name, skip_rows)
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
            supplier, created = Supplier.objects.get_or_create(
                supplier=supplier_data['supplier'],
                defaults=supplier_data
            )
            
            if created:
                result['created'] += 1
            else:
                # Update existing
                for key, value in supplier_data.items():
                    if key != 'supplier':
                        setattr(supplier, key, value)
                supplier.full_clean()
                supplier.save()
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
                    date_obj = datetime.strptime(row['date'].strip(), '%Y-%m-%d').date()
                else:
                    date_obj = pd.to_datetime(row['date']).date()
            except Exception as e:
                raise ValueError(f"Invalid date format '{row['date']}'. Expected YYYY-MM-DD")
            
            # Parse balance
            try:
                balance = Decimal(str(row['balance']).replace(',', ''))
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
            
            if 'status' in row and pd.notna(row['status']):
                status = str(row['status']).strip()
                if status in ['Cleared', 'On Process']:
                    stmt_data['status'] = status
            
            # Create bank statement
            statement = BankStatement(**stmt_data)
            statement.full_clean()
            statement.save()
            
            result['created'] += 1
        
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
