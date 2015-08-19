*************************
Distributed Computing API
*************************

**Last Updated:** May 26, 2015

Distributed computing in Tethys Platform is made possible with HTCondor. HTCondor computing resources are managed through the `Tethys Compute`_ settings of the site admin in Tethys Portal. Access to the HTCondor computing environment is made possible to app developers through a `Job Manager`_ object. For more information on HTCondor see `Overview of HTCondor <http://condorpy.readthedocs.org/en/latest/htcondor.html>`_ or the `HTCondor User Manual <http://research.cs.wisc.edu/htcondor/manual/>`_.

Tethys Compute
==============
The Tethys Compute settings in site admin allows an administrator to manage computing clusters, configure schedulers, oversee jobs, and configure settings for computing resources.

(add screenshot of settings?)

Clusters
--------
A cluster is a group of virtual machines (VMs) that are configured with HTCondor so that they provided a distributed computing environment. Each cluster is made up of a master node and zero to many worker nodes. The master node is responsible for assigning jobs to the worker nodes based on their availability and capability. Tethys Platform uses a Python module called `TethysCluster <http://ci-water.github.io/TethysCluster/>`_ to provision and manage clusters using commercial clouds. TethysCluster enables provisioning clusters using either Amazon Web Services (AWS) or Microsoft Azure.

When creating a new cluster there are only two required settings: 'name' and 'size'. The name must be unique among all of the clusters for a given cloud account. Therefore, if the same account credentials are used for two separate instances of Tethys Portal then the the two Tethys Portals may not both have a cluster with the same name. The size is the number of VMs the cluster will contain. The size may be changed after the cluster is created.

There are four optional options when creating a cluster: 'master image id',' master instance type', 'node image id', and 'node instance type'. The master image id and node image id refer to the image that the master node and the worker nodes, respectively, will be made from. When using AWS this would be the AMI ID (e.g. ami-38e4a750). When using Azure it is the name of the image (e.g. tc-ubuntu14). The master instance type and node instance type refer to the type of VM for the master and worker nodes respectively. For AWS this would be something like t2.small, m3.medium, etc. For Azure it would be Small, Large, A4, etc. If the master image id and master instance type are not specified then the master node will be the same as the worker nodes. For default values refer to the `Default Cluster`_ setting below.

Jobs
----
Jobs represent some sort of computation that is sent from an app to a cluster using the `Job Manager`_. For each job that is created a database entry is made to store some of the basic information about the job including: name, user, creation time, and status. The Jobs section in Tethys Compute allows for basic management of these database entries.


Settings
--------
Tethys Compute settings are divided into three sections: `Azure Credentials`_, `Amazon Credentials`_, and `Cluster Management`_. The Azure and Amazon Credentials sections are used to store the cloud account credentials that will be used by Tethys Portal to create clusters. Both Azure and Amazon credentials may be added, however, Tethys Portal is only capable of using one cloud provider at a time. The cloud provider that will be used is determined by the `Default Cluster`_ setting in the `Cluster Management`_ section. In addition to the `Default Cluster`_ setting the `Cluster Management`_ section also holds settings for the scheduler server.

Azure Credentials
.................

Subscription ID
'''''''''''''''

Certificate Path
''''''''''''''''


Amazon Credentials
..................

AWS Access Key ID
'''''''''''''''''

AWS Secret Access Key
'''''''''''''''''''''

AWS User ID
'''''''''''

Key Name
''''''''

Key Location
''''''''''''

Cluster Management
..................
This section contains settings for

Scheduler IP
''''''''''''
The ip address or host name of the HTCondor scheduler server. This should be one of the nodes in a cluster.

Scheduler Key Location
''''''''''''''''''''''
The path to the private ssh key allowing passwordless ssh into the scheduler server. When a node in a cluster is used as the scheduler server then this will be the same as either the `Key Location`_ (for AWS) or the `Certificate Path`_ (for Azure).

Default Cluster
'''''''''''''''









Job Manager
===========


Configuring the Job Manager
---------------------------


Using the Job Manager in your App
---------------------------------
