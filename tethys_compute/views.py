from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from tethyscluster.cli_api import TethysCluster
from tethyscluster import config, cluster
from subprocess import Popen
from multiprocessing import Process
from threading import Timer

from tethys_compute.models import TethysJob, Cluster

# Create your views here.

def index(request):
    clusters = Cluster.objects.all()
    return render(request, 'tethys_compute/cluster_index.html', {'title':'Computing Resources', 'clusters':clusters})




def create_cluster(request):
    if request.POST:
        name = request.POST['name']
        size = int(request.POST['size'])
        try:
            #sc = TethysCluster()
            #sc.start(name, cluster_size=size)

            # cm = config.get_cluster_manager()
            # cl = cm.get_default_template_cluster()
            # cl.update({'cluster_size':size})
            # cl.start()

            process = Popen(['tethyscluster', 'start', '-s', str(size), name])

            # t = Timer(120, _status_update)
            # t.start()

        except Exception as e:
            return HttpResponseServerError('There was an error with TethysCluster: %s' % str(e.message))

        cluster = Cluster(name=name, size=size)
        cluster.save()

        return redirect(reverse('index'))
    else:
        raise Exception


def update_cluster(request, pk):
    if request.POST:
        cluster = get_object_or_404(Cluster, id=pk)
        name = cluster.name
        delta_size = abs(request.POST['size'] - cluster.size)
        if delta_size != 0:
            cmd = 'addnode' if request.POST['size'] > cluster.size else 'deletenode'

            Popen(['tethyscluster', cmd, '-n', delta_size, name])

            cluster.size = request.POST['size']
            cluster.status = 'UPD'
            cluster.save()

        return redirect(reverse('index'))
    else:
        raise Exception

def delete_cluster(request, pk):
    cluster = get_object_or_404(Cluster, id=pk)
    name = cluster.name

    try:
        # sc = TethysCluster()
        # sc.terminate(name)

        # cm = config.get_cluster_manager()
        # cl = cm.get_cluster(name)
        # cl.terminate_cluster(force=True)

        # Popen(['tethyscluster', 'terminate', '-f', '-c', name])

        process = Process(target=_delete_cluster, args=(name,))
        process.start()

    except:
        HttpResponse('There was an error with TethysCluster')

    cluster.status = 'DEL'
    cluster.save()

    return redirect(reverse('index'))


def _start_cluster(name, size):
    cm = config.get_cluster_manager()
    cl = cm.get_default_template_cluster(name)
    cl.update({'cluster_size':size})
    cl.start()

def _delete_cluster(name):
    cm = config.get_cluster_manager()
    cl = cm.get_cluster(name)
    cl.terminate_cluster(force=True)
    cluster = Cluster.objects.get(name=name)
    cluster.delete()