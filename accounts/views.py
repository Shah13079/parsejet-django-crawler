"""Views for user authentication, registration, and password management."""
from django.shortcuts import redirect, render
from accounts.forms import Registration, ProfileUpdate
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Account
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .task import sending_activation_mail


def register(request):
    """Handle new user registration and send an activation email."""
    if request.user.is_authenticated:
        return redirect(reverse_lazy('Amazon_crawler:best-selling'))

    if request.method == 'POST':
        form = Registration(request.POST)
        context = {'form': form}
        if form.is_valid():
            current_site = get_current_site(request)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            word = form.cleaned_data['password']
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=word.strip(),
            )
            user.save()
            user_id = user.id

            # Dispatch activation email via Celery
            sending_activation_mail.delay(
                'account_verification_email',
                str(current_site),
                user_id,
                email,
                'ParseJet Account Verification!',
            )

            return redirect('/accounts/login/?command=verification&email=' + email)
    else:
        form = Registration()
        context = {'form': form}
    return render(request, 'accounts/register.html', context)


def activate(request, uidb64, token):
    """Activate a user account via a token link from the verification email."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! You are ready to go!')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')


def view_login(request):
    """Authenticate and log in a user with email and password."""
    if request.user.is_authenticated:
        return redirect(reverse_lazy('Amazon_crawler:best-selling'))

    elif request.method == 'POST':
        mail = request.POST.get('email')
        word = request.POST.get('password')
        user = authenticate(request, email=mail, password=word)

        if user is not None:
            login(request, user)
            return redirect(reverse_lazy('Amazon_crawler:best-selling'))
        else:
            messages.error(request, 'Invalid login details!')
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')


@login_required
def logouting(request):
    """Log the current user out and redirect to the login page."""
    logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('accounts:login')


def forgot_password(request):
    """Send a password-reset email if the given email address exists."""
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            current_site = get_current_site(request)
            user_id = user.id
            mail_subject = 'ParseJet Reset Your Password'

            # Dispatch password-reset email via Celery
            sending_activation_mail.delay(
                'reset_pass_email', str(current_site), user_id, email, mail_subject
            )

            messages.success(
                request, 'Password reset email has been sent to your email address!'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Account does not exist with this email!')
    return render(request, 'accounts/forgotpassword.html')


def resetpassword_validate(request, uidb64, token):
    """Validate the password-reset token and store the user ID in the session."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('resetpassword')
    else:
        messages.error(request, 'Invalid reset link!')
        return redirect('register')


def resetpassword(request):
    """Set a new password for the user identified by the session UID."""
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('login')

        else:
            messages.error(request, 'The passwords did not match!')
            return redirect('resetpassword')
    else:
        return render(request, 'accounts/resetpassword.html')


def ok(request):
    """Simple health-check endpoint."""
    return HttpResponse(request, 'ok')
