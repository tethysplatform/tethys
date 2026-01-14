.. _docker_primer:

*************
Docker Primer
*************

**Last Updated:** November 2021

This guide provides an overview of Docker and the key concepts needed to use it effectively. For more detailed descriptions of the concepts in this guide, please review the articles in the footnotes.

Shipping Analogy
================

Prior to the advent of the shipping container, shipping goods to different parts of the world was a logistical nightmare. Goods came in all different sizes of containers and arranging them on ships was haphazard. The same was true with trains and trucks when it came time to ship them overland. The result was shipping was expensive and slow and goods were often misplaced, broken, or rotted because of the delays.

The shipping container streamlined the shipping process because of its standard size. Merchants could put whatever they wanted in a shipping container. It didn't matter to the shipping companies if they were shipping bananas or cars. Loading the ship became a simple operation of stacking boxes and loading was reduced from days and weeks to hours. In addition containers could be easily transferred to trucks or trains for overland shipping.

.. raw:: html

    <iframe width="200" height="500" src="https://www.youtube.com/embed/DY9VE3i-KcM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Containers
==========

Like shipping containers, Docker containers have streamlined and standardized the way applications are deployed on the web. Docker describes a **container** as "a standard unit of software that packages up code and all its dependencies so the application runs quickly and reliably from one computing environment to another." [#f2]_ Containers leverage features of Linux that make them lighter weight than virtual machines. The applications inside containers are isolated from the server they are running on, which makes them more secure.

Container Images
================

Containers are running instances of **container images**, which are "lightweight, standalone, executable package of software that includes everything needed to run an application: code, runtime, system tools, system libraries and settings." [#f2]_ A container image is a read-only template or blueprint for a container. [#f3]_ Container images can be exported as archives (i.e. ``.tar``) and they can be easily transferred to a server for deployment.

Containers vs. Virtual Machines
===============================

Containers and virtual machines have some similar properties, however there are important differences in how they function that make containers more portable and efficient. The primary difference is that containers virtualize the operating system whereas virtual machines virtualize the hardware (see Figure 1). This means that containers share the core OS components (called the kernel), which makes them an order of magnitude smaller than virtual machines (container images are usually tens of MBs vs. virtual machine images that are tens of GBs). Any given server will be able to run many more containers than than virtual machines. [#f2]_

.. figure:: images/primer--containers-vs-vms.png
    :width: 800px
    :alt: Illustration of the difference between containers and virtual machines.

    **Figure 1**: Illustration of the difference between containers and virtual machines. [#f2]_

Dockerfile
==========

A **Dockerfile** is a text document that contains the instructions for building a container image. It can be thought of as a list of commands that a user would call on the commandline to install an application on a server. The Dockerfile spec includes instructions for running commands, adding files to the image, setting environment variables, and defining the command that should be run when the container starts. [#f4]_

Docker Deamon and Client
========================

The **Docker daemon** is the application that does the work of building container images and running containers from images. You interact with the Docker daemon using the **Docker client**, which is a commandline program. [#f5]_ When you run a command like ``docker build`` with the Docker client it passes the instruction to the Docker daemon, which performs the build operation. [#f3]_

Docker Registries
=================

A **Docker Registry** is a database for Docker images. The command ``docker pull`` is used to download images from registries and the command ``docker push`` is used to upload images to a registry. You can host your own registry [#f6]_, but most images are hosted on Docker Hub.

Docker Hub
==========

`Docker Hub <https://hub.docker.com/>`_ is a public Docker registry maintained by Docker. In fact, it is the default registry that the Docker daemon uses when you attempt to pull a container image. Docker Hub hosts over 100,000 container images, including official images for many Linux distributions (e.g.: `Debian <https://hub.docker.com/_/debian>`_, `Ubuntu <https://hub.docker.com/_/ubuntu>`_, and `CentOS <https://hub.docker.com/_/centos>`_)  and application components (e.g.: `PostgreSQL <https://hub.docker.com/_/postgres>`_, `NGINX <https://hub.docker.com/_/nginx>`_, and `Python <https://hub.docker.com/_/python>`_). Docker Hub can also be used to publish your own Docker images and it is free to do so for individuals, education, open source projects, and small businesses. [#f7]_

.. figure:: images/primer--docker-hub.png
    :width: 800px
    :alt: Screenshot of Docker Hub.

    **Figure 2**: Screenshot of Docker Hub.

.. rubric:: Footnotes

.. [#f2] See `What is a container? | Docker <https://www.docker.com/resources/what-container>`_
.. [#f3] See `Docker overview | Docker Documentation <https://docs.docker.com/get-started/docker-overview/>`_
.. [#f4] See `Dockerfile reference | Docker Documentation <https://docs.docker.com/reference/dockerfile/>`_
.. [#f5] See `Use the Docker command line | Docker Documentation <https://docs.docker.com/reference/cli/docker/>`_
.. [#f6] See `What is a registry | Docker Documentation <https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-registry/>`_
.. [#f7] See `Docker Pricing & Monthly Plan Details | Docker <https://www.docker.com/pricing>`_
