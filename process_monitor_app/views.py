import uuid
from datetime import datetime

import django_filters
import django_tables2 as tables
import psutil
import xlwt
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views import View
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from process_monitor_app.models import (Process, Snapshot, StoppedProcess,
                                        StoredProcess)

# Lista procesów, które nie mogą być zatrzymane tak dla przykładu
UNSTOPABLE = [
    "systemd",
    "init",
    "kthreadd",
    "ksoftirqd",
    "kworker",
    "kdevtmpfs",
    "khungtaskd",
    "kintegrityd",
    "kblockd",
    "kswapd",
    "ksmd",
    "khugepaged",
    "kthrotld",
    "kmpathd",
    "kpsmoused",
]


class HomeView(View):
    def get(self, request):
        return render(request, "index.html")


class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("process_list")
        else:
            return redirect("login")


# region processes
class ProcessFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains"
    )  # Filtrowanie po nazwie procesu

    class Meta:
        model = Process
        fields = ["PID", "name", "status"]


class ProcessTable(tables.Table):

    stop = tables.Column(empty_values=(), orderable=False, verbose_name="Action")
    PID = tables.Column(orderable=True)
    name = tables.Column(orderable=True)
    status = tables.Column(orderable=True)
    start_time = tables.Column(orderable=True)
    duration = tables.Column(orderable=True)
    memory_usage_MB = tables.Column(orderable=True, verbose_name="Memory (MB)")
    CPU_Usage_Percent = tables.Column(orderable=True, verbose_name="CPU (%)")

    def render_stop(self, record):
        stop_url = reverse("stop_process", args=[record.id, record.PID])
        return format_html(
            '<button hx-post="{}" '
            'hx-trigger="click" '
            'hx-confirm="Are you sure you want to stop this process?" '
            'hx-target="closest tr" '
            'hx-swap="outerHTML" '
            'class="btn btn-danger">Stop</button>',
            stop_url,
        )

    class Meta:
        fields = (
            "PID",
            "name",
            "status",
            "start_time",
            "duration",
            "memory_usage_MB",
            "CPU_Usage_Percent",
        )


class ProcessListView(SingleTableMixin, FilterView):
    model = Process
    table_class = ProcessTable
    template_name = "htmxprocess.html"
    filterset_class = ProcessFilter
    paginate_by = 42
    ordering = ["PID"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_loaded"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_authenticated:
            if self.request.htmx:
                return render(self.request, "processes_table.html", context)
            return super().render_to_response(context, **response_kwargs)
        else:
            return redirect("login")


# endregion


# region snapshot
class SnapshotView(View):

    def post(self, request):
        snapshot = Snapshot(author=request.user.username)
        snapshot.save()
        for process in Process.objects.all():
            iid_str = f"{process.id}--{process.PID}--{process.name}--{process.start_time}{datetime.now()}"
            iid = uuid.uuid5(uuid.NAMESPACE_DNS, iid_str)
            try:
                stored_process = StoredProcess(
                    iid=iid,
                    PID=process.PID,
                    name=process.name,
                    status=process.status,
                    start_time=process.start_time,
                    duration=process.duration,
                    memory_usage_MB=process.memory_usage_MB,
                    CPU_Usage_Percent=process.CPU_Usage_Percent,
                    snapshot=snapshot,
                )
                stored_process.save()
                # snapshot..add(stored_process)
            except Exception as e:
                print(e)
                continue

        return redirect("process_list")


class SnapshotTable(tables.Table):
    id = tables.Column(orderable=True)
    timestamp = tables.Column(orderable=True)
    author = tables.Column(orderable=True)
    details = tables.Column(empty_values=(), orderable=False, verbose_name="details")
    export_to_excel = tables.Column(
        empty_values=(), orderable=False, verbose_name="Export"
    )

    def render_details(self, record):
        process_detail_url = reverse(
            "snapshot_detail", args=[record.id]
        )  # Ścieżka do widoku szczegółów procesu
        return format_html(
            '<a href="{}" class="process-link"> Detail</a>',
            process_detail_url,
        )

    def render_export_to_excel(self, record):
        export_url = reverse("export_snapshot", args=[record.id])
        return format_html(
            '<a href="{}" class="stop-btn" download>Export</a>', export_url
        )

    class Meta:
        model = Process
        fields = ("id", "author")


class SanpShotProcessTable(tables.Table):

    PID = tables.Column(orderable=True)
    name = tables.Column(orderable=True)
    status = tables.Column(orderable=True)
    start_time = tables.Column(orderable=True)
    duration = tables.Column(orderable=True)
    memory_usage_MB = tables.Column(orderable=True, verbose_name="Memory (MB)")
    CPU_Usage_Percent = tables.Column(orderable=True, verbose_name="CPU (%)")

    class Meta:
        # model = Process
        fields = (
            "PID",
            "name",
            "status",
            "start_time",
            "duration",
            "memory_usage_MB",
            "CPU_Usage_Percent",
        )


class SnapshotDetailedView(SingleTableMixin, FilterView):

    model = StoredProcess
    table_class = SanpShotProcessTable
    template_name = "snap_detail.html"
    filterset_class = ProcessFilter
    paginate_by = 42
    ordering = ["PID"]

    def get_queryset(self):
        """Filtrowanie rekordów StoredProcess na podstawie snapshot_id"""
        snapshot_id = self.kwargs.get("snap_id")
        return StoredProcess.objects.filter(snapshot_id=snapshot_id)

    def get_context_data(self, **kwargs):
        """Dodaj sumę CPU i RAM do kontekstu widoku"""
        context = super().get_context_data(**kwargs)
        snap_processes = self.get_queryset()
        total_cpu = (
            snap_processes.aggregate(Sum("CPU_Usage_Percent"))["CPU_Usage_Percent__sum"]
            or 0
        )
        total_ram = (
            snap_processes.aggregate(Sum("memory_usage_MB"))["memory_usage_MB__sum"]
            or 0
        )
        number_of_processes = len(snap_processes)
        context["total_cpu"] = total_cpu
        context["total_ram"] = total_ram
        context["nop"] = number_of_processes
        return context

    def render_to_response(self, context, **response_kwargs):

        if self.request.user.is_authenticated:
            if self.request.htmx:
                return render(self.request, "processes_table.html", context)
            return super().render_to_response(context, **response_kwargs)
        else:
            return redirect("login")


class SnapshotListView(SingleTableMixin, View):
    model = Snapshot
    table_class = SnapshotTable
    template_name = "snaps.html"
    paginate_by = 42
    ordering = ["id"]

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            snapshots = Snapshot.objects.all().order_by(*self.ordering)  #
            table = self.table_class(snapshots)
            total_cpu = 0.0
            total_ram = 0.0
            number_of_processes = 0
            for snap in snapshots:
                snap_processes = StoredProcess.objects.filter(snapshot_id=snap.id)
                total_cpu += (
                    snap_processes.aggregate(Sum("CPU_Usage_Percent"))[
                        "CPU_Usage_Percent__sum"
                    ]
                    or 0
                )
                total_ram += (
                    snap_processes.aggregate(Sum("memory_usage_MB"))[
                        "memory_usage_MB__sum"
                    ]
                    or 0
                )
                number_of_processes += len(snap_processes)

            context = {
                "table": table,
                "total_cpu": total_cpu,
                "total_ram": total_ram,
                "nop": number_of_processes,
            }

            if request.htmx:
                return render(request, "snap_table.html", context)

            return render(request, self.template_name, context)
        else:
            return redirect("login")


class ExportSnapshotView(View):

    def get(self, request, snap_id):
        snapshot = Snapshot.objects.get(id=snap_id)
        processes = StoredProcess.objects.filter(snapshot_id=snapshot.id)
        wb = xlwt.Workbook(encoding="utf-8")
        ws = wb.add_sheet("Processes")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = [
            "PID",
            "Name",
            "STATUS",
            "Start Time",
            "Duration sek.",
            "Memory MB",
            "CPU %",
        ]
        for col_num, column_title in enumerate(columns):
            ws.write(0, col_num, column_title, font_style)
        font_style = xlwt.XFStyle()
        for process in processes:
            row_num += 1
            row = [
                process.PID,
                process.name,
                process.status,
                process.start_time,
                process.duration,
                process.memory_usage_MB,
                process.CPU_Usage_Percent,
            ]
            for col_num, value in enumerate(row):
                font_style = xlwt.XFStyle()
                if isinstance(value, datetime):
                    font_style.num_format_str = "dd/mm/yyyy hh:mm:ss"
                if value is None:
                    value = "null"
                try:
                    ws.write(row_num, col_num, row[col_num], font_style)
                except Exception as e:
                    print(e)
        response = HttpResponse(
            headers={
                "Content-Type": "application/vnd.ms-excel",
                "Content-Disposition": f'attachment; filename="snapshot_by_{snapshot.author}_{snapshot.timestamp}.xls"',
            }
        )
        wb.save(response)
        return response


# endregion


# region stop process
class StopProcessView(View):

    def post(self, request, process_id, pid):

        try:
            process = Process.objects.get(PID=pid)
            try:
                real_process = psutil.Process(pid=pid)
                if real_process.name() not in UNSTOPABLE and real_process.pid != 1:
                    try:
                        real_process.kill()
                    except Exception as e:
                        messages.warning(request, f"{e.__context__.strerror}")
                        return redirect("process_list")

            except psutil.NoSuchProcess as e:
                messages.warning(request, f"{e.__context__.strerror}")
                return redirect("process_list")
            stopped_proc = StoppedProcess(
                timestamp=datetime.now(),
                author=request.user.username,
                name=process.name,
            )
            stopped_proc.save()
            process.delete()
            return redirect("process_list")
        except Exception as e:
            print(e)
            return redirect("process_list")


class StopPedTable(tables.Table):
    id = tables.Column(orderable=True)
    timestamp = tables.Column(orderable=True)
    author = tables.Column(orderable=True, verbose_name="user name")

    class Meta:
        model = StoppedProcess
        fields = ("id", "timestamp", "name")


class StoppedProcessesView(SingleTableMixin, FilterView):
    model = StoppedProcess
    table_class = StopPedTable
    template_name = "stopped.html"
    paginate_by = 42
    ordering = ["id"]

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_authenticated:
            if self.request.htmx:
                return render(self.request, "stopped_table.html", context)
            return super().render_to_response(context, **response_kwargs)
        else:
            return redirect("login")


# endregion
