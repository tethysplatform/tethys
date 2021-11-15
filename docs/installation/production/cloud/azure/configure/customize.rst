.. _azure_vm_config_customize:

*************************************
Customize Tethys Portal (Recommended)
*************************************

**Last Updated:** Nov 2021

Customize the theme and content of the Tethys Portal to reflect your organization brand and theme guidelines. Follow the :ref:`Customize Portal Theme <production_customize_theme>` configuration guide to learn how to do this.

Custom images, CSS, and JavaScript should be added to a new directory in the :file:`$TETHYS_HOME/static` directory (e.g.: :file:`$TETHYS_HOME/static/custom_theme`. These can then be referenced in the settings via the name of the new directory (e.g.: :file:`custom_theme/images/custom_logo.png`.

.. figure:: ../../../../../images/production/azure/configure--custom-theme.png
    :width: 800px
    :alt: Tethys Portal with a custom theme.

    **Figure 1.** Tethys Portal with a custom theme.