********************
Terminal Quick Guide
********************

**Last Updated:** November 18, 2014

To install and use Tethys Platform, you will need to be familiar with using the command line/terminal. This guide provides tips and explanations of the most common features of command line that you will need to know to work with Tethys. For a more exhaustive reference, please review this excellent tutorial: `Learn the Bash Command Line <https://ryanstutorials.net/linuxtutorial/>`_.

$
*

The "$" in code blocks means "run this in the terminal". This is usually done by typing the command or copying and pasting it into the terminal. When copying, don't copy the "$". Copy lines one at a time and press :kbd:`enter` after each one to execute it. Note that some commands may prompt you for input.

~
*

The "~" is short hand for your :file:`Home` directory. You will see this symbol most often in paths that extend from your :file:`Home` directory. The shorthand is used because the path to the :file:`Home` directory varies depending on your user name. For example, if your user name was "john", then the absolute path to your home directory would be something like :file:`/home/john`.

sudo
****

Some operations on the commandline require authorization by a superuser or administrator. The ``sudo`` command is used to grant permission. This is done by prepending any command with ``sudo``. You will be prompted for your password before you can continue.

::

    sudo apt-get moo

.. note::

   When you type passwords into the command line, the characters are not printed to the screen for security reasons. This can be unsettling, but type with faith and press enter.

cd
**

This command is used to change working directories on the command line. This is the equivalent of moving in and out of folders on a file browser.

mkdir
*****

This command is used to make new directories.

chown
*****

This command is used to change the owner of files or directories.


Copy and Paste
**************

The keyboard shortcuts :kbd:`CTRL-C` and :kbd:`CTRL-V` do not do preform copy and paste in the terminal. Instead, use the shortcuts :kbd:`CTRL-SHIFT-C` and :kbd:`CTRL-SHIFT-V` to copy and paste.