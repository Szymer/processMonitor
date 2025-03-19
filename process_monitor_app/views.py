import uuid
import django_tables2 as tables
import django_filters
from django_filters.views import FilterView

from django_tables2 import SingleTableMixin
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


from process_monitor_app.models import Process, StoppedProcess, StoredProcess,Snapshot






class HomeView(View):
    def get(self, request):
        return render(request, "index.html")
    
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")
    
class ProcessFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')  # Filtrowanie po nazwie procesu
    class Meta:
        model = Process
        fields = ['PID','name', 'status']


class StopProcessView(View):
    
    def post(self, request, process_id, pid):
        rr =1
        try:
            process = Process.objects.get(PID=pid)
            iid_str = f"{process_id}--{process.PID}--{process.name}--{process.start_time}"
            iid = uuid.uuid5(uuid.NAMESPACE_DNS, iid_str)
            stored_process = StoredProcess(
                iid = iid,   
                PID = process.PID,
                name = process.name,
                status = process.status,
                start_time = process.start_time,
                duration = process.duration,
                memory_usage_MB = process.memory_usage_MB,
                CPU_Usage_Percent = process.CPU_Usage_Percent
            )
            stored_process.save()
            StoppedProcess(
                process=stored_process,
                author=request.user.username
            ).save()
            process.delete()
            return redirect('process_list')
        except Process.DoesNotExist:
            return redirect('process_list')


class SnapshotView(View):
    
    def post(self, request):
        snapshot = Snapshot(author=request.user.username)
        snapshot.save()
        for process in Process.objects.all():
            iid_str = f"{process.id}--{process.PID}--{process.name}--{process.start_time}"
            iid = uuid.uuid5(uuid.NAMESPACE_DNS, iid_str)
            stored_process = StoredProcess(
                iid = iid,
                PID = process.PID,
                name = process.name,
                status = process.status,
                start_time = process.start_time,
                duration = process.duration,
                memory_usage_MB = process.memory_usage_MB,
                CPU_Usage_Percent = process.CPU_Usage_Percent
            )
            stored_process.save()
            snapshot.processes.add(stored_process)
        snapshot.save()
        return redirect('process_list')



class ProcessTable(tables.Table):
    
    stop = tables.Column(empty_values=(), orderable=False, verbose_name="Action")
    id = tables.Column(orderable=True)
    PID = tables.Column(orderable=True)
    name = tables.Column(orderable=True)
    status = tables.Column(orderable=True)
    start_time = tables.Column(orderable=True)
    duration = tables.Column(orderable=True)
    memory_usage_MB = tables.Column(orderable=True, verbose_name="Memory (MB)")
    CPU_Usage_Percent = tables.Column(orderable=True, verbose_name="CPU (%)")
    

    def render_stop(self, record):
        stop_url = reverse("stop_process", args=[ record.id, record.PID])
        return format_html(
          '<button hx-post="{}" '
            'hx-trigger="click" '
            'hx-confirm="Are you sure you want to stop this process?" '
            'hx-target="closest tr" '
            'hx-swap="outerHTML" '
            'class="stop-btn">Stop</button>',
            stop_url
             )
    class Meta:
        model = Process
        template_name = "django_tables2/bootstrap5.html" # Szablon Bootstrapa
        fields = ("id","PID", "name", "status", "start_time", "duration", "memory_usage_MB", "CPU_Usage_Percent")
        attrs = {"class": "table table-striped"}  # Bootstrap dla lepszego wyglądu




class ProcessListView(SingleTableMixin, FilterView):
    model = Process
    table_class = ProcessTable
    template_name = 'htmxprocess.html'
    filterset_class = ProcessFilter
    paginate_by = 15
    ordering = ['id']  


        
    def render_to_response(self, context, **response_kwargs):
        """Jeśli żądanie pochodzi od HTMX, renderuj tylko tabelę."""
        if self.request.user.is_authenticated == False:
            if self.request.htmx: 
                return render(self.request, "processes_table.html", context)
            return super().render_to_response(context, **response_kwargs)
        else:   
            return redirect('login')
