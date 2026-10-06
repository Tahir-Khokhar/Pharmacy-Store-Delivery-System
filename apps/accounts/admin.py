from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Address

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Info'

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    inlines = (ProfileInline, AddressInline)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Pharmacy Role & Details', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Pharmacy Role & Details', {'fields': ('role', 'phone', 'email')}),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'user__email')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'full_name', 'phone', 'city', 'is_default')
    list_filter = ('city', 'is_default')
    search_fields = ('user__username', 'full_name', 'address_line', 'city')
