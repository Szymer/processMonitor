import uuid
from django.http import HttpResponse
import psutil
import django_tables2 as tables
import django_filters
import xlwt
from  datetime import datetime



from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


from process_monitor_app.models import Process, StoppedProcess, StoredProcess,Snapshot


# Lista procesów, które nie mogą być zatrzymane tak dla przykładu
UNSTOPABLE = ["systemd", "init", "kthreadd", "ksoftirqd", "kworker", "kdevtmpfs", "khungtaskd", "kintegrityd", "kblockd", "kswapd", "ksmd", "khugepaged", "kthrotld", "kmpathd", "kpsmoused"]


class HomeView(View):
    def get(self, request):
        return render(request, "index.html")
    
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('process_list')
        else:
            return redirect('login')
    
class ProcessFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')  # Filtrowanie po nazwie procesu
    class Meta:
        model = Process
        fields = ['PID','name', 'status']

class StopProcessView(View):
    
    def post(self, request, process_id, pid):
       
        try:
            process = Process.objects.get(PID=pid)
            iid_str = f"{process_id}--{process.PID}--{process.name}--{process.start_time}"
            iid = uuid.uuid5(uuid.NAMESPACE_DNS, iid_str)
            
            try:
                real_process = psutil.Process(pid=pid)
                if real_process.name() not in UNSTOPABLE and real_process.pid != 1:
                    real_process.kill()
            except psutil.NoSuchProcess:
                return redirect('process_list')   
            
            stopped_proc = StoppedProcess(timestamp=datetime.now(), author=request.user.username)
            stopped_proc.save()
                 
            stored_process = StoredProcess(
                iid = iid,   
                PID = process.PID,
                name = process.name,
                status = process.status,
                start_time = process.start_time,
                duration = process.duration,
                memory_usage_MB = process.memory_usage_MB,
                CPU_Usage_Percent = process.CPU_Usage_Percent,
                stopped = stopped_proc
            )
            stored_process.save()
            process.delete()
            return redirect('process_list')
        except Exception as e:
            print(e)
            return redirect('process_list')


class SnapshotView(View):
    
    def post(self, request):
        snapshot = Snapshot(author=request.user.username)
        snapshot.save()
        for process in Process.objects.all():
            iid_str = f"{process.id}--{process.PID}--{process.name}--{process.start_time}{datetime.now()}"
            iid = uuid.uuid5(uuid.NAMESPACE_DNS, iid_str)
            try:
                stored_process = StoredProcess(
                    iid = iid,
                    PID = process.PID,
                    name = process.name,
                    status = process.status,
                    start_time = process.start_time,
                    duration = process.duration,
                    memory_usage_MB = process.memory_usage_MB,
                    CPU_Usage_Percent = process.CPU_Usage_Percent,
                    snapshot = snapshot
                )
                stored_process.save()
                # snapshot..add(stored_process)
            except Exception as e:
                print(e)
                continue
 
        return redirect('process_list')


class SnapshotTable(tables.Table):
    id = tables.Column(orderable=True)
    timestamp = tables.Column(orderable=True)
    author = tables.Column(orderable=True)
    details = tables.Column(empty_values=(), orderable=False, verbose_name="details")
    export_to_excel = tables.Column(empty_values=(), orderable=False, verbose_name="Export")

    def render_details(self, record):
        process_detail_url = reverse("snapshot_detail", args=[record.id])  # Ścieżka do widoku szczegółów procesu
        return format_html('<a href="{}" class="process-link"> Detail</a>', process_detail_url, )

    
    def render_export_to_excel(self, record):
        export_url = reverse("export_snapshot", args=[record.id])
        return format_html(
          '<button hx-post="{}" '
            'hx-trigger="click" '
            'hx-target="closest tr" '
            'hx-swap="outerHTML" '
            'class="stop-btn">Export</button>',
            export_url
             )

    class Meta:
        model = Process
        template_name = "django_tables2/bootstrap5.html" # Szablon Bootstrapa
        fields = ("id", "author")
        attrs = {"class": "table table-striped"}  

    
class SnapshotListView(SingleTableMixin, View):
    model = Snapshot
    table_class = SnapshotTable
    template_name = 'snaps.html'
    paginate_by = 42    
    ordering = ['id']
     
    def get(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:
            snapshots = Snapshot.objects.all().order_by(*self.ordering)  #
            table = self.table_class(snapshots)
            context = {"table": table}
            
            if request.htmx:
                return render(request, "snap_table.html", context)  
            
            return render(request, self.template_name, context)  
        else:
            return redirect('login')


class ExportSnapshotView(View):
    
    def post(self, request, snap_id):
        snapshot = Snapshot.objects.get(id=snap_id)
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="snapshot_{snap_id}.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Snapshot')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['ID', 'Timestamp', 'Author', 'Processes']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        for process in snapshot.processes.all():
            row_num += 1
            row = [process.id, process.timestamp, process.author, process.processes]
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        return response

       
class ProcessTable(tables.Table):
    
    stop = tables.Column(empty_values=(), orderable=False, verbose_name="Action")
    PID = tables.Column(orderable=True)
    name = tables.Column(orderable=True)
    status = tables.Column(orderable=True)
    start_time = tables.Column(orderable=True)
    duration = tables.Column(orderable=True)
    memory_usage_MB = tables.Column(orderable=True, verbose_name="Memory (MB)")
    CPU_Usage_Percent = tables.Column(orderable=True, verbose_name="CPU (%)")
    
    def __init__(self, *args, show_stop=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not show_stop:
            del self.base_columns['stop']
    
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
        # model = Process
        template_name = "django_tables2/bootstrap5.html" 
        fields = ("PID", "name", "status", "start_time", "duration", "memory_usage_MB", "CPU_Usage_Percent")
        attrs = {"class": "table table-striped"}  


class ProcessListView(SingleTableMixin, FilterView):
    model = Process
    table_class = ProcessTable
    template_name = 'htmxprocess.html'
    filterset_class = ProcessFilter
    paginate_by = 42
    ordering = ['PID']  


        
    def render_to_response(self, context, **response_kwargs):
        """Jeśli żądanie pochodzi od HTMX, renderuj tylko tabelę."""
        if self.request.user.is_authenticated:
            if self.request.htmx: 
                return render(self.request, "processes_table.html", context)
            return super().render_to_response(context, **response_kwargs)
        else:   
            return redirect('login')


class SnapshotDetailedView(SingleTableMixin, FilterView):
    
    model = StoredProcess
    table_class = ProcessTable
    template_name = 'snap_detail.html'
    filterset_class = ProcessFilter
    paginate_by = 42
    ordering = ['PID']  

    
    def get_queryset(self):
        """Filtrowanie rekordów StoredProcess na podstawie snapshot_id"""
        snapshot_id = self.kwargs.get("snap_id")  # Pobierz ID Snapshota z URL
        return StoredProcess.objects.filter(snapshot_id=snapshot_id)  # Filtrujemy tylko te procesy
    
    
    def get_context_data(self, **kwargs):
        """Dodaj sumę CPU i RAM do kontekstu widoku"""
        context = super().get_context_data(**kwargs)
        snap_proceses = self.get_queryset()
        # Obliczamy sumy CPU i RAM dla wszystkich StoredProcess w danym Snapshocie
        total_cpu = snap_proceses.aggregate(Sum('CPU_Usage_Percent'))['CPU_Usage_Percent__sum'] or 0
        total_ram = snap_proceses.aggregate(Sum('memory_usage_MB'))['memory_usage_MB__sum'] or 0

        # Dodajemy do kontekstu
        context['total_cpu'] = total_cpu
        context['total_ram'] = total_ram
     

        return context

    def render_to_response(self, context, show_stop,  **response_kwargs):

        if self.request.user.is_authenticated:
            if self.request.htmx: 
                return render(self.request, "processes_table.html", context)
            return super().render_to_response(context, **response_kwargs)
        else:   
            return redirect('login')
 
 
 
 
class StopedTable(tables.Table):
    id = tables.Column(orderable=True)
    timestamp = tables.Column(orderable=True)
    author = tables.Column(orderable=True)
    process_name = tables.Column(empty_values=(), verbose_name="Process Name")
    
    def render_process_name(self,record): 
        try:
            process = StoredProcess.objects.filter(StoppedProcess= record.id).first()
            if process:     
                return process.name
        except Exception as e:
            print(e)
        return "Unknown"
    class Meta:
        model = StoppedProcess
        template_name = "django_tables2/bootstrap5.html" # Szablon Bootstrapa
        fields = ("id", "author", "timestamp",)
        attrs = {"class": "table table-striped"}  

 
 
class StoppedProcessesView(SingleTableMixin, View):
    model = StoppedProcess
    table_class = StopedTable
    template_name = 'stopped.html'
    paginate_by = 42
    ordering = ['process__PID']  

    def get(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:
            stopped= StoppedProcess.objects.all()
            table = self.table_class(stopped)
            context = {"table": table}
            
            if request.htmx:
                return render(request, "stopped_table.html", context)  
            
            return render(request, self.template_name, context)  
        else:
            return redirect('login')


 
        
        
    