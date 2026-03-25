from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError

from dashboard_app.utils.validators import (
	validate_alphanumeric_with_spaces,
	validate_budget_amount,
	validate_hex_color,
	validate_letters_only,
	validate_mooe_format,
	validate_no_script_content,
	validate_phone_number,
	validate_string_length,
	validate_tin_format,
	validate_tin_numeric,
	validate_transaction_amount,
	sanitize_string_input,
)


class Division(models.Model):
	name = models.CharField(
		max_length=100,
		unique=True,
		validators=[validate_string_length(min_length=2, max_length=100), validate_letters_only],
		help_text="Division name (letters and spaces only)",
	)
	description = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = "Division"
		verbose_name_plural = "Divisions"

	def __str__(self):
		return self.name

	def clean(self):
		self.name = sanitize_string_input(self.name)
		validate_no_script_content(self.name)
		if self.id:
			duplicate = Division.objects.filter(name__iexact=self.name).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'name': 'A division with this name already exists.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class Staff(models.Model):
	first_name = models.CharField(
		max_length=100,
		validators=[validate_string_length(min_length=2, max_length=100), validate_letters_only],
	)
	middle_initial = models.CharField(max_length=5, blank=True, validators=[validate_letters_only])
	last_name = models.CharField(
		max_length=100,
		validators=[validate_string_length(min_length=2, max_length=100), validate_letters_only],
	)
	division = models.ForeignKey(
		Division,
		on_delete=models.PROTECT,
		related_name='staff_members',
		null=True,
		blank=True,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['last_name', 'first_name']
		verbose_name = "Staff"
		verbose_name_plural = "Staff Members"

	def __str__(self):
		middle = f" {self.middle_initial}" if self.middle_initial else ""
		return f"{self.first_name}{middle} {self.last_name}"

	def clean(self):
		self.first_name = sanitize_string_input(self.first_name)
		self.middle_initial = sanitize_string_input(self.middle_initial)
		self.last_name = sanitize_string_input(self.last_name)
		validate_no_script_content(self.first_name)
		validate_no_script_content(self.last_name)
		if self.middle_initial:
			validate_no_script_content(self.middle_initial)

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class Supplier(models.Model):
	CATEGORY_CHOICES = [('NV', 'Non-VAT Registered'), ('V', 'VAT Registered'), ('—', 'N/A')]

	supplier = models.CharField(
		max_length=200,
		unique=True,
		validators=[validate_string_length(min_length=2, max_length=200)],
	)
	tin = models.CharField(max_length=50, validators=[validate_tin_format, validate_tin_numeric], blank=True, null=True)
	vat_status = models.CharField(max_length=2, choices=CATEGORY_CHOICES, blank=True, null=True)
	philgeps_registration = models.CharField(max_length=100, blank=True, validators=[validate_alphanumeric_with_spaces])
	address = models.TextField(blank=True, null=True, validators=[validate_string_length(min_length=5, max_length=500)])
	propprietor = models.CharField(max_length=200, blank=True, null=True, validators=[validate_string_length(min_length=2, max_length=200)])
	contact_number = models.CharField(max_length=30, blank=True, null=True, validators=[validate_phone_number])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['supplier']
		verbose_name = "Supplier"
		verbose_name_plural = "Suppliers"

	def __str__(self):
		return self.supplier

	def clean(self):
		self.supplier = sanitize_string_input(self.supplier)
		self.address = sanitize_string_input(self.address)
		self.propprietor = sanitize_string_input(self.propprietor)
		self.philgeps_registration = sanitize_string_input(self.philgeps_registration)
		self.contact_number = sanitize_string_input(self.contact_number) if self.contact_number else ''
		validate_no_script_content(self.supplier)
		validate_no_script_content(self.address)
		validate_no_script_content(self.propprietor)
		if self.id:
			duplicate = Supplier.objects.filter(supplier__iexact=self.supplier).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'supplier': 'A supplier with this name already exists.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class FundSource(models.Model):
	name = models.CharField(max_length=100, unique=True, validators=[validate_string_length(min_length=2, max_length=100)])
	annual_budget = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_budget_amount])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = "Fund Source"
		verbose_name_plural = "Fund Sources"

	def __str__(self):
		return self.name

	def clean(self):
		self.name = sanitize_string_input(self.name)
		validate_no_script_content(self.name)
		if self.id:
			duplicate = FundSource.objects.filter(name__iexact=self.name).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'name': 'A fund source with this name already exists.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class BreakdownCategory(models.Model):
	code = models.CharField(max_length=10, unique=True)
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True, null=True)
	order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['order', 'code']
		verbose_name = "Breakdown Category"
		verbose_name_plural = "Breakdown Categories"

	def __str__(self):
		return f"{self.code} - {self.name}"


class FundSourceBreakdown(models.Model):
	fund_source = models.ForeignKey(FundSource, on_delete=models.CASCADE, related_name='breakdowns')
	category = models.ForeignKey('BreakdownCategory', on_delete=models.CASCADE, related_name='fund_breakdowns', blank=True, null=True)
	budget_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_transaction_amount])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['fund_source', 'category__order', 'category__code']
		verbose_name = "Fund Source Breakdown"
		verbose_name_plural = "Fund Source Breakdowns"
		unique_together = ('fund_source', 'category')

	def __str__(self):
		return f"{self.fund_source.name} - {self.category.code}"

	def clean(self):
		if not self.fund_source_id or not self.budget_amount:
			return
		total_breakdown = FundSourceBreakdown.objects.filter(fund_source_id=self.fund_source_id).exclude(id=self.id).aggregate(total=Sum('budget_amount'))['total'] or 0
		if total_breakdown + self.budget_amount > self.fund_source.annual_budget:
			raise ValidationError({'budget_amount': f'Total breakdown ({total_breakdown + self.budget_amount}) cannot exceed annual budget ({self.fund_source.annual_budget}).'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class ExpenseObject(models.Model):
	code = models.CharField(max_length=50, unique=True, validators=[validate_string_length(min_length=5, max_length=50)])
	name = models.CharField(max_length=255, validators=[validate_string_length(min_length=3, max_length=255)])
	color = models.CharField(max_length=7, default='#3498db', validators=[validate_hex_color])
	description = models.TextField(blank=True, null=True, validators=[validate_string_length(max_length=500)])
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['code']
		verbose_name = "Expense Object"
		verbose_name_plural = "Expense Objects"

	def __str__(self):
		return f"({self.code}) {self.name}"

	def clean(self):
		self.name = sanitize_string_input(self.name)
		if self.description:
			self.description = sanitize_string_input(self.description)
		validate_no_script_content(self.name)
		if self.description:
			validate_no_script_content(self.description)
		if self.id:
			duplicate = ExpenseObject.objects.filter(code=self.code).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'code': 'This expense code is already in use.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class ExpenseCategory(models.Model):
	name = models.CharField(max_length=255, unique=True, validators=[validate_string_length(min_length=2, max_length=255)])
	color = models.CharField(max_length=7, default='#95a5a6', validators=[validate_hex_color])
	description = models.TextField(blank=True, null=True, validators=[validate_string_length(max_length=500)])
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = "Expense Category"
		verbose_name_plural = "Expense Categories"

	def __str__(self):
		return self.name

	def clean(self):
		self.name = sanitize_string_input(self.name)
		if self.description:
			self.description = sanitize_string_input(self.description)
		validate_no_script_content(self.name)
		if self.description:
			validate_no_script_content(self.description)
		if self.id:
			duplicate = ExpenseCategory.objects.filter(name__iexact=self.name).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'name': 'A category with this name already exists.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class District(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True, null=True)
	order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['order', 'name']
		verbose_name = "District"
		verbose_name_plural = "Districts"

	def __str__(self):
		return self.name

	def clean(self):
		self.name = sanitize_string_input(self.name)
		validate_no_script_content(self.name)
		if not self.name or len(self.name.strip()) < 2:
			raise ValidationError({'name': 'District name must be at least 2 characters.'})
		if self.id:
			duplicate = District.objects.filter(name__iexact=self.name).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'name': 'A district with this name already exists.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class NegosyoCenter(models.Model):
	district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='negosyo_centers')
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['district__order', 'district__name', 'name']
		verbose_name = "Negosyo Center"
		verbose_name_plural = "Negosyo Centers"
		unique_together = ('district', 'code')

	def __str__(self):
		return f"{self.name} ({self.district.name})"

	def clean(self):
		self.name = sanitize_string_input(self.name)
		self.code = self.code.lower().strip()
		validate_no_script_content(self.name)
		if not self.name or len(self.name.strip()) < 2:
			raise ValidationError({'name': 'NC name must be at least 2 characters.'})
		if not self.code or len(self.code.strip()) < 2:
			raise ValidationError({'code': 'NC code must be at least 2 characters.'})
		if self.id:
			duplicate = NegosyoCenter.objects.filter(code__iexact=self.code).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'code': 'A NC with this code already exists.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class PurchaseType(models.Model):
	name = models.CharField(max_length=100, unique=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = "Purchase Type"
		verbose_name_plural = "Purchase Types"

	def __str__(self):
		return self.name

	def clean(self):
		self.name = sanitize_string_input(self.name)
		validate_no_script_content(self.name)
		if not self.name or len(self.name.strip()) < 2:
			raise ValidationError({'name': 'Name must be at least 2 characters.'})
		if len(self.name) > 100:
			raise ValidationError({'name': 'Name cannot exceed 100 characters.'})
		if self.id:
			duplicate = PurchaseType.objects.filter(name__iexact=self.name).exclude(id=self.id).exists()
			if duplicate:
				raise ValidationError({'name': 'A purchase type with this name already exists.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class TaxTable(models.Model):
	purchase_type = models.ForeignKey(PurchaseType, on_delete=models.CASCADE, related_name='tax_entries', null=True, blank=False)
	vat_goods_5 = models.CharField(max_length=50, blank=True)
	vat_services_5 = models.CharField(max_length=50, blank=True)
	vat_goods_services_3 = models.CharField(max_length=50, blank=True)
	vat_goods_1 = models.CharField(max_length=50, blank=True)
	vat_services_2 = models.CharField(max_length=50, blank=True)
	vat_rental_5 = models.CharField(max_length=50, blank=True)
	vat_prof_fee_10 = models.CharField(max_length=50, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['purchase_type__name']
		verbose_name = "Tax Table Entry"
		verbose_name_plural = "Tax Table Entries"
		unique_together = ('purchase_type',)

	def __str__(self):
		return self.purchase_type.name

	def clean(self):
		if not self.purchase_type:
			raise ValidationError({'purchase_type': 'Purchase type is required.'})
		validate_no_script_content(self.vat_goods_5 or '')
		validate_no_script_content(self.vat_services_5 or '')
		validate_no_script_content(self.vat_goods_services_3 or '')
		validate_no_script_content(self.vat_goods_1 or '')
		validate_no_script_content(self.vat_services_2 or '')
		validate_no_script_content(self.vat_rental_5 or '')
		validate_no_script_content(self.vat_prof_fee_10 or '')

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)
