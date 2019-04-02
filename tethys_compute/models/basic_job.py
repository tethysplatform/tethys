"""
********************************************************************************
* Name: basic_job
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
from tethys_compute.models.tethys_job import TethysJob


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
