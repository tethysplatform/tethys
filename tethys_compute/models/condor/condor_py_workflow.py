"""
********************************************************************************
* Name: condor_py_workflow
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from tethys_portal.optional_dependencies import optional_import

from django.db import models

# optional imports
Workflow = optional_import("Workflow", from_module="condorpy")


class CondorPyWorkflow(models.Model):
    """
    Database model for condorpy workflows
    """

    condorpyworkflow_id = models.AutoField(primary_key=True)
    _max_jobs = models.JSONField(default=dict, null=True, blank=True)
    _config = models.CharField(max_length=1024, null=True, blank=True)

    @property
    def condorpy_workflow(self):
        """
        Returns: an instance of a condorpy Workflow
        """
        if not hasattr(self, "_condorpy_workflow"):
            workflow = Workflow(
                name=self.name.replace(" ", "_"),
                max_jobs=self.max_jobs,
                config=self.config,
                working_directory=self.workspace,
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
        if self.pk:  # verify that object has been saved before accessing node_set
            return self.node_set.select_subclasses()
        else:
            return []

    @property
    def num_jobs(self):
        return self.condorpy_workflow.num_jobs

    def load_nodes(self):
        workflow = self.condor_object

        # Skip if nodes are loaded already
        if len(workflow.node_set):
            return

        node_dict = dict()

        def add_node_to_dict(node):
            if node not in node_dict:
                node_dict[node] = node.condorpy_node

        for node in self.nodes:
            add_node_to_dict(node)
            condorpy_node = node_dict[node]
            condorpy_node.job._remote = workflow.scheduler
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
