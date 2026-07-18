from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.
    """
    model = User
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (_('Custom Fields'), {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Custom Fields'), {'fields': ('role',)}),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
