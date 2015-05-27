*************************
Distributed Computing API
*************************

**Last Updated:** February 5, 2015

Distributed computing in Tethys is made possible with HTCondor (see installation documentation for instructions on installing HTCondor. Access to HTCondor tools is made possible through the condorpy module.  See the following code example for how to use condorpy:
::

    >>> from condorpy import Job, Templates
    >>> job = Job('job_name', Templates.vanilla_transfer_files)
    >>> job.executable = 'job_script'
    >>> jobs.arguments = 'input_1 input_2'
    >>> job.transfer_input_files = 'input_1 input_2'
    >>> job.transfer_output_files = 'output'
    >>> job.submit()