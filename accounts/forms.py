from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))

        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_admin')

        def clean_password(self):
            return self.initial['password']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'email',
                'placeholder': 'Email Address'

            }
        )
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'First Name'

            }
        )
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'

            }
        )
    )
    password1 = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'Password',
                'placeholder': 'Create password'

            }
        )
    )
    password2 = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'Password',
                'placeholder': 'Repeat Password'

            }
        )
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        ]

    def clean_email(self):
        error_messages = {
            'duplicate_email': 'Email is already taken.'
        }
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email=email)
            raise forms.ValidationError(
                error_messages['duplicate_email'],
                code='duplicate_email',
            )
        except User.DoesNotExist:
            return email


class UserLoginForm(forms.Form):
    email = forms.CharField(
        label='email',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "type": 'email',
                "placeholder": "Email address",
                "required": True

            }
        )
    )
    password = forms.CharField(
        label='email',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "type": "password",
                "placeholder": "Password",
                "Required": True
            }
        )
    )

    def clean(self, *args, **kwargs):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user_qs_final = User.objects.filter(Q(email__iexact=email)).distinct()
        if not user_qs_final.exists() and user_qs_final.count != 1:
            raise forms.ValidationError("User does not exist")
        user_obj = user_qs_final.first()
        if not user_obj.check_password(password):
            raise forms.ValidationError("Credentials are not correct")
        self.cleaned_data["user_obj"] = user_obj
        return super(UserLoginForm, self).clean(*args, **kwargs)
    
    
class UserPasswordResetForm(SetPasswordForm):
    """Change password form."""
    new_password1 = forms.CharField(label='Password',
        help_text="<ul class='errorlist text-muted'><li>Your password can 't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can 't be a commonly used password.</li> <li>Your password can 't be entirely numeric.<li></ul>",
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'password',
            'type': 'password',
            'id': 'user_password',
        }))

    new_password2 = forms.CharField(label='Confirm password',
        help_text=False,
        max_length=100,
        required=True,
        widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'confirm password',
            'type': 'password',
            'id': 'user_password',
        }))


class UserForgotPasswordForm(PasswordResetForm):
    """User forgot password, check via email form."""
    email = forms.EmailField(label='Email address',
        max_length=254,
        required=True,
        widget=forms.TextInput(
         attrs={'class': 'form-control',
                'placeholder': 'email address',
                'type': 'text',
                'id': 'email_address'
                }
        ))
