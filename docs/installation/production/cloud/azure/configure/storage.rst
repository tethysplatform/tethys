.. _azure_vm_config_storage:

*********************************
Add Additional Storage (Optional)
*********************************

**Last Updated:** November 2021

The storage allocated to your VM by default will likely not be sufficient for data-intensive apps. This tutorial will guide you through the process of attaching additional storage to the VM and configuring Tethys Platform to use it.

1. Attach Additional Storage
============================

Add additional storage to the VM as follows:

1. Navigate to the Overview page for the VM Resource.
2. From the navigation menu on the left, select **Disks**.
3. Press the **Create and attach a new disk** button under the **Data disks** section.
4. Fill out the options in the new row that appears as follows:

    * **LUN**: Logical Unit Number, a unique ID for the disk.
    * **Disk name**: Give the disk a name (e.g. my-first-tethys-storage-0).
    * **Storage type**: Choose the storage type. Standard SSD is ok for most Tethys Servers.
    * **Size**: Specify the size in GibiBytes (see: `Gibibyte | Wikipedia <https://simple.m.wikipedia.org/wiki/Gibibyte>`_).
    * **Encryption**: Choose the encryption method for the disk. See the info note in the column header for more details.
    * **Host caching**: Choose host caching option (not required, but may boost performance).

5. Press the **Save** button at the top of the page when done.

2. Format Disk
==============

After attaching the storage to the virtual machine, you will need to format it and add a file system to it:

1. Login to the VM using SSH (see: :ref:`Orientation to Azure VM | Connect with SSH <azure_vm_orientation_ssh>`).
2. Run `lsblk <https://man7.org/linux/man-pages/man8/lsblk.8.html>`_ to list all storage devices:

    .. code-block::

        lsblk

    This will result in a printout of the storage devices like this:

    .. code-block::
        :emphasize-lines: 14

        NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
        loop0     7:0    0 61.8M  1 loop /snap/core20/1081
        loop1     7:1    0 61.9M  1 loop /snap/core20/1169
        loop2     7:2    0 32.4M  1 loop /snap/snapd/13270
        loop3     7:3    0 67.2M  1 loop /snap/lxd/21803
        loop4     7:4    0 67.2M  1 loop /snap/lxd/21835
        loop5     7:5    0 32.5M  1 loop /snap/snapd/13640
        sda       8:0    0   30G  0 disk
        ├─sda1    8:1    0 29.9G  0 part /
        ├─sda14   8:14   0    4M  0 part
        └─sda15   8:15   0  106M  0 part /boot/efi
        sdb       8:16   0   20G  0 disk
        └─sdb1    8:17   0   20G  0 part /mnt
        sdc       8:32   0  100G  0 disk

    The disk with the operating system installed on it is the one with the root directory (``/``) as the mountpoint (**sda1** in this case). The name of the new disk that we attached to the VM is **sdc**, which was determined by the size and the fact that it has no mount point.

3. Use `fdisk <https://man7.org/linux/man-pages/man8/fdisk.8.html>`_ to create a partition on the disk as follows:

    1. Run the ``fdisk`` with the path to the new disk.

        .. code-block::

            sudo fdisk /dev/<new_disk_name>


        For example, the new disk in the example above is named ``sdc`` so the command would be as follows:

        .. code-block::

            # Heads up! This is an example!
            sudo fdisk /dev/sdc

    2. Enter ``g`` to create a new partition table:

        .. code-block::

            Command (m for help): g
            Created a new GPT disklabel (GUID: 83C2F8FE-4D08-A24B-B18D-B39F90DC9ED1).

    3. Enter ``n`` to create a new partition and accept the default values for the three prompts that follow (i.e. leave blank):

        .. code-block::

            Command (m for help): n
            Partition number (1-128, default 1):
            First sector (2048-209715166, default 2048):
            Last sector, +/-sectors or +/-size{K,M,G,T,P} (2048-209715166, default 209715166):

            Created a new partition 1 of type 'Linux filesystem' and of size 100 GiB.

    4. Enter ``w`` to apply the changes you specified above. Alternatively, if you need to start over, enter ``q`` to exit without applying the changes.

        .. code-block::

            Command (m for help): w
            The partition table has been altered.
            Calling ioctl() to re-read partition table.
            Syncing disks.

    5. Run ``lsblk`` again to confirm the partition was created and that it is the full size of the disk. In the case below, the partition ``sdc1`` is now listed under ``sdc``:

        .. code-block::
            :emphasize-lines: 15

            NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
            loop0     7:0    0 61.8M  1 loop /snap/core20/1081
            loop1     7:1    0 61.9M  1 loop /snap/core20/1169
            loop2     7:2    0 32.4M  1 loop /snap/snapd/13270
            loop3     7:3    0 67.2M  1 loop /snap/lxd/21803
            loop4     7:4    0 67.2M  1 loop /snap/lxd/21835
            loop5     7:5    0 32.5M  1 loop /snap/snapd/13640
            sda       8:0    0   30G  0 disk
            ├─sda1    8:1    0 29.9G  0 part /
            ├─sda14   8:14   0    4M  0 part
            └─sda15   8:15   0  106M  0 part /boot/efi
            sdb       8:16   0   20G  0 disk
            └─sdb1    8:17   0   20G  0 part /mnt
            sdc       8:32   0  100G  0 disk
            └─sdc1    8:33   0  100G  0 part

    6. Create a file system on the new partition using the `mkfs <https://man7.org/linux/man-pages/man8/mkfs.8.html>`_ command:

        .. code-block::

            sudo mkfs -t ext4 -j -L <volume_label> /dev/<new_partition_name>

        For example, the new partition in the example above is named ``sdc1`` so the command would be:

        .. code-block::

            # Heads up! This is an example!
            sudo mkfs -t ext4 -j -L mydisk /dev/sdc1

        The ``-L`` option lets you specify a label for the file system that will be used in the next step. The maximum length of the label is 16 ASCII characters. ``ext4`` is the type of filesystem that is created on the disk and is the standard file system for Linux.


3. Mount Disk
=============

Now that the disk has been formatted with a Linux filesystem, it can be mounted as follows:

1. Create a directory where you intend the new disk to be mounted.

    .. code-block::

        sudo mkdir <mount_directory>

    Continuing our example, this would be:

    .. code-block::

        # Heads up! This is an example!
        sudo mkdir /mydisk

2. To manually mount the disk, use the `mount <https://man7.org/linux/man-pages/man8/mount.8.html>`_ command, specifying the new partition, and the mount directory (mountpoint).

    .. code-block::

        sudo mount /dev/<partition_name> <mount_directory>

    where ``<partition_name>`` is the name of the new partition and ``<mount_directory>`` is the directory that you want to mount it to. In the example this would be:

    .. code-block::

        # Heads up! This is an example!
        sudo mount /dev/sdc1 /mydisk

3. Run ``lsblk`` one more time to verify that the new partition has a mountpoint now. In the example above, ``sdc1`` now lists ``/mydisk`` as the mountpoint:

    .. code-block::
        :emphasize-lines: 15

        NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
        loop0     7:0    0 61.8M  1 loop /snap/core20/1081
        loop1     7:1    0 61.9M  1 loop /snap/core20/1169
        loop2     7:2    0 32.4M  1 loop /snap/snapd/13270
        loop3     7:3    0 67.2M  1 loop /snap/lxd/21803
        loop4     7:4    0 67.2M  1 loop /snap/lxd/21835
        loop5     7:5    0 32.5M  1 loop /snap/snapd/13640
        sda       8:0    0   30G  0 disk
        ├─sda1    8:1    0 29.9G  0 part /
        ├─sda14   8:14   0    4M  0 part
        └─sda15   8:15   0  106M  0 part /boot/efi
        sdb       8:16   0   20G  0 disk
        └─sdb1    8:17   0   20G  0 part /mnt
        sdc       8:32   0  100G  0 disk
        └─sdc1    8:33   0  100G  0 part /mydisk

4. You can now change into the mountpoint directory like any other directory. Any files written within that directory will be written to the new disk. For example:

    .. code-block::

        cd /mydisk
        ls -al
        total 24
        drwxr-xr-x 3 root root  4096 Nov 15 20:26 .
        drwxr-xr-x 4 root root  4096 Nov 15 20:42 ..
        drwx------ 2 root root 16384 Nov 15 20:26 lost+found

5. Everything is owned by root at the moment. Change ownership of the <mount_directory> to be owned by your user account:

    .. code-block::

        sudo chown -R ${USER} <mount_directory>

    For the example this would be:

    .. code-block::

        # Heads up! This is example code
        sudo chown -R ${USER} /mydisk

4. Configure Automount
======================

This step will describe how to configure the VM to automatically mount the new disk if the server is restarted:

1. Open :file:`/etc/fstab` in your favorite text editor (e.g. vim, nano):

    .. code-block::

        sudo vim /etc/fstab

2. Add a new line to the file as follows:

    .. code-block::

        LABEL=<volume_label> <mount_directory> ext4 defaults,rw 0 2

    where ``<volume_label>`` is the label you assigned when creating the file system and ``<mount_directory>`` is the directory that you mounted it to.

    For example:

    .. code-block::

        LABEL=mydisk /mydisk ext4 defaults,rw 0 2

    .. important::

        Each item in the ``fstab`` file must be separated by **exactly** one space or tab character. The options (i.e.: ``defaults,rw``) should be separated by commas and **no spaces**. For more details on the ``fstab`` file and the options see: `Fstab <https://help.ubuntu.com/community/Fstab>`_.

3. Exit SSH

    .. code-block::

        exit

4. Restart the VM using the control on the Overview page for the Virtual Machine resource, then login again after the machine starts.

5. Use the `df <https://man7.org/linux/man-pages/man1/df.1.html>`_ command to view disk space usage and confirm that the new disk was automatically mounted:

    .. code-block::

        df -h

    which should yield something like this:

    .. code-block::
        :emphasize-lines: 15

        Filesystem      Size  Used Avail Use% Mounted on
        /dev/root        29G   13G   17G  44% /
        devtmpfs        2.0G     0  2.0G   0% /dev
        tmpfs           2.0G   44K  2.0G   1% /dev/shm
        tmpfs           394M  1.2M  393M   1% /run
        tmpfs           5.0M     0  5.0M   0% /run/lock
        tmpfs           2.0G     0  2.0G   0% /sys/fs/cgroup
        /dev/loop0       62M   62M     0 100% /snap/core20/1169
        /dev/loop2       68M   68M     0 100% /snap/lxd/21803
        /dev/loop1       62M   62M     0 100% /snap/core20/1081
        /dev/loop3       68M   68M     0 100% /snap/lxd/21835
        /dev/loop5       33M   33M     0 100% /snap/snapd/13640
        /dev/loop4       33M   33M     0 100% /snap/snapd/13270
        /dev/sda15      105M  5.2M  100M   5% /boot/efi
        /dev/sdc1        98G   61M   93G   1% /mydisk
        /dev/sdb1        20G   45M   19G   1% /mnt
        tmpfs           394M     0  394M   0% /run/user/1002


5. Configure Tethys
===================

Now that the new disk has been formatted and will automatically mount when the system boots, Tethys needs to be configured to use it. This includes updating the Tethys config to use the new storage for app workspaces and configuring GeoServer, THREDDS, and any other data services to use a data directory on the drive.

Tethys Workspaces
-----------------


THREDDS
-------


GeoServer
---------
