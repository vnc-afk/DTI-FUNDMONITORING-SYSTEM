from datetime import datetime, timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from data_management_app.models import (
    Division,
    District,
    ExpenseCategory,
    ExpenseObject,
    FundSource,
    NegosyoCenter,
    PurchaseType,
    Staff,
    Supplier,
)
from bank_statement_app.models import BankAccount
from mater_fundmonitor_app.models import MasterFundMonitoring
from bank_statement_app.models import BankStatement


class Command(BaseCommand):
    help = "Populate the database with sample data for testing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting to populate sample data..."))

        try:
            # Create Divisions
            self.stdout.write("Creating Divisions...")
            divisions = self._create_divisions()

            # Create Districts
            self.stdout.write("Creating Districts...")
            districts = self._create_districts()

            # Create Expense Categories
            self.stdout.write("Creating Expense Categories...")
            categories = self._create_expense_categories()

            # Create Expense Objects
            self.stdout.write("Creating Expense Objects...")
            objects = self._create_expense_objects()

            # Create Purchase Types
            self.stdout.write("Creating Purchase Types...")
            purchase_types = self._create_purchase_types()

            # Create Fund Sources
            self.stdout.write("Creating Fund Sources...")
            fund_sources = self._create_fund_sources()

            # Create Suppliers
            self.stdout.write("Creating Suppliers...")
            suppliers = self._create_suppliers()

            # Create Staff
            self.stdout.write("Creating Staff...")
            staff_members = self._create_staff(divisions)

            # Create Negosyo Centers
            self.stdout.write("Creating Negosyo Centers...")
            nc_list = self._create_negosyo_centers(districts)

            # Create Bank Accounts
            self.stdout.write("Creating Bank Accounts...")
            bank_accounts = self._create_bank_accounts()

            # Create Bank Statements
            self.stdout.write("Creating Bank Statements...")
            self._create_bank_statements(bank_accounts)

            # Create Master Fund Monitoring Records
            self.stdout.write("Creating Master Fund Monitoring Records...")
            self._create_master_fund_monitoring(
                divisions, fund_sources, suppliers, nc_list, purchase_types, 
                categories, objects, staff_members
            )

            self.stdout.write(
                self.style.SUCCESS("✓ Sample data population completed successfully!")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            raise

    def _create_divisions(self):
        """Create sample divisions"""
        divisions_data = [
            {"name": "Finance", "description": "Finance and Treasury Division"},
            {"name": "Operations", "description": "Operations and Administration"},
            {"name": "Procurement", "description": "Procurement Division"},
            {"name": "Human Resources", "description": "Human Resources Division"},
            {"name": "Planning", "description": "Planning and Development Division"},
        ]
        
        divisions = []
        for data in divisions_data:
            division, created = Division.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"], "is_active": True}
            )
            if created:
                self.stdout.write(f"  Created Division: {division.name}")
            divisions.append(division)
        
        return divisions

    def _create_districts(self):
        """Create sample districts"""
        districts_data = [
            {"name": "District 1", "description": "First District"},
            {"name": "District 2", "description": "Second District"},
            {"name": "District 3", "description": "Third District"},
            {"name": "District 4", "description": "Fourth District"},
        ]
        
        districts = []
        for idx, data in enumerate(districts_data, 1):
            district, created = District.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "order": idx,
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"  Created District: {district.name}")
            districts.append(district)
        
        return districts

    def _create_expense_categories(self):
        """Create sample expense categories"""
        categories_data = [
            {"name": "Personnel", "color": "#3498db", "description": "Personnel and salary expenses"},
            {"name": "Operations", "color": "#2ecc71", "description": "Operational expenses"},
            {"name": "Capital", "color": "#e74c3c", "description": "Capital expenditures"},
            {"name": "Maintenance", "color": "#f39c12", "description": "Maintenance and repairs"},
            {"name": "Supplies", "color": "#9b59b6", "description": "Office supplies and materials"},
        ]
        
        categories = []
        for data in categories_data:
            category, created = ExpenseCategory.objects.get_or_create(
                name=data["name"],
                defaults={
                    "color": data["color"],
                    "description": data["description"],
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"  Created Expense Category: {category.name}")
            categories.append(category)
        
        return categories

    def _create_expense_objects(self):
        """Create sample expense objects"""
        objects_data = [
            {"code": "5010-01", "name": "Salaries and Wages", "color": "#3498db"},
            {"code": "5020-01", "name": "Employee Benefits", "color": "#2ecc71"},
            {"code": "6010-01", "name": "Repairs and Maintenance", "color": "#e74c3c"},
            {"code": "6020-01", "name": "Utilities", "color": "#f39c12"},
            {"code": "6030-01", "name": "Office Supplies", "color": "#9b59b6"},
            {"code": "6040-01", "name": "Equipment", "color": "#1abc9c"},
            {"code": "7010-01", "name": "Travel and Transportation", "color": "#34495e"},
            {"code": "7020-01", "name": "Training and Development", "color": "#e67e22"},
        ]
        
        objects = []
        for data in objects_data:
            obj, created = ExpenseObject.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "color": data["color"],
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"  Created Expense Object: {obj.code} - {obj.name}")
            objects.append(obj)
        
        return objects

    def _create_purchase_types(self):
        """Create sample purchase types"""
        purchase_types_data = [
            "Goods",
            "Services",
            "Supplies",
            "Equipment",
            "Repairs and Maintenance",
        ]
        
        purchase_types = []
        for name in purchase_types_data:
            pt, created = PurchaseType.objects.get_or_create(
                name=name,
                defaults={"is_active": True}
            )
            if created:
                self.stdout.write(f"  Created Purchase Type: {pt.name}")
            purchase_types.append(pt)
        
        return purchase_types

    def _create_fund_sources(self):
        """Create sample fund sources"""
        fund_sources_data = [
            {"name": "General Fund", "annual_budget": Decimal("5000000.00")},
            {"name": "Development Fund", "annual_budget": Decimal("3000000.00")},
            {"name": "Contingency Fund", "annual_budget": Decimal("1000000.00")},
            {"name": "Special Purpose Fund", "annual_budget": Decimal("2000000.00")},
        ]
        
        fund_sources = []
        for data in fund_sources_data:
            fs, created = FundSource.objects.get_or_create(
                name=data["name"],
                defaults={"annual_budget": data["annual_budget"]}
            )
            if created:
                self.stdout.write(f"  Created Fund Source: {fs.name}")
            fund_sources.append(fs)
        
        return fund_sources

    def _create_suppliers(self):
        """Create sample suppliers"""
        suppliers_data = [
            {
                "supplier": "ABC Trading Corporation",
                "tin": "123-456-789-001",
                "vat_status": "V",
                "address": "123 Main Street, Metro Manila",
                "propprietor": "Juan dela Cruz",
                "contact_number": "02-1234-5678",
            },
            {
                "supplier": "XYZ Services Inc",
                "tin": "987-654-321-002",
                "vat_status": "V",
                "address": "456 Business Ave, Makati",
                "propprietor": "Maria Santos",
                "contact_number": "02-9876-5432",
            },
            {
                "supplier": "General Supplies Ltd",
                "tin": "555-666-777-003",
                "vat_status": "NV",
                "address": "789 Trade Street, Quezon City",
                "propprietor": "Pedro Reyes",
                "contact_number": "02-5555-6666",
            },
            {
                "supplier": "Professional Services Group",
                "tin": "111-222-333-004",
                "vat_status": "V",
                "address": "321 Professional Plaza, Ortigas",
                "propprietor": "Ana Rodriguez",
                "contact_number": "02-1111-2222",
            },
            {
                "supplier": "Equipment & Maintenance Solutions",
                "tin": "999-888-777-005",
                "vat_status": "V",
                "address": "654 Industrial Park, Santa Rosa",
                "propprietor": "Ricardo Garcia",
                "contact_number": "02-9999-8888",
            },
        ]
        
        suppliers = []
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                supplier=data["supplier"],
                defaults={
                    "tin": data["tin"],
                    "vat_status": data["vat_status"],
                    "address": data["address"],
                    "propprietor": data["propprietor"],
                    "contact_number": data["contact_number"],
                }
            )
            if created:
                self.stdout.write(f"  Created Supplier: {supplier.supplier}")
            suppliers.append(supplier)
        
        return suppliers

    def _create_staff(self, divisions):
        """Create sample staff"""
        staff_data = [
            {"first_name": "John", "middle_initial": "M", "last_name": "Santos"},
            {"first_name": "Maria", "middle_initial": "C", "last_name": "Garcia"},
            {"first_name": "Robert", "middle_initial": "L", "last_name": "Cruz"},
            {"first_name": "Anna", "middle_initial": "P", "last_name": "Lopez"},
            {"first_name": "Carlos", "middle_initial": "R", "last_name": "Reyes"},
            {"first_name": "Patricia", "middle_initial": "A", "last_name": "Gonzales"},
            {"first_name": "Miguel", "middle_initial": "S", "last_name": "Rodriguez"},
            {"first_name": "Diana", "middle_initial": "E", "last_name": "Villanueva"},
        ]
        
        staff_members = []
        for idx, data in enumerate(staff_data):
            division = divisions[idx % len(divisions)]
            staff, created = Staff.objects.get_or_create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                defaults={
                    "middle_initial": data["middle_initial"],
                    "division": division,
                }
            )
            if created:
                self.stdout.write(f"  Created Staff: {staff}")
            staff_members.append(staff)
        
        return staff_members

    def _create_negosyo_centers(self, districts):
        """Create sample Negosyo Centers"""
        centers_data = [
            {"district_idx": 0, "name": "North Center", "code": "neg-001"},
            {"district_idx": 0, "name": "Central Hub", "code": "neg-002"},
            {"district_idx": 1, "name": "East Center", "code": "neg-003"},
            {"district_idx": 1, "name": "Commercial Center", "code": "neg-004"},
            {"district_idx": 2, "name": "South Center", "code": "neg-005"},
            {"district_idx": 3, "name": "West Center", "code": "neg-006"},
        ]
        
        nc_list = []
        for data in centers_data:
            district = districts[data["district_idx"]]
            nc, created = NegosyoCenter.objects.get_or_create(
                district=district,
                code=data["code"],
                defaults={"name": data["name"], "is_active": True}
            )
            if created:
                self.stdout.write(f"  Created Negosyo Center: {nc.name}")
            nc_list.append(nc)
        
        return nc_list

    def _create_bank_accounts(self):
        """Create sample bank accounts"""
        accounts_data = [
            {
                "name": "Operating Account",
                "account_number": "123456789001",
                "opening_balance": Decimal("500000.00"),
            },
            {
                "name": "Development Account",
                "account_number": "123456789002",
                "opening_balance": Decimal("300000.00"),
            },
            {
                "name": "Contingency Account",
                "account_number": "123456789003",
                "opening_balance": Decimal("100000.00"),
            },
        ]
        
        accounts = []
        for data in accounts_data:
            account, created = BankAccount.objects.get_or_create(
                account_number=data["account_number"],
                defaults={
                    "name": data["name"],
                    "opening_balance": data["opening_balance"],
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(f"  Created Bank Account: {account.name}")
            accounts.append(account)
        
        return accounts

    def _create_bank_statements(self, bank_accounts):
        """Create sample bank statements"""
        base_date = timezone.now().date()
        statement_count = 0

        for bank_account in bank_accounts:
            opening_balance = bank_account.opening_balance
            running_balance = opening_balance

            # Create 10 sample transactions per bank account
            transactions_data = [
                {"date_offset": 30, "description": "Initial deposit", "credit": Decimal("100000.00"), "check_number": ""},
                {"date_offset": 29, "description": "Utility payment", "debit": Decimal("5000.00"), "check_number": "CHK-0001"},
                {"date_offset": 28, "description": "Supplier invoice payment", "debit": Decimal("25000.00"), "check_number": "CHK-0002"},
                {"date_offset": 27, "description": "Interest credit", "credit": Decimal("500.00"), "check_number": ""},
                {"date_offset": 26, "description": "Equipment purchase", "debit": Decimal("50000.00"), "check_number": "CHK-0003"},
                {"date_offset": 25, "description": "Refund received", "credit": Decimal("10000.00"), "check_number": ""},
                {"date_offset": 24, "description": "Maintenance expense", "debit": Decimal("8000.00"), "check_number": "CHK-0004"},
                {"date_offset": 23, "description": "Contract payment", "debit": Decimal("75000.00"), "check_number": "CHK-0005"},
                {"date_offset": 22, "description": "Income deposit", "credit": Decimal("150000.00"), "check_number": ""},
                {"date_offset": 21, "description": "Office supplies", "debit": Decimal("3500.00"), "check_number": "CHK-0006"},
            ]

            for trans in transactions_data:
                trans_date = base_date - timedelta(days=trans["date_offset"])
                debit = trans.get("debit", Decimal("0.00"))
                credit = trans.get("credit", Decimal("0.00"))

                # Calculate running balance
                running_balance = running_balance + credit - debit

                statement, created = BankStatement.objects.get_or_create(
                    date=trans_date,
                    description=trans["description"],
                    defaults={
                        "check_number": trans["check_number"],
                        "debit": debit,
                        "credit": credit,
                        "balance": running_balance,
                        "status": "Cleared" if trans["date_offset"] > 15 else "On Process",
                    }
                )

                if created:
                    self.stdout.write(
                        f"  Created Bank Statement: {statement.date} - {statement.description} - "
                        f"Balance: {statement.balance}"
                    )
                    statement_count += 1

        self.stdout.write(f"Total Bank Statement records created: {statement_count}")

    def _create_master_fund_monitoring(
        self, divisions, fund_sources, suppliers, nc_list, 
        purchase_types, categories, objects, staff_members
    ):
        """Create sample Master Fund Monitoring records"""
        
        # Sample transaction data
        transactions = [
            {
                "date_offset": 30,
                "supplier_idx": 0,
                "fund_source_idx": 0,
                "nc_idx": 0,
                "particulars": "Office supplies and equipment purchases",
                "payments": Decimal("15000.00"),
                "transaction_type": "Disbursement",
                "dv_number": "DV-001-2024",
                "cheque_number": "CHK-0001",
            },
            {
                "date_offset": 29,
                "supplier_idx": 1,
                "fund_source_idx": 0,
                "nc_idx": 1,
                "particulars": "Maintenance and repair services",
                "payments": Decimal("25000.00"),
                "transaction_type": "Disbursement",
                "dv_number": "DV-002-2024",
                "cheque_number": "CHK-0002",
            },
            {
                "date_offset": 28,
                "supplier_idx": 2,
                "fund_source_idx": 1,
                "nc_idx": 2,
                "particulars": "Consumable supplies for operations",
                "payments": Decimal("10000.00"),
                "transaction_type": "Disbursement",
                "dv_number": "DV-003-2024",
                "cheque_number": "CHK-0003",
            },
            {
                "date_offset": 27,
                "supplier_idx": 3,
                "fund_source_idx": 1,
                "nc_idx": 3,
                "particulars": "Professional consulting services",
                "payments": Decimal("50000.00"),
                "transaction_type": "Disbursement",
                "dv_number": "DV-004-2024",
                "cheque_number": "CHK-0004",
            },
            {
                "date_offset": 26,
                "supplier_idx": 4,
                "fund_source_idx": 2,
                "nc_idx": 4,
                "particulars": "Equipment acquisition and installation",
                "payments": Decimal("100000.00"),
                "transaction_type": "Disbursement",
                "dv_number": "DV-005-2024",
                "cheque_number": "CHK-0005",
            },
            {
                "date_offset": 25,
                "supplier_idx": 0,
                "fund_source_idx": 0,
                "nc_idx": 5,
                "particulars": "Supplies for community center",
                "payments": Decimal("20000.00"),
                "transaction_type": "Downloads",
                "dv_number": "DV-006-2024",
                "cheque_number": "CHK-0006",
            },
            {
                "date_offset": 24,
                "supplier_idx": 1,
                "fund_source_idx": 3,
                "nc_idx": 0,
                "particulars": "Repair and enhancement project",
                "payments": Decimal("75000.00"),
                "transaction_type": "Disbursement",
                "dv_number": "DV-007-2024",
                "cheque_number": "CHK-0007",
            },
            {
                "date_offset": 23,
                "supplier_idx": 2,
                "fund_source_idx": 0,
                "nc_idx": 1,
                "particulars": "Training materials and resources",
                "payments": Decimal("30000.00"),
                "transaction_type": "Disbursement",
                "dv_number": "DV-008-2024",
                "cheque_number": "CHK-0008",
            },
        ]
        
        count = 0
        base_date = timezone.now().date()
        
        for trans in transactions:
            trans_date = base_date - timedelta(days=trans["date_offset"])
            
            # Create monitoring record with unique identifier to avoid duplicates
            unique_key = f"{suppliers[trans['supplier_idx']].id}_{trans_date}_{trans['dv_number']}"
            
            monitoring, created = MasterFundMonitoring.objects.get_or_create(
                payee=suppliers[trans["supplier_idx"]],
                date=trans_date,
                dv_number=trans["dv_number"],
                defaults={
                    "division": divisions[random.randint(0, len(divisions) - 1)],
                    "fund_source": fund_sources[trans["fund_source_idx"]],
                    "nc": nc_list[trans["nc_idx"]],
                    "particulars": trans["particulars"],
                    "transaction_type": trans["transaction_type"],
                    "payments": trans["payments"],
                    "cheque_number": trans.get("cheque_number", ""),
                    "tin": random.choice(suppliers).tin,
                    "purchase_type": purchase_types[random.randint(0, len(purchase_types) - 1)],
                    "account_title": objects[random.randint(0, len(objects) - 1)],
                    "expense_classification": categories[random.randint(0, len(categories) - 1)],
                    "staff": staff_members[random.randint(0, len(staff_members) - 1)],
                    "cheque_status": "Pending",
                }
            )
            
            if created:
                self.stdout.write(
                    f"  Created Master Fund Monitoring: {monitoring.payee.supplier} - {monitoring.date}"
                )
                count += 1
        
        self.stdout.write(f"Total Master Fund Monitoring records created: {count}")
