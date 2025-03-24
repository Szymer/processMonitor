from django.contrib import admin

from .models import Process, Snapshot


class ProcessAdmin(admin.ModelAdmin):
    list_display = ("name", "PID", "status")
    search_fields = ("name",)


admin.site.register(Process, ProcessAdmin)


class SnapshotAdmin(admin.ModelAdmin):
    list_display = ("author", "timestamp")
    search_fields = ("author",)


admin.site.register(Snapshot, SnapshotAdmin)
