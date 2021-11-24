from accounts.views import email_confirm
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import UserCreationForm, UserChangeForm
from .models import EmailConfirmed
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

User = get_user_model()

admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    readonly_fields = ('date_joined',)
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_admin', 'is_staff', 'is_superuser',
                    )
    list_filter = ('is_admin', 'is_staff',)
    field_sets = (
        (
            None, {'fields': ('email', 'first_name', 'last_name', 'password')}
         ),
        (
            'Permissions', {'fields': ('is_admin', 'is_staff', 'is_superuser')}
        )
    )
    add_fieldsets = (
        (
            None, {
                'fields': ('email', 'first_name', 'last_name', 'is_active', 'password1', 'password2')
            }
        ),
        ('Permissions', {'fields': ('is_admin', 'is_superuser')})
    )
    ordering = ('email',)
    search_fields = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)


class EmailConfirmedAdmin (admin.ModelAdmin) :
    list_display = ('user', 'first_name', 'last_name', 'date_created', 'email_confirmed', 'date_confirmed')
    list_filter = ('email_confirmed','date_created',  'date_confirmed', )


    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name


admin.site.register(EmailConfirmed, EmailConfirmedAdmin)


