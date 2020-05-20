.. _production_se_linux_config:

**********************
SE Linux Configuration
**********************

**Last Updated:** May 2020


17) Configure SELinux (CentOS, RedHat, Fedora)

    If your server is running Security Enhanced Linux, you will need to create a security policy for Tethys. This is typically the case on CentOS, RedHat, and Fedora systems. The following is what the installation script does to configure SELinux, but you should not rely on this for your own deployment without understanding what it is doing (see: `Security-Enhanced Linux <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_, `CentOS SELinux <https://wiki.centos.org/HowTos/SELinux>`_, `RedHat SELinux <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/deployment_guide/ch-selinux>`_). **USE AT YOUR OWN RISK**:

    .. code-block::

        sudo chown ${USER} <TETHYS_HOME>
        sudo yum install setroubleshoot -y
        sudo semanage fcontext -a -t httpd_config_t <TETHYS_HOME>/tethys_nginx.conf
        sudo restorecon -v <TETHYS_HOME>/tethys_nginx.conf
        sudo semanage fcontext -a -t httpd_sys_content_t "<TETHYS_HOME>(/.*)?"
        sudo semanage fcontext -a -t httpd_sys_content_t "<STATIC_ROOT>(/.*)?"
        sudo semanage fcontext -a -t httpd_sys_rw_content_t "<TETHYS_WORKSPACE_ROOT>(/.*)?"
        sudo restorecon -R -v <TETHYS_HOME> > /dev/null
        echo $'module tethys-selinux-policy 1.0;\nrequire {type httpd_t; type init_t; class unix_stream_socket connectto; }\n#============= httpd_t ==============\nallow httpd_t init_t:unix_stream_socket connectto;' > <TETHYS_HOME>/tethys-selinux-policy.te

        checkmodule -M -m -o <TETHYS_HOME>/tethys-selinux-policy.mod <TETHYS_HOME>/tethys-selinux-policy.te
        semodule_package -o <TETHYS_HOME>/tethys-selinux-policy.pp -m <TETHYS_HOME>/tethys-selinux-policy.mod
        sudo semodule -i <TETHYS_HOME>/tethys-selinux-policy.pp
        sudo chown <NGINX_USER> <TETHYS_HOME>