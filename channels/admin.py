from django.contrib import admin
from .models import Channel, Message

admin.site.register(Channel)

class MessageAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

admin.site.register(Message, MessageAdmin)