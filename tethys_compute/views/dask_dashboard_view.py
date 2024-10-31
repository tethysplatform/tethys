from django.shortcuts import render, reverse
from tethys_compute.models.dask.dask_scheduler import DaskScheduler
from tethys_portal.optional_dependencies import optional_import

# optional imports
server_document = optional_import("server_document", from_module="bokeh.embed")


def dask_dashboard(request, dask_scheduler_id, page="status"):
    dask_scheduler = DaskScheduler.objects.get(id=dask_scheduler_id)
    scheduler_name = dask_scheduler.name
    dashboard_host = dask_scheduler.dashboard

    # Append http if not exists
    if "http" not in dashboard_host:
        dashboard_host = "http://" + dashboard_host

    # Add forward slash to end if not exist
    if dashboard_host[-1] != "/":
        dashboard_host = dashboard_host + "/"

    # Define url link for each page
    url_link = dashboard_host + page
    back_link = reverse("admin:tethys_compute_daskscheduler_changelist")
    status_link = reverse(
        "admin:dask_dashboard",
        kwargs={"page": "status", "dask_scheduler_id": dask_scheduler_id},
    )
    workers_link = reverse(
        "admin:dask_dashboard",
        kwargs={"page": "workers", "dask_scheduler_id": dask_scheduler_id},
    )
    tasks_link = reverse(
        "admin:dask_dashboard",
        kwargs={"page": "tasks", "dask_scheduler_id": dask_scheduler_id},
    )
    systems_link = reverse(
        "admin:dask_dashboard",
        kwargs={"page": "system", "dask_scheduler_id": dask_scheduler_id},
    )
    profile_link = reverse(
        "admin:dask_dashboard",
        kwargs={"page": "profile", "dask_scheduler_id": dask_scheduler_id},
    )
    graph_link = reverse(
        "admin:dask_dashboard",
        kwargs={"page": "graph", "dask_scheduler_id": dask_scheduler_id},
    )
    groups_link = reverse(
        "admin:dask_dashboard",
        kwargs={"page": "groups", "dask_scheduler_id": dask_scheduler_id},
    )

    # Create script that will load the app
    script = server_document(url_link)

    context = {
        "back_link": back_link,
        "scheduler_name": scheduler_name,
        "the_script": script,
        "status_link": status_link,
        "workers_link": workers_link,
        "tasks_link": tasks_link,
        "systems_link": systems_link,
        "profile_link": profile_link,
        "graph_link": graph_link,
        "groups_link": groups_link,
        "dashboard_link": dashboard_host,
    }

    return render(request, "tethys_compute/dask_scheduler_dashboard.html", context)
