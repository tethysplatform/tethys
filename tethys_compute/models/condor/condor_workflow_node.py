"""
********************************************************************************
* Name: condor_workflow_node
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from abc import abstractmethod

from django.db import models
from model_utils.managers import InheritanceManager

from tethys_compute.models.condor.condor_py_workflow import CondorPyWorkflow
from tethys_portal.optional_dependencies import optional_import

# optional imports
Node = optional_import("Node", from_module="condorpy")


class CondorWorkflowNode(models.Model):
    """
    Base class for CondorWorkflow Nodes
    """

    TYPES = (
        ("JOB", "JOB"),
        ("DAT", "DATA"),
        ("SUB", "SUBDAG"),
        ("SPL", "SPLICE"),
        ("FIN", "FINAL"),
    )

    TYPE_DICT = {k: v for v, k in TYPES}

    objects = InheritanceManager()

    name = models.CharField(max_length=1024)
    workflow = models.ForeignKey(
        CondorPyWorkflow, on_delete=models.CASCADE, related_name="node_set"
    )
    parent_nodes = models.ManyToManyField(
        "self", related_name="children_nodes", symmetrical=False
    )
    pre_script = models.CharField(max_length=1024, null=True, blank=True)
    pre_script_args = models.CharField(max_length=1024, null=True, blank=True)
    post_script = models.CharField(max_length=1024, null=True, blank=True)
    post_script_args = models.CharField(max_length=1024, null=True, blank=True)
    variables = models.JSONField(default=dict, null=True, blank=True)
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
        if not hasattr(self, "_condorpy_node"):
            condorpy_node = Node(
                job=self.job,
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
                done=self.done,
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
