import django_tables2 as tables
import django_filters

from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.views.decorators.vary import vary_on_headers

from process_monitor_app.models import Process






class HomeView(View):
    def get(self, request):
        return render(request, "index.html")
    
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")
    
# class ProcessListView(View):
#     def get(self, request):
#         dupa =  Process.objects.all()
#         context = {
#                 "processes": dupa,
#                 'user': request.user
            
#         }
#         return render(request, "processes.html", context)
class ProcessFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label="Search by Name")  # Filtrowanie po nazwie procesu
    class Meta:
        model = Process
        fields = ['name']

class ProcessTable(tables.Table):
    class Meta:
        model = Process
        template_name = "django_tables2/bootstrap5.html"  # Możesz użyć innego szablonu
        fields = ("id", "name", "status", "start_time", "duration", "memory_usage_MB", "CPU_Usage_Percent")
        attrs = {"class": "table table-striped"}  # Bootstrap dla lepszego wyglądu


# Widok z filtrowaniem i sortowaniem

class ProcessListView(ListView):
    model = Process
    template_name = 'processes.html'
    # template_name = 'htmxprocess.html'
    context_object_name = 'processes'
    paginate_by = 350  # Liczba elementów na stronie

    def get_queryset(self):
        queryset = Process.objects.all()
        self.filterset = ProcessFilter(self.request.GET, queryset=queryset)  # Filtrowanie
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset  # Przekazanie obiektu filtra do szablonu
        context['table'] = ProcessTable(self.get_queryset())  # Przekazanie tabeli do szablonu
        return context

    def render_to_response(self, context, **response_kwargs):
        """Jeśli żądanie pochodzi od HTMX, renderuj tylko tabelę."""
        if self.request.htmx:
            context =self.get_context_data(**response_kwargs)
            return render(self.request, self.template_name, context)
        return super().render_to_response(context, **response_kwargs)





