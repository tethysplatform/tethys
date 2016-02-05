**************************
Tethys Compute Admin Pages
**************************
The Tethys Compute settings in site admin allows an administrator to manage computing clusters, oversee jobs, configure schedulers, and configure settings for computing resources.

* `Clusters`_
* `Jobs`_
* `Schedulers`_
* `Settings`_

.. figure:: ../images/tethys_compute/tethys_compute_admin.png
    :width: 600px
    :align: left

**Figure 1.** Dashboard for Tethys Compute admin pages.


Clusters
--------
A cluster is a group of virtual machines (VMs) that are configured with HTCondor so that they provided a distributed computing environment. Each cluster is made up of a master node and zero to many worker nodes. The master node is responsible for assigning jobs to the worker nodes based on their availability and capability. Tethys Platform uses a Python module called `TethysCluster <http://www.tethysplatform.org/TethysCluster/>`_ to provision and manage clusters using commercial clouds. TethysCluster enables provisioning clusters using either Amazon Web Services (AWS) or Microsoft Azure.

When creating a new cluster there are only two required settings: 'name' and 'size'. The name must be unique among all of the clusters for a given cloud account. Therefore, if the same account credentials are used for two separate instances of Tethys Portal then the the two Tethys Portals may not both have a cluster with the same name. The size is the number of VMs the cluster will contain. The size may be changed after the cluster is created.

There are four optional options when creating a cluster: 'master image id',' master instance type', 'node image id', and 'node instance type'. The master image id and node image id refer to the image that the master node and the worker nodes, respectively, will be made from. When using AWS this would be the AMI ID (e.g. ami-38e4a750). When using Azure it is the name of the image (e.g. tc-ubuntu14). The master instance type and node instance type refer to the type of VM for the master and worker nodes respectively. For AWS this would be something like t2.small, m3.medium, etc. For Azure it would be Small, Large, A4, etc. If the master image id and master instance type are not specified then the master node will be the same as the worker nodes. For default values refer to the `Default Cluster`_ setting below.

Jobs
----
Jobs represent some sort of computation that is sent from an app to a cluster using the :ref:`job-manager-label`. For each job that is created a database record is made to store some of the basic information about the job including: name, user, creation time, and status. The Jobs section in the Tethys Compute admin page allows for basic management of these database records.

.. _schedulers-label:

Schedulers
----------
Schedulers are HTCondor nodes that have scheduling rights in the pool they belong to. Schedulers are needed for CondorJob types (see :ref:`job-manager-label` documentation).

Settings
--------
Tethys Compute settings are divided into three sections: `Azure Credentials`_, `Amazon Credentials`_, and `Cluster Management`_. The Azure and Amazon Credentials sections are used to store the cloud account credentials that will be used by Tethys Portal to create clusters. Both Azure and Amazon credentials may be added, however, Tethys Portal is only capable of using one cloud provider at a time. The cloud provider that will be used is determined by the `Default Cluster`_ setting in the `Cluster Management`_ section. In addition to the `Default Cluster`_ setting the `Cluster Management`_ section also holds settings for the scheduler server.

Azure Credentials
.................
This section contains settings for connecting to an Azure account. There are two required settings: `Subscription ID`_ and `Certificate Path`_.

Subscription ID
'''''''''''''''
The `Subscription ID`_ is a unique identifier for your Azure subscription. For instructions on how to find your subscription id see this `video <https://www.youtube.com/watch?v=VNoGnxvTLDQ>`_.

Certificate Path
''''''''''''''''
The `Certificate Path`_ is the path to an SSL certificate file on the Tethys Portal server that is also registered in with your Azure subscription. View these `instructions <https://msdn.microsoft.com/en-us/library/azure/gg551722.aspx>`__ for help creating and uploading a certificate to the Microsoft Azure Management Portal.

Amazon Credentials
..................
This section contains settings for connecting to an Amazon Web Services (AWS) account.

AWS Access Key ID
'''''''''''''''''
The `AWS Access Key ID`_ is a unique id for your IAM user. View these `instructions <http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html>`__ for getting your Access Key ID and Secret Access Key.

AWS Secret Access Key
'''''''''''''''''''''
The `AWS Secret Access Key`_ is like a password for the AWS account. It is associated with your Access Key ID, but is not viewable through the AWS Management Console. They only time a Secret Access Key can be retrieved is when it is created. View these `instructions <http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html>`_ for getting your Access Key ID and Secret Access Key.

AWS User ID
'''''''''''
The `AWS User ID`_ is a unique 12-digit number that identifies the AWS account. This is different from the `AWS Access Key ID`_ which is associated with a specific IAM user within an AWS account.

Key Name
''''''''
The `Key Name`_ is the name of an SSH key pair that is uploaded to your AWS account. For more information see `Amazon EC2 Key Pairs <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html>`_.

Key Location
''''''''''''
The `Key Location`_ is the path to the SSH private key on the Tethys Portal server. For more information see `Amazon EC2 Key Pairs <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html>`_.

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