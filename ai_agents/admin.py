from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from .models import AIAgent

@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'version')
    readonly_fields = ('token', 'created_at', 'updated_at', 'display_job_ids')

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('token',)
        return self.readonly_fields
    
    def display_job_ids(self, obj):
        return mark_safe('<br>'.join(obj.job_ids))
    display_job_ids.short_description = 'Job IDs'

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'version', 'is_active', 'token', 'application_id', 'bot_token')
        }),
        ('Jobs', {
            'fields': ('display_job_ids',),
        }),
    )

    # def view_jobs(self, obj):
    #     return format_html('<a href="{}">View Jobs</a>', f'/admin/view_jobs/{obj.id}/')

    # view_jobs.short_description = 'Jobs'

    # def get_urls(self):
    #     from django.urls import path
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('view_jobs/<int:agent_id>/', self.admin_site.admin_view(self.view_jobs_view), name='view-agent-jobs'),
    #     ]
    #     return custom_urls + urls

    # def view_jobs_view(self, request, agent_id):
    #     from django.shortcuts import render
    #     agent = AIAgent.objects.get(id=agent_id)
    #     jobs = agent.get_jobs()
    #     context = {
    #         'agent': agent,
    #         'jobs': jobs,
    #     }
    #     return render(request, 'admin/ai_agents/view_jobs.html', context)