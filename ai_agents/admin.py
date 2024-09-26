from django.contrib import admin
from .models import AIAgent

@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'token', 'version', 'is_active', 'created_at')
    readonly_fields = ('token', 'created_at', 'updated_at')
    fields = ('name', 'description', 'application_id', 'bot_token', 'version', 'is_active', 'token', 'created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('token',)
        return self.readonly_fields