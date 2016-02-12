**************************
Tethys Compute Admin Pages
**************************
The Tethys Compute settings in site admin allows an administrator to manage computing clusters, oversee jobs, configure schedulers, and configure settings for computing resources.

* `Clusters`_
* `Jobs`_
* `Schedulers`_
* `Settings`_

.. figure:: ../images/tethys_compute/tethys_compute_admin.png
    :width: 700px
    :align: left

**Figure 1.** Dashboard for Tethys Compute admin pages.


Clusters
--------
A cluster is a group of virtual machines (VMs) that are configured with HTCondor so that they provided a distributed computing environment. Each cluster is made up of a master node and zero to many worker nodes. The master node is responsible for assigning jobs to the worker nodes based on their availability and capability. Tethys Platform uses a Python module called `TethysCluster <http://www.tethysplatform.org/TethysCluster/>`_ to provision and manage clusters using commercial clouds. TethysCluster enables provisioning clusters using either Amazon Web Services (AWS) or Microsoft Azure.

When creating a new cluster there are only two required settings: :ref:`cluster-name-label` and `size`_ ; and four options settings: `master image id`_, `master instance type`_, `node image id`_, and `node instance type`_.

.. figure:: ../images/tethys_compute/tethys_compute_clusters.png
    :width: 700px
    :align: left

**Figure 2.** Form for creating a new Cluster.

.. _cluster-name-label:

name
....
The name can be any string, but must be unique among all of the clusters for a given cloud account. Therefore, if the same account credentials are used for two separate instances of Tethys Portal then the the two Tethys Portals may not both have a cluster with the same name.

size
....
The size is the number of VMs the cluster will contain (including the master). The minimum is 1 and the maximum is determined by the limits on the cloud account being uses. The size may be changed after the cluster is created.

master image id
...............
The master image id refers to the image that the master node will be made from. When using AWS this would be the AMI ID (e.g. ami-38e4a750). When using Azure it is the name of the image (e.g. tc-ubuntu14). If left blank the master node will be created from the `node image id`_.

master instance type
....................
The master instance type refers to the VM type for the master node. For AWS this would be something like t2.small, m3.medium, etc. For Azure it would be Small, Large, A4, etc. If left blank then the master instance type will be the same as the `node instance type`_. For default values refer to the `Default Cluster`_ setting below.

node image id
.............
The node image id refers to the image that the worker nodes will be made from. When using AWS this would be the AMI ID (e.g. ami-38e4a750). When using Azure it is the name of the image (e.g. tc-ubuntu14). If left blank the image id specified in the `Default Cluster`_ template will be used.

node instance type
..................
The node instance type refers to the VM type for the worker nodes. For AWS this would be something like t2.small, m3.medium, etc. For Azure it would be Small, Large, A4, etc. If left blank then the default value specified by the `Default Cluster`_ template will be used.

------------

Jobs
----
Jobs represent some sort of computation that is sent from an app to a cluster using the :ref:`job-manager-label`. For each job that is created a database record is made to store some of the basic information about the job including: name, user, creation time, and status. The Jobs section in the Tethys Compute admin page allows for basic management of these database records. Jobs cannot be created in the admin pages, but they can be edited.

------------

.. _schedulers-label:


Schedulers
----------
Schedulers are HTCondor nodes that have scheduling rights in the pool they belong to. Schedulers are needed for CondorJob types (see :ref:`job-manager-label` documentation). When creating a new Scheduler there are two required settings: :ref:`scheduler-name-label` and `Host`_ ; an optional setting: `Username`_ ; and then two options for specifying authentication credentials: `Password`_ or `Private key path`_ and `Private key pass`_.

.. figure:: ../images/tethys_compute/tethys_compute_schedulers.png
    :width: 700px
    :align: left

**Figure 3.** Form for creating a new Scheduler.

.. _scheduler-name-label:

Name
....
A name to refer to the scheduler. Can be any string, but must be unique among schedulers.

Host
....
The fully qualified domain name (FQDN) or the IP address of the scheduler.

Username
........
The username that will be used to connect to the scheduler. The default username is 'root'.

Password
........
The password for the user specified by `Username`_ on the scheduler. Either a `Password`_ or a `Private key path`_ must be specified.

Private key path
................
The absolute path to the private key that is configured with the scheduler. Either a `Password`_ or a `Private key path`_ must be specified.

.. Note::
    The shortcut for the home directory: '~/' can be used and will be evaluated to the home directory of the Apache user.

Private key pass
................
The passphrase for the private key. If there is no passphrase then leave this field blank.

------------

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
This section contains general settings for clusters.

Scheduler IP
''''''''''''
The ip address or host name of the global HTCondor scheduler server. This should be one of the nodes in a cluster.

.. Note::
    This setting is deprecated. Use the `Schedulers`_ options to set up schedulers now.

Scheduler Key Location
''''''''''''''''''''''
The path to the private ssh key allowing passwordless ssh into the scheduler server. When a node in a cluster is used as the scheduler server then this will be the same as either the `Key Location`_ (for AWS) or the `Certificate Path`_ (for Azure).

.. Note::
    This setting is deprecated. Use the `Schedulers`_ options to set up schedulers now.


Default Cluster
'''''''''''''''
The template that will be used to create new clusters. This value also determines which cloud provider will be used to create clusters. Acceptable values are:

    * `azure_default_cluster`
    * `aws_default_cluster`

Azure Default Cluster
~~~~~~~~~~~~~~~~~~~~~
.. code::

    [cluster azure_default_cluster]
    CLOUD_PROVIDER = Azure
    CLUSTER_SIZE = 1
    CLUSTER_SHELL = bash
    NODE_IMAGE_ID = ami-3393a45a
    NODE_INSTANCE_TYPE = m3.medium

AWS Default Cluster
~~~~~~~~~~~~~~~~~~~
.. code::

    [cluster aws_default_cluster]
    CLOUD_PROVIDER = AWS
    CLUSTER_SIZE = 1
    CLUSTER_SHELL = bash
    NODE_IMAGE_ID = tc-linux12-2
    NODE_INSTANCE_TYPE = Small