from django.core.checks import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model, authenticate, login, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from .models import EmailConfirmed
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
import uuid
User = get_user_model()


def register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_active = False
            instance.save()
               # Send Email
            user = EmailConfirmed.objects.get(user=instance)
            site = get_current_site(request)
            email = instance.email
            first_name = instance.first_name
            last_name = instance.last_name
            #date_created = instance.date_created
            email_body = render_to_string(
                'accounts/verify_email.html',
                {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'activation_key': user.activation_key,
                    'domain': site.domain,

                })

            send_mail(
                subject='Email Confirmation',
                message=email_body,
                from_email='testmaildjango82@gmail.com',
                recipient_list=[email],
                fail_silently=True,
            )
            return render(request, 'accounts/registration_start.html')
        return render(request, 'accounts/register.html', {'form': form})
    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    _next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user_obj = form.cleaned_data.get('user_obj')
            auth_login(request, user_obj)
            if _next:
                return redirect(_next)
            return redirect('pages:index')
        return render(request, 'accounts/login.html', {'form': form})
    return render(request, 'accounts/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect("accounts:login")


def email_confirm(request, activation_key):
    user = get_object_or_404(EmailConfirmed, activation_key=activation_key)
    if user is not None:
        user.email_confirmed = True
        user.save()
        instance = User.objects.get(email=user)
        instance.is_active = True
        instance.save()
        return render(request, 'accounts/registration_complete.html')


