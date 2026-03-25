from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class UserAccountForm(forms.ModelForm):
    """Form for creating and editing user accounts"""

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to use temporary password',
            'required': False
        }),
        required=False,
        help_text='Leave blank to use temporary password (TempPass123!) - user will change on first login'
    )

    is_staff = forms.BooleanField(
        label='Staff Status',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        help_text='Allows access to admin interface'
    )

    is_superuser = forms.BooleanField(
        label='Superuser Status',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        help_text='Full administrator permissions'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username (no spaces)',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'user@example.com',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        if self.is_edit:
            self.fields['password'].help_text = 'Leave blank to keep current password'

        if self.instance.pk:
            self.fields['is_staff'].initial = self.instance.is_staff
            self.fields['is_superuser'].initial = self.instance.is_superuser

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()

        if not username:
            raise ValidationError('Username is required.', code='required')

        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.', code='min_length')

        if len(username) > 150:
            raise ValidationError('Username must not exceed 150 characters.', code='max_length')

        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            raise ValidationError(
                'Username can only contain letters, numbers, dots, underscores, and hyphens.',
                code='invalid_chars'
            )

        existing = User.objects.filter(username=username)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError('This username is already taken.', code='duplicate')

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()

        if not email:
            raise ValidationError('Email is required.', code='required')

        existing = User.objects.filter(email=email)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise ValidationError('An account with this email already exists.', code='duplicate')

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password', '').strip()

        if self.is_edit and not password:
            return cleaned_data

        if not self.is_edit and not password:
            return cleaned_data

        if password:
            self._validate_password_strength(password)

        return cleaned_data

    def _validate_password_strength(self, password):
        if len(password) < 8:
            raise ValidationError(
                'Password must be at least 8 characters long.',
                code='password_too_short'
            )

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            raise ValidationError(
                'Password must contain uppercase letters, lowercase letters, and numbers.',
                code='password_weak'
            )

    def save(self, commit=True):
        user = super().save(commit=False)

        if not user.pk:
            user.is_active = True

        password = self.cleaned_data.get('password', '').strip()
        fixed_temporary_password = 'TempPass123!'

        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_password(fixed_temporary_password)

        if commit:
            user.save()
            from user_app.models import UserPreference
            pref, created = UserPreference.objects.get_or_create(user=user)
            if not created:
                pref.password_changed = False
                pref.save()

        if not password and not user.pk:
            user._temporary_password = fixed_temporary_password

        return user


class InitialPasswordChangeForm(forms.Form):
    """Form for users to change their initial/temporary password on first login"""

    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'required': True,
            'autocomplete': 'new-password',
        }),
        help_text='Must contain uppercase, lowercase, numbers. At least 8 characters.'
    )

    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'required': True,
            'autocomplete': 'new-password',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1', '').strip()

        if not password:
            raise ValidationError('Password is required.', code='required')

        if len(password) < 8:
            raise ValidationError(
                'Password must be at least 8 characters long.',
                code='password_too_short'
            )

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            raise ValidationError(
                'Password must contain uppercase letters, lowercase letters, and numbers.',
                code='password_weak'
            )

        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1', '')
        password2 = cleaned_data.get('new_password2', '')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.', code='password_mismatch')

        return cleaned_data

    def save(self):
        password = self.cleaned_data.get('new_password1')
        self.user.set_password(password)
        self.user.save()

        from user_app.models import UserPreference
        try:
            pref = UserPreference.objects.get(user=self.user)
            pref.password_changed = True
            pref.save()
        except UserPreference.DoesNotExist:
            UserPreference.objects.create(user=self.user, password_changed=True)

        return self.user


__all__ = ['UserAccountForm', 'InitialPasswordChangeForm']
