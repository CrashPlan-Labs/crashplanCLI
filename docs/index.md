# CrashPlan command-line interface (CLI)

```{eval-rst}
.. toctree::
    :hidden:
    :maxdepth: 2

    guides
```

```{eval-rst}
.. toctree::
    :hidden:
    :maxdepth: 2

    commands
```

[![license](https://img.shields.io/pypi/l/crashplancli.svg)](https://pypi.org/project/crashplancli/)
[![versions](https://img.shields.io/pypi/pyversions/crashplancli.svg)](https://pypi.org/project/crashplancli/)

The CrashPlan command-line interface (CLI) tool offers a way to interact with your CrashPlan environment without using the
CrashPlan console or making API calls directly. For example, you can use it to extract CrashPlan audit log data or to manage users, devices, and legal holds.

## Requirements
To use the CrashPlan CLI, you must have:

* A [CrashPlan product plan](https://support.crashplan.com/hc/en-us/articles/9802774807821-CrashPlan-product-plans) that supports the feature or functionality for your use case
* Python version 3.11 and later installed

## Content

* [User Guides](guides.md)
    * [Get started with the CrashPlan command-line interface (CLI)](userguides/gettingstarted.md)
    * [Configure a profile](userguides/profile.md)
    * [Manage legal hold users](userguides/legalhold.md)
    * [Clean up your environment by deactivating devices](userguides/deactivatedevices.md)
    * [Manage users](userguides/users.md)
    * [Perform bulk actions](userguides/bulkcommands.md)
    * [Send audit logs to a SIEM](userguides/siemexample.md)
    * [Write custom extension scripts using the CrashPlan CLI and Pycpg](userguides/extensions.md)
* [Commands](commands.md)
    * [Audit Logs](commands/auditlogs.rst)
    * [Devices](commands/devices.rst)
    * [Legal Hold](commands/legalhold.rst)
    * [Profile](commands/profile.rst)
    * [Users](commands/users.rst)
