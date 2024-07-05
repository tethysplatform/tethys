"""
********************************************************************************
* Name: scheduler
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import logging
from django.db import models
from tethys_compute.models.scheduler import Scheduler
from tethys_compute.models.dask.dask_job_exception import DaskJobException
from tethys_portal.optional_dependencies import optional_import

# optional imports
Client = optional_import("Client", from_module="dask.distributed")

log = logging.getLogger("tethys." + __name__)


class DaskScheduler(Scheduler):
    """
    Scheduler for Dask jobs.
    """

    timeout = models.IntegerField(blank=True, default=0)
    heartbeat_interval = models.IntegerField(blank=True, default=0)
    dashboard = models.CharField(max_length=255, blank=True, null=True)

    @property
    def client(self):
        """
        Get the Client associated with this job. The Client connects users to a dask.distributed compute cluster. It provides an asynchronous user interface around functions and futures.

        Returns:
            dask.distributed.Client: Client initialized with Scheduler configuration if defined, otherwise bound locally.
        """  # noqa: #501
        if not getattr(self, "_client", None):
            if self.heartbeat_interval == 0:
                heartbeat_interval = None
            else:
                heartbeat_interval = self.heartbeat_interval

            if self.timeout == 0:
                timeout = "__no_default__"
            else:
                timeout = self.timeout

            try:
                # validating the invalid scheduler
                client = Client(
                    address=self.host,
                    heartbeat_interval=heartbeat_interval,
                    timeout=timeout,
                )

            except Exception:
                log.exception("Dask Client Init Error")
                raise DaskJobException("Invalid scheduler is provided")

            self._client = client

        return self._client

    class Meta:
        verbose_name = "Dask Scheduler"
        verbose_name_plural = "Dask Schedulers"
