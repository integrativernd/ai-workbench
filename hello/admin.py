from django.contrib import admin
from .models import Greeting

# Register your models here.


class GreetingAdmin(admin.ModelAdmin):
    pass

admin.site.register(Greeting, GreetingAdmin)