from django.contrib import admin

from .models import Process

class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'PID', 'status')
    search_fields = ('name',)

admin.site.register(Process, ProcessAdmin)