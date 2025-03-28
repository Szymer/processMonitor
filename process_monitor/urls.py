"""
URL configuration for process_monitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from process_monitor_app.views import (
    ExportSnapshotView,
    HomeView,
    LoginView,
    ProcessListView,
    SnapshotDetailedView,
    SnapshotListView,
    SnapshotView,
    StoppedProcessesView,
    StopProcessView,
)
from process_monitor_app.views import logout_view as logout

urlpatterns = [
    path("admin/", admin.site.urls),
    path("home/", HomeView.as_view(), name="home"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout, name="logout"),
    path("processes/", ProcessListView.as_view(), name="process_list"),
    path(
        "processes/stop/<int:process_id>&<int:pid>/",
        StopProcessView.as_view(),
        name="stop_process",
    ),
    path("processes/save/", SnapshotView.as_view(), name="snapshot"),
    path("snapshots/", SnapshotListView.as_view(), name="snapshot_list"),
    path("stopped/", StoppedProcessesView.as_view(), name="stopped_list"),
    path(
        "snapshots/export/<int:snap_id>",
        ExportSnapshotView.as_view(),
        name="export_snapshot",
    ),
    path(
        "snapshots/detail/<int:snap_id>",
        SnapshotDetailedView.as_view(),
        name="snapshot_detail",
    ),
]
