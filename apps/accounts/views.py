from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.common.utils import log_audit_action
from .forms import CustomerRegistrationForm, CustomerLoginForm, UserProfileUpdateForm, ProfileDetailsForm, AddressForm
from .models import UserRole, Address, User

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:router')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = UserRole.CUSTOMER
            user.save()
            log_audit_action(user, 'CREATE', 'User', user.id, f"Customer registered: {user.username}", request)
            login(request, user)
            messages.success(request, f"Welcome to PharmaCare, {user.first_name or user.username}! Your account has been created.")
            return redirect('dashboard:customer')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:router')
    
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Allow login via username or email
            user = authenticate(request, username=username_or_email, password=password)
            if not user and '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                log_audit_action(user, 'LOGIN', 'User', user.id, f"User logged in: {user.username}", request)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:router')
            else:
                messages.error(request, "Invalid username/email or password.")
        else:
            messages.error(request, "Invalid credentials. Please verify your details.")
    else:
        form = CustomerLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        log_audit_action(request.user, 'LOGIN', 'User', request.user.id, "User logged out", request)
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('products:home')


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=user)
        profile_form = ProfileDetailsForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            log_audit_action(user, 'UPDATE', 'Profile', profile.id, "Updated user profile details", request)
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
    else:
        user_form = UserProfileUpdateForm(instance=user)
        profile_form = ProfileDetailsForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })


@login_required
def addresses_view(request):
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if not addresses.exists():
                address.is_default = True
            address.save()
            messages.success(request, "New address added successfully.")
            return redirect('accounts:addresses')
            
    return render(request, 'accounts/addresses.html', {
        'addresses': addresses,
        'form': form
    })


@login_required
def address_edit_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('accounts:addresses')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_edit.html', {'form': form, 'address': address})


@login_required
def address_delete_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address removed successfully.")
    return redirect('accounts:addresses')


@login_required
def address_set_default_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, f"'{address.title}' is now your default delivery address.")
    return redirect('accounts:addresses')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
