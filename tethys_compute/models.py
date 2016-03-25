"""
********************************************************************************
* Name: models.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import os
import re
import shutil
import datetime
import inspect
from multiprocessing import Process
from abc import abstractmethod, abstractproperty
import logging
log = logging.getLogger('tethys.tethys_compute.models')

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.utils import timezone
from model_utils.managers import InheritanceManager

from tethys_compute import (TETHYSCLUSTER_CFG_FILE,
                            TETHYSCLUSTER_CFG_TEMPLATE,
                            TETHYSCLUSTER_AWS_CFG_FILE,
                            TETHYSCLUSTER_AWS_CFG_TEMPLATE,
                            TETHYSCLUSTER_AZURE_CFG_FILE,
                            TETHYSCLUSTER_AZURE_CFG_TEMPLATE)
from tethys_compute.utilities import DictionaryField, ListField
from tethys_apps.base.persistent_store import TethysFunctionExtractor

from tethyscluster import config as tethyscluster_config
from tethyscluster.sshutils import get_certificate_fingerprint
from condorpy import Job, Workflow, Node, Templates, logger as condorpy_logger


class SettingsCategory(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Settings Category'
        verbose_name_plural = 'Settings'

    def __unicode__(self):
        return self.name


class Setting(models.Model):
    name = models.TextField(max_length=30)
    content = models.TextField(max_length=500, blank=True)
    date_modified = models.DateTimeField('date modified', auto_now=True)
    category = models.ForeignKey(SettingsCategory, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name

    @classmethod
    def as_dict(cls):
        all_settings = cls.objects.all()

        settings_dict = dict()

        for setting in all_settings:
            code_name = setting.name.lower().replace(' ', '_')
            settings_dict[code_name] = setting.content

        return settings_dict

@receiver(post_save, sender=Setting)
def setting_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    settings = Setting.as_dict()
    if settings['default_cluster']:
        with open(TETHYSCLUSTER_CFG_FILE, 'w') as config_file:
            config_file.write(TETHYSCLUSTER_CFG_TEMPLATE % settings)

    if settings['aws_access_key_id'] \
        and settings['aws_secret_access_key'] \
        and settings['aws_user_id'] \
        and settings['key_name'] \
        and settings['key_location']:

        with open(TETHYSCLUSTER_AWS_CFG_FILE, 'w') as config_file:
            config_file.write(TETHYSCLUSTER_AWS_CFG_TEMPLATE % settings)

    if settings['subscription_id'] and settings['certificate_path']:
        settings['certificate_fingerprint'] = get_certificate_fingerprint(cert_location=settings['certificate_path'])
        with open(TETHYSCLUSTER_AZURE_CFG_FILE, 'w') as config_file:
            config_file.write(TETHYSCLUSTER_AZURE_CFG_TEMPLATE % settings)



class Cluster(models.Model):
    STATUSES = (
        ('STR', 'Starting'),
        ('RUN', 'Running'),
        ('STP', 'Stopped'),
        ('UPD', 'Updating'),
        ('DEL', 'Deleting'),
        ('ERR', 'Error'),
    )

    STATUS_DICT = {k:v for v,k in STATUSES}

    PROVIDERS = (
        ('AWS', 'Amazon Web Services'),
        ('AZR', 'Microsoft Azure'),
    )

    try:
        TC_MANAGER = tethyscluster_config.get_cluster_manager()
    except Exception as e:
        log.exception(e.message)
        TC_MANAGER = None

    _name = models.CharField(max_length=30, unique=True, default='tethys_default')
    _size = models.IntegerField(default=1)
    _status = models.CharField(max_length=3, choices=STATUSES, default=STATUS_DICT['Starting'])
    _cloud_provider = models.CharField(max_length=3, choices=PROVIDERS, default=PROVIDERS[0][0])
    _master_image_id = models.CharField(max_length=9, blank=True, null=True)
    _node_image_id = models.CharField(max_length=9, blank=True, null=True)
    _master_instance_type = models.CharField(max_length=20, blank=True, null=True)
    _node_instance_type = models.CharField(max_length=20, blank=True, null=True)
    _tethys_cluster = None

    @classmethod
    def create(cls, name, size=1):
        return cls(name=name, size=size)

    def __unicode__(self):
        return '%s (%d-node)' % (self.name, self.size)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        object.__setattr__(self, '_size', size)

    @property
    def status(self):
        self._update_status()
        field = self._meta.get_field('_status')
        return self._get_FIELD_display(field)

    @property
    def cloud_provider(self):
        field = self._meta.get_field('_cloud_provider')
        return self._get_FIELD_display(field)

    @property
    def tethys_cluster(self):
        if not self._tethys_cluster:
            try:
                self._tethys_cluster = self.TC_MANAGER.get_cluster_or_none(self.name)
            except Exception as e:
                log.exception(e.message)
        return self._tethys_cluster

    def create_tethys_cluster(self):
        tc = self.tethys_cluster
        if not tc:
            try:
                tc = self.TC_MANAGER.get_default_template_cluster(self.name)
                tc.update({'cluster_size':self.size})
                tc.start()
                self._tethys_cluster = tc
                self.connect_scheduler_and_master()
                self.save()
            except Exception as e:
                log.exception(e.message)
        else:
            pass
            #raise

    def connect_scheduler_and_master(self):
        def add_value_to_condor_config(config_file, attr, value):
            text = config_file.read()
            text_parts = re.split('^\s*%s ?= ?' % (attr, ), text, flags=re.IGNORECASE|re.M)
            if len(text_parts) > 1:
                last_part = text_parts.pop()
                new_last_part = '%s %s' % (value, last_part)
                text_parts.append(new_last_part)
                join_attr = '%s = ' % (attr, )
                new_text = join_attr.join(text_parts)
            else:
                new_text = '%s\n%s = %s\n' % (text, attr, value)
            config_file.seek(0)
            config_file.write(new_text)

        def get_public_ip():
            #TODO try this code
            # import socket
            # host_ip socket.gethostbyname(socket.gethostname())

            import urllib2, json
            json_response = urllib2.urlopen('http://ip.jsontest.com/').read()
            host_ip = json.loads(json_response)['ip']
            return host_ip

        tc = self.tethys_cluster
        if tc:
            master = tc.master_node
            settings = Setting.as_dict()
            scheduler_ip = settings['scheduler_ip'] or get_public_ip()
            master_local_config_file = master.ssh.execute('condor_config_val local_config_file')[0]
            with master.ssh.remote_file(master_local_config_file, mode='r+') as config_file:
                add_value_to_condor_config(config_file, 'FLOCK_FROM', scheduler_ip)

            p = os.popen('condor_config_val local_config_file')
            local_config_file = p.read().strip('\n')
            p.close()

            with open(local_config_file, 'r+') as config_file:
                add_value_to_condor_config(config_file, 'FLOCK_TO', master.ip_address)


    def update_tethys_cluster(self):
        #TODO check if connection to master needs to be updated
        tc = self.tethys_cluster
        if tc:
            tc_size = len(tc.nodes)
            delta = abs(tc_size - self.size)
            if delta != 0:
                cmd = self._add_nodes if self.size > tc_size else self._remove_nodes
                cmd(delta)
        else:
            self.create_tethys_cluster()
            #raise

    def delete_tethys_cluster(self):
        #TODO remove master_ip from local condor config
        tc = self.tethys_cluster
        if tc:
            tc.terminate_cluster(force=True)

    def _add_nodes(self, num_nodes, image_id=None, instance_type=None, spot_bid=None):
        tc = self.tethys_cluster
        tc.add_nodes(num_nodes, image_id=image_id, instance_type=instance_type, spot_bid=spot_bid)
        self._sync()

    def _remove_nodes(self, num_nodes):
        tc = self.tethys_cluster
        tc.remove_nodes(num_nodes=num_nodes, force=True)
        self._sync()

    def _update_status(self):
        old_status = self._status
        tc = self.tethys_cluster
        if tc is None:
            if self._status == self.STATUS_DICT['Starting']:
                pass
            elif self._status == self.STATUS_DICT['Deleting']:
                self.delete() #TODO: Not so sure this will work
            else:
                self._status = self.STATUS_DICT['Error']
        elif self._status == self.STATUS_DICT['Updating']:
            if tc.is_cluster_up() and len(tc.nodes) == self.size:
                self._status = self.STATUS_DICT['Running']
        elif (self._status == self.STATUS_DICT['Starting'] or self._status == self.STATUS_DICT['Stopped']) and tc.is_cluster_up():
            self._status = self.STATUS_DICT['Running']
        elif self._status == self.STATUS_DICT['Running']:
            if tc.is_cluster_stopped():
                self._status = self.STATUS_DICT['Stopped']
            elif not tc.is_valid():
                self._status = self.STATUS_DICT['Error']


@receiver(pre_save, sender=Cluster)
def cluster_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    instance._update_status()


@receiver(post_save, sender=Cluster)
def cluster_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        target = instance.create_tethys_cluster
    else:
        target = instance.update_tethys_cluster
    process = Process(target=target)
    process.start()


@receiver(post_delete, sender=Cluster)
def cluster_post_delete(sender, instance, **kwargs):
    process = Process(target=instance.delete_tethys_cluster)
    process.start()


class Scheduler(models.Model):
    name = models.CharField(max_length=1024)
    host = models.CharField(max_length=1024)
    username = models.CharField(max_length=1024, blank=True, null=True)
    password = models.CharField(max_length=1024, blank=True, null=True)
    private_key_path = models.CharField(max_length=1024, blank=True, null=True)
    private_key_pass = models.CharField(max_length=1024, blank=True, null=True)


class TethysJob(models.Model):
    """
    Base class for all job types. This is intended to be an abstract class that is not directly instantiated.
    """
    class Meta:
        verbose_name = 'Job'

    objects = InheritanceManager()

    STATUSES = (
        ('PEN', 'Pending'),
        ('SUB', 'Submitted'),
        ('RUN', 'Running'),
        ('COM', 'Complete'),
        ('ERR', 'Error'),
        ('ABT', 'Aborted'),
        ('VAR', 'Various'),
        ('VCP', 'Various-Complete'),
    )

    STATUS_DICT = {k: v for v, k in STATUSES}

    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=2048, blank=True, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=1024)
    creation_time = models.DateTimeField(auto_now_add=True)
    execute_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    completion_time = models.DateTimeField(blank=True, null=True)
    workspace = models.CharField(max_length=1024, default='')
    extended_properties = DictionaryField(default='', blank=True)
    _process_results_function = models.CharField(max_length=1024, blank=True, null=True)
    _status = models.CharField(max_length=3, choices=STATUSES, default=STATUSES[0][0])

    @property
    def update_status_interval(self):
        if not hasattr(self, '_update_status_interval'):
            self._update_status_interval = datetime.timedelta(seconds=10)
        return self._update_status_interval

    @property
    def last_status_update(self):
        return self._last_status_update

    @property
    def status(self):
        self.update_status()
        field = self._meta.get_field('_status')
        status = self._get_FIELD_display(field)
        return status

    @property
    def run_time(self):
        # start_time = self.start_time
        start_time = self.execute_time
        if start_time:
            end_time = self.completion_time or datetime.datetime.now(start_time.tzinfo)
            run_time = end_time - start_time
        else:
            if self.completion_time and self.execute_time:
                run_time = self.completion_time - self.execute_time
            else:
                return ''

        times = []
        total_seconds = run_time.seconds
        times.append(('days', run_time.days))
        times.append(('hr', total_seconds/3600))
        times.append(('min', (total_seconds%3600)/60))
        times.append(('sec', total_seconds%60))
        run_time_str = ''
        for time_str, time in times:
            if time:
                run_time_str += "%s %s " % (time, time_str)
        if not run_time_str or (run_time.days == 0 and total_seconds < 2):
            run_time_str = '%.2f sec' % (total_seconds + float(run_time.microseconds)/1000000,)
        return run_time_str

    def execute(self, *args, **kwargs):
        """
        executes the job
        """
        self.execute_time = timezone.now()
        self._status = 'PEN'
        self.save()
        self._execute(*args, **kwargs)

    def update_status(self, *args, **kwargs):
        old_status = self._status
        if self._status in ['PEN', 'SUB', 'RUN', 'VAR']:
            if not hasattr(self, '_last_status_update') \
                    or datetime.datetime.now()-self.last_status_update > self.update_status_interval:
                self._update_status(*args, **kwargs)
                self._last_status_update = datetime.datetime.now()
            if self._status == 'RUN' and (old_status == 'PEN' or old_status == 'SUB'):
                self.start_time = timezone.now()
            if self._status == "COM" or self._status == "VCP":
                self.process_results()
            elif self._status == 'ERR' or self._status == 'ABT':
                self.completion_time = timezone.now()
            self.save()

    @property
    def process_results_function(self):
        """

        Returns:
            A function handle or None if function cannot be resolved.
        """
        if self._process_results_function:
            function_extractor = TethysFunctionExtractor(self._process_results_function, None)
            if function_extractor.valid:
                return function_extractor.function

    @process_results_function.setter
    def process_results_function(self, function):
        module_path = inspect.getmodule(function).__name__.split('.')[2:]
        module_path.append(function.__name__)
        self._process_results_function = '.'.join(module_path)

    def process_results(self, *args, **kwargs):
        """

        """
        self.completion_time = timezone.now()
        self.save()
        self._process_results(*args, **kwargs)

    @abstractmethod
    def _execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def _update_status(self, *args, **kwargs):
        pass

    @abstractmethod
    def _process_results(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self):
        """
        Stops job from executing
        """
        raise NotImplementedError()

    @abstractmethod
    def pause(self):
        """
        Pauses job during execution
        """
        raise NotImplementedError()

    @abstractmethod
    def resume(self):
        """
        Resumes a job that has been paused
        """
        raise NotImplementedError()


class BasicJob(TethysJob):
    """
    Basic job type. Use this class as a model for subclassing TethysJob
    """

    def _execute(self, *args, **kwargs):
        pass

    def _update_status(self, *args, **kwargs):
        pass

    def _process_results(self, *args, **kwargs):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass


# condorpy_logger.activate_console_logging()


class CondorBase(TethysJob):
    """
    Base class for CondorJob and CondorWorkflow
    """
    cluster_id = models.IntegerField(blank=True, default=0)
    remote_id = models.CharField(max_length=32, blank=True, null=True)
    scheduler = models.ForeignKey(Scheduler, on_delete=models.SET_NULL, blank=True, null=True)

    STATUS_MAP = {'Unexpanded': 'PEN',
                  'Idle': 'SUB',
                  'Running': 'RUN',
                  'Removed': 'ABT',
                  'Completed': 'COM',
                  'Held': 'ERR',
                  'Submission_err': 'ERR',
                  'Various': 'VAR',
                  'Various-Complete': 'VCP',
                  }

    @property
    def condor_object(self):
        """
        Returns: an instance of a condorpy job or condorpy workflow with scheduler, cluster_id, and remote_id attributes set
        """
        condor_object = self._condor_object
        if self.remote_id:
            condor_object._remote_id = self.remote_id
        condor_object._cluster_id = self.cluster_id
        condor_object._cwd = self.workspace
        if self.scheduler:
            condor_object.set_scheduler(self.scheduler.host,
                                        self.scheduler.username,
                                        self.scheduler.password,
                                        self.scheduler.private_key_path,
                                        self.scheduler.private_key_pass
                                        )
        return condor_object

    @abstractproperty
    def _condor_object(self):
        """
        Returns: an instance of a condorpy job or condorpy workflow
        """
        pass

    @property
    def statuses(self):
        updated = True
        if hasattr(self, '_last_status_update'):
            updated = datetime.datetime.now() - self.last_status_update < self.update_status_interval
        if not (hasattr(self, '_statuses') and updated):
            self._statuses = self.condor_object.statuses

        return self._statuses

    @abstractmethod
    def _execute(self, *args, **kwargs):
        self.cluster_id = self.condor_object.submit(*args, **kwargs)
        self.save()

    def _update_status(self):
        if not self.execute_time:
            return 'PEN'
        try:
            # get the status of the condorpy job/workflow
            condor_status = self.condor_object.status
            if condor_status == 'Various':
                statuses = self.statuses
                running_statuses = statuses['Unexpanded'] + statuses['Idle'] + statuses['Running']
                if not running_statuses:
                    condor_status = 'Various-Complete'
        except Exception, e:
            # raise e
            condor_status = 'Submission_err'
        self._status = self.STATUS_MAP[condor_status]
        self.save()

    def _process_results(self):
        if self.scheduler:
            self.condor_object.sync_remote_output()
            self.condor_object.close_remote()

    def stop(self):
        self.condor_object.remove()

    def pause(self):
        """
        Pauses job during execution
        """
        pass
        # self.condor_object.hold()

    def resume(self):
        """
        Resumes a job that has been paused
        """
        pass
        # self.condor_object.release()

    def update_database_fields(self):
        self.remote_id = self._condor_object._remote_id


class CondorPyJob(models.Model):
    """
    Database model for condorpy jobs
    """
    condorpyjob_id = models.AutoField(primary_key=True)
    _attributes = DictionaryField(default='')
    _num_jobs = models.IntegerField(default=1)
    _remote_input_files = ListField(default='')

    @classmethod
    def get_condorpy_template(cls, template_name):
        template_name = template_name or 'base'
        template = getattr(Templates, template_name)
        if not template:
            template = Templates.base
        return template

    @property
    def condorpy_job(self):

        if not hasattr(self, '_condorpy_job'):
            job = Job(name=self.name.replace(' ', '_'),
                      attributes=self.attributes,
                      num_jobs=self.num_jobs,
                      remote_input_files=self.remote_input_files,
                      working_directory=self.workspace)

            self._condorpy_job = job
        return self._condorpy_job

    @property
    def attributes(self):
        return self._attributes

    # @attributes.setter
    # def attributes(self, attributes):
    #     assert isinstance(attributes, dict)
    #     self.condorpy_job._attributes = attributes
    #     self._attributes = attributes

    @property
    def num_jobs(self):
        return self._num_jobs

    @num_jobs.setter
    def num_jobs(self, num_jobs):
        num_jobs = int(num_jobs)
        self.condorpy_job.num_jobs = num_jobs
        self._num_jobs = num_jobs

    @property
    def remote_input_files(self):
        return self._remote_input_files

    @remote_input_files.setter
    def remote_input_files(self, remote_input_files):
        self.condorpy_job.remote_input_files = remote_input_files
        self._remote_input_files = remote_input_files

    @property
    def initial_dir(self):
        return os.path.join(self.workspace, self.condorpy_job.initial_dir)

    def get_attribute(self, attribute):
        self.condorpy_job.get(attribute)

    def set_attribute(self, attribute, value):
        setattr(self.condorpy_job, attribute, value)

    def update_database_fields(self):
        self._attributes = self.condorpy_job.attributes
        self.num_jobs = self.condorpy_job.num_jobs
        self.remote_input_files = self.condorpy_job.remote_input_files


class CondorJob(CondorBase, CondorPyJob):
    """
    CondorPy Job job type
    """

    @property
    def _condor_object(self):
        """
        Returns: an instance of a condorpy job
        """
        return self.condorpy_job

    def _execute(self, queue=None, options=[]):
        self.num_jobs = queue or self.num_jobs
        super(self.__class__, self)._execute(queue=self.num_jobs, options=options)

    def update_database_fields(self):
        CondorBase.update_database_fields(self)
        CondorPyJob.update_database_fields(self)


@receiver(pre_save, sender=CondorJob)
def condor_job_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    instance.update_database_fields()


@receiver(pre_delete, sender=CondorJob)
def condor_job_pre_delete(sender, instance, using, **kwargs):
    try:
        instance.condor_object.close_remote()
        shutil.rmtree(instance.initial_dir)
    except Exception, e:
        log.exception(e.message)


class CondorPyWorkflow(models.Model):
    """
    Database model for condorpy workflows
    """
    condorpyworkflow_id = models.AutoField(primary_key=True)
    _max_jobs = DictionaryField(default='', blank=True)
    _config = models.CharField(max_length=1024, null=True, blank=True)

    @property
    def condorpy_workflow(self):
        """
        Returns: an instance of a condorpy Workflow
        """
        if not hasattr(self, '_condorpy_workflow'):
            workflow = Workflow(name=self.name.replace(' ', '_'),
                                max_jobs=self.max_jobs,
                                config=self.config,
                                working_directory=self.workspace
                                )

            self._condorpy_workflow = workflow
            self.load_nodes()
        return self._condorpy_workflow

    @property
    def max_jobs(self):
        return self._max_jobs

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self.condorpy_workflow.config = config
        self._config = config

    @property
    def nodes(self):
        return self.node_set.select_subclasses()

    def load_nodes(self):
        workflow = self.condorpy_workflow
        node_dict = dict()

        def add_node_to_dict(node):
            if node not in node_dict:
                node_dict[node] = node.condorpy_node

        for node in self.nodes:
            add_node_to_dict(node)
            condorpy_node = node_dict[node]
            parents = node.parents
            for parent in parents:
                add_node_to_dict(parent)
                condorpy_node.add_parent(node_dict[parent])
            workflow.add_node(condorpy_node)

    def add_max_jobs_throttle(self, category, max_jobs):
        """
        Adds a max_jobs attribute to the workflow to throttle the number of jobs in a category

        Args:
            category (str): The category to throttle.
            max_jobs (int): The maximum number of jobs that submit at one time
        """
        self.max_jobs[category] = max_jobs
        self.condorpy_workflow.add_max_jobs_throttle(category, max_jobs)

    def update_database_fields(self):
        # self.max_jobs = self.condorpy_workflow.max_jobs
        # self.config = self.condorpy_workflow.config
        for node in self.nodes:
            node.update_database_fields()


class CondorWorkflow(CondorBase, CondorPyWorkflow):
    """
    CondorPy Workflow job type
    """

    @property
    def _condor_object(self):
        """
        Returns: an instance of a condorpy Workflow
        """
        return self.condorpy_workflow

    def _execute(self, options=[]):
        self.load_nodes()
        super(self.__class__, self)._execute(options=options)

    def get_job(self, job_name):
        try:
            node = self.node_set.get_subclass(name=job_name)
            return node
        except CondorWorkflowNode.DoesNotExist:
            return None

    def update_database_fields(self):
        CondorBase.update_database_fields(self)
        CondorPyWorkflow.update_database_fields(self)


@receiver(pre_save, sender=CondorWorkflow)
def condor_workflow_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    instance.update_database_fields()


@receiver(pre_delete, sender=CondorWorkflow)
def condor_workflow_pre_delete(sender, instance, using, **kwargs):
    try:
        instance.condor_object.close_remote()
        shutil.rmtree(instance.initial_dir)
    except Exception, e:
        log.exception(e.message)


class CondorWorkflowNode(models.Model):
    """
    Base class for CondorWorkflow Nodes
    """
    TYPES = (('JOB', 'JOB'),
             ('DAT', 'DATA'),
             ('SUB', 'SUBDAG'),
             ('SPL', 'SPLICE'),
             ('FIN', 'FINAL'),
             )

    TYPE_DICT = {k: v for v, k in TYPES}

    objects = InheritanceManager()

    name = models.CharField(max_length=1024)
    workflow = models.ForeignKey(CondorPyWorkflow, on_delete=models.CASCADE, related_name='node_set')
    parent_nodes = models.ManyToManyField('self', related_name='children_nodes', symmetrical=False)
    pre_script = models.CharField(max_length=1024, null=True, blank=True)
    pre_script_args = models.CharField(max_length=1024, null=True, blank=True)
    post_script = models.CharField(max_length=1024, null=True, blank=True)
    post_script_args = models.CharField(max_length=1024, null=True, blank=True)
    variables = DictionaryField(default='', blank=True)
    priority = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=128, null=True, blank=True)
    retry = models.PositiveSmallIntegerField(null=True, blank=True)
    retry_unless_exit_value = models.IntegerField(null=True, blank=True)
    pre_skip = models.IntegerField(null=True, blank=True)
    abort_dag_on = models.IntegerField(null=True, blank=True)
    abort_dag_on_return_value = models.IntegerField(null=True, blank=True)
    dir = models.CharField(max_length=1024, null=True, blank=True)
    noop = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    objects = InheritanceManager()

    @abstractproperty
    def type(self):
        pass

    @abstractproperty
    def job(self):
        pass

    @property
    def condorpy_node(self):
        if not hasattr(self, '_condorpy_node'):
            condorpy_node = Node(job=self.job,
                                 pre_script=self.pre_script,
                                 pre_script_args=self.pre_script_args,
                                 post_script=self.post_script,
                                 post_script_args=self.post_script_args,
                                 variables=self.variables,
                                 priority=self.priority,
                                 category=self.category,
                                 retry=self.retry,
                                 pre_skip=self.pre_skip,
                                 abort_dag_on=self.abort_dag_on,
                                 abort_dag_on_return_value=self.abort_dag_on_return_value,
                                 dir=self.dir,
                                 noop=self.noop,
                                 done=self.done
                                 )
            self._condorpy_node = condorpy_node
        return self._condorpy_node

    @property
    def parents(self):
        return self.parent_nodes.select_subclasses()

    def add_parent(self, parent):
        self.parent_nodes.add(parent)

    def update_database_fields(self):
        pass


class CondorWorkflowJobNode(CondorWorkflowNode, CondorPyJob):
    """
    CondorWorkflow JOB type node
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize both CondorWorkflowNode and CondorPyJob

        Args:
            name:
            workflow:
            attributes:
            num_jobs:
            remote_input_files:
        """
        CondorWorkflowNode.__init__(self, *args, **kwargs)
        CondorPyJob.__init__(self, *args, **kwargs)

    @property
    def type(self):
        return 'JOB'

    @property
    def workspace(self):
        return ''

    @property
    def job(self):
        return self.condorpy_job

    def update_database_fields(self):
        CondorWorkflowNode.update_database_fields(self)
        CondorPyJob.update_database_fields(self)


@receiver(pre_save, sender=CondorWorkflowJobNode)
def condor_workflow_job_node_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    instance.update_database_fields()
