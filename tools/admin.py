# admin.py
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import IntegrationCredential

class IntegrationCredentialForm(forms.ModelForm):
    class Meta:
        model = IntegrationCredential
        fields = ['user', 'provider', 'credentials']
        widgets = {
            'user': forms.Select(attrs={'disabled': 'disabled'}),
            'provider': forms.TextInput(attrs={'readonly': 'readonly'}),
            'credentials': forms.Textarea(attrs={'readonly': 'readonly'}),
        }

@admin.register(IntegrationCredential)
class IntegrationCredentialAdmin(admin.ModelAdmin):
    form = IntegrationCredentialForm
    list_display = ('user', 'provider', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'encrypted_credentials')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {'fields': ['user', 'provider']}),
            ('Encrypted Credentials', {'fields': ['encrypted_credentials']}),
            ('Timestamps', {'fields': ['created_at', 'updated_at']}),
        ]
        return fieldsets

    def encrypted_credentials(self, obj):
        return obj.credentials
    encrypted_credentials.short_description = 'Encrypted Credentials'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True  # Allow viewing the change form, but all fields will be read-only

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def save_model(self, request, obj, form, change):
        # Prevent saving changes
        pass

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_continue'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)
