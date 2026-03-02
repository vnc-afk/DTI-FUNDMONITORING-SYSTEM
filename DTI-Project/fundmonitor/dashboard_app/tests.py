from django.test import TestCase
from dashboard_app.forms import MasterFundMonitoringForm, SupplierForm
from dashboard_app.models import Supplier, FundSource, Division, BreakdownCategory, NegosyoCenter


class MasterFundMonitoringFormTests(TestCase):
    def setUp(self):
        # create minimal related objects to satisfy form foreign keys
        # use the correct field names for models
        self.supplier = Supplier.objects.create(supplier='Test Supplier', tin='000-000-000-000', vat_status='NA', address='123 Street',
                                                propprietor='Owner', contact_number='09171234567')
        self.fund_source = FundSource.objects.create(name='Test Fund', annual_budget=1000)
        self.division = Division.objects.create(name='Test Division')
        self.mooe_cat = BreakdownCategory.objects.create(name='Test', code='MO001', is_active=True)
        # need a district for the NC
        from dashboard_app.models.funding import District
        self.district = District.objects.create(name='Test District', order=1)
        self.nc = NegosyoCenter.objects.create(name='Test NC', code='test_nc', district=self.district)

    def test_optional_fields_not_required(self):
        """Division, fund_source, mooe, and nc may be omitted."""
        data = {
            'date': '2023-01-01',
            'payee': self.supplier.pk,
            'particulars': 'Some details',
            'payments': '100.00',  # payments now required
        }
        form = MasterFundMonitoringForm(data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        # ensure cleaned_data contains None/empty for omitted optional fields
        self.assertIsNone(form.cleaned_data.get('division'))
        self.assertIsNone(form.cleaned_data.get('fund_source'))
        self.assertIsNone(form.cleaned_data.get('mooe'))
        self.assertIsNone(form.cleaned_data.get('nc'))

    def test_particulars_and_payments_required(self):
        """Form should reject submissions missing particulars or payments."""
        data = {
            'date': '2023-01-01',
            'payee': self.supplier.pk,
            'particulars': '',
            'payments': ''
        }
        form = MasterFundMonitoringForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('particulars', form.errors)
        self.assertIn('payments', form.errors)


class SupplierFormTests(TestCase):
    def setUp(self):
        # minimal supplier for tests
        self.supplier_data = {
            'supplier': 'Sample Supplier',
            'tin': '',
            'vat_status': '',
            'philgeps_registration': '',
            'address': '',
            'propprietor': '',
            'contact_number': ''
        }

    def test_optional_fields_not_required(self):
        """Allowed to submit supplier form without optional fields."""
        form = SupplierForm(self.supplier_data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        cleaned = form.cleaned_data
        self.assertEqual(cleaned.get('tin'), '')
        self.assertEqual(cleaned.get('vat_status'), '')
        self.assertEqual(cleaned.get('address'), '')
        self.assertEqual(cleaned.get('propprietor'), '')
        self.assertEqual(cleaned.get('contact_number'), '')

    def test_all_fields_accept_values(self):
        """Form should also validate when optional fields are populated."""
        data = self.supplier_data.copy()
        data.update({
            'tin': '123-456-789-012',
            'vat_status': 'V',
            'address': '123 Main St',
            'propprietor': 'Owner Name',
            'contact_number': '09171234567'
        })
        form = SupplierForm(data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data['tin'], data['tin'])
        self.assertEqual(form.cleaned_data['vat_status'], data['vat_status'])

