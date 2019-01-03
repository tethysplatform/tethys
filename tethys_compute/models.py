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
import shutil
import datetime
import inspect
from abc import abstractmethod
import logging

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from model_utils.managers import InheritanceManager

from tethys_compute.utilities import DictionaryField, ListField
from tethys_apps.base.function_extractor import TethysFunctionExtractor

from condorpy import Job, Workflow, Node, Templates

log = logging.getLogger('tethys' + __name__)


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
            # TODO: Is this code reachable?
            if self.completion_time and self.execute_time:
                run_time = self.completion_time - self.execute_time
            else:
                return ''

        return run_time

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
                    or datetime.datetime.now() - self.last_status_update > self.update_status_interval:
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
        """  # noqa: E501
        condor_object = self._condor_object
        condor_object._cluster_id = self.cluster_id
        condor_object._cwd = self.workspace
        if self.scheduler:
            condor_object.set_scheduler(self.scheduler.host,
                                        self.scheduler.username,
                                        self.scheduler.password,
                                        self.scheduler.private_key_path,
                                        self.scheduler.private_key_pass
                                        )
            # save remote_id if it's not already saved, and then make sure the condor_object's remote_id is in sync
            self.remote_id = self.remote_id or condor_object._remote_id
            condor_object._remote_id = self.remote_id
        return condor_object

    @abstractmethod
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
        except Exception:
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

    def __init__(self, *args, **kwargs):
        # if condorpy_template_name or attributes is passed in then get the template and add it to the _attributes
        attributes = kwargs.pop('attributes', dict())
        _attributes = kwargs.get('_attributes', dict())
        attributes.update(_attributes)
        condorpy_template_name = kwargs.pop('condorpy_template_name', None)
        if condorpy_template_name is not None:
            template = self.get_condorpy_template(condorpy_template_name)
            template.update(attributes)
            attributes = template
        kwargs['_attributes'] = attributes
        super(CondorPyJob, self).__init__(*args, **kwargs)

    @classmethod
    def get_condorpy_template(cls, template_name):
        template_name = template_name or 'base'
        template = getattr(Templates, template_name, None)
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

    @attributes.setter
    def attributes(self, attributes):
        assert isinstance(attributes, dict)
        self._attributes = attributes
        self.condorpy_job._attributes = attributes

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
        return self.condorpy_job.get(attribute)

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
        shutil.rmtree(instance.initial_dir, ignore_errors=True)
    except Exception as e:
        log.exception(str(e))


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

    @max_jobs.setter
    def max_jobs(self, max_jobs):
        self.condorpy_workflow._max_jobs = max_jobs
        self._max_jobs = max_jobs

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
        shutil.rmtree(instance.workspace, ignore_errors=True)
    except Exception as e:
        log.exception(str(e))


class CondorWorkflowNode(models.Model):
    """
    Base class for CondorWorkflow Nodes

    Args:
        name (str):
        workflow (`CondorWorkflow`): instance of a `CondorWorkflow` that node belongs to
        parent_nodes (list): list of `CondorWorkflowNode` objects that are prerequisites to this node
        pre_script (str):
        pre_script_args (str):
        post_script (str):
        post_script_args (str):
        variables (dict):
        priority (int):
        category (str):
        retry (int):
        retry_unless_exit_value (int):
        pre_skip (int):
        abort_dag_on (int):
        dir (str):
        noop (bool):
        done (bool):

    For a description of the arguments see http://research.cs.wisc.edu/htcondor/manual/v8.6/2_10DAGMan_Applications.html
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

    @abstractmethod
    def type(self):
        pass

    @abstractmethod
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


@receiver(post_save, sender=CondorJob)
@receiver(post_save, sender=BasicJob)
@receiver(post_save, sender=TethysJob)
def tethys_job_post_save(sender, instance, raw, using, update_fields, **kwargs):
    if instance.name.find('{id}') >= 0:
        instance.name = instance.name.format(id=instance.id)
        instance.save()
