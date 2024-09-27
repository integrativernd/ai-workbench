from django.contrib import admin
from tools.models import IntegrationCredential
from django.utils.html import format_html

@admin.register(IntegrationCredential)
class IntegrationCredentialAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'created_at', 'updated_at', 'view_credentials')
    list_filter = ('provider', 'created_at', 'updated_at')
    search_fields = ('user__username', 'provider')
    readonly_fields = ('created_at', 'updated_at', 'decrypted_credentials')

    def view_credentials(self, obj):
        return format_html('<a href="{}">View Credentials</a>', f'/admin/tools/integrationcredential/{obj.id}/change/')
    
    view_credentials.short_description = 'View'

    def decrypted_credentials(self, obj):
        return obj.get_credentials()
    decrypted_credentials.short_description = 'Decrypted Credentials'

    def has_add_permission(self, request):
        return False  # Prevent adding credentials through admin

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deleting credentials through admin
