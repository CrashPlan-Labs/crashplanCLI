# Get started with theCrashPlancommand-line interface (CLI)

* [Licensing](#licensing)
* [Installation](#installation)
* [Authentication](#authentication)
* [Troubleshooting and Support](#troubleshooting-and-support)

## Licensing

This project uses the [MIT License](https://github.com/CrashPlan-Labs/crashplancli/blob/main/LICENSE.md).

## Installation

You can install the CrashPlan CLI from PyPI, from source, or from distribution.

### From PyPI

The easiest and most common way is to use `pip`:

```bash
python3 -m pip install crashplancli
```

To install a previous version of the CrashPlan CLI via `pip`, add the version number. For example, to install version
1.0.0, enter:

```bash
python3 -m pip install crashplancli==1.0.0
```

Visit the [project history](https://pypi.org/project/crashplancli/#history) on PyPI to see all published versions.

### From source

Alternatively, you can install the CrashPlan CLI directly from [source code](https://github.com/CrashPlan-Labs/crashplancli):

```bash
git clone https://github.com/CrashPlan-Labs/crashplancli.git
```

When it finishes downloading, from the root project directory, run:

```bash
python setup.py install
```

### From distribution

If you want create a `.tar` ball for installing elsewhere, run the following command from the project's root directory:

```bash
python setup.py sdist
```

After it finishes building, the `.tar` ball will be located in the newly created `dist` directory. To install it, enter:

```bash
python3 -m pip install crashplancli-[VERSION].tar.gz
```

## Updates

To update the CLI, use the pip `--upgrade` flag.

```bash
python3 -m pip install crashplancli --upgrade
```

## Authentication

```{eval-rst}
.. important:: The CrashPlan CLI currently only supports token-based authentication.
```

Create a user in CrashPlan to authenticate (basic authentication) and access data via the CLI. The CLI returns data based
on the roles assigned to this user. To ensure that the user's rights are not too permissive, create a user with the lowest
level of privilege necessary. See our [Role assignment use cases](https://support.crashplan.com/hc/en-us/articles/9112366299789-Roles-reference)
for information on recommended roles. We recommend you test to confirm that the user can access the right data.

If you choose not to store your password in the CLI, you must enter it for each command that requires a connection.

The CrashPlan CLI supports local accounts with MFA (multi-factor authentication) enabled. The Time-based One-Time
Password (TOTP) must be provided at every invocation of the CLI, either via the `--totp` option or when prompted.

The CrashPlan CLI currently does **not** support SSO login providers or any other identity providers such as Active
Directory or Okta.

## Proxy Support

```{eval-rst}
.. note:: Proxy support was added in crashplancli version 1.16.0
```

The CrashPlan CLI will attempt to connect through a proxy if the `https_proxy`/`HTTPS_PROXY` environment variable is set.

### Windows and Mac

For Windows and Mac systems, the CLI uses Keyring when storing passwords.

### Red Hat Enterprise Linux

To use Keyring to store the credentials you 2enter in the CrashPlan CLI, enter the following commands before installing.
```bash
yum -y install python-pip python3 dbus-python gnome-keyring libsecret dbus-x11
pip3 install crashplancli
```
If the following directories do not already exist, create them:
```bash
mkdir -p ~/.cache
mkdir -p ~/.local/share/keyring
```
In the following commands, replace the example value `\n` with the Keyring password (if the default Keyring already exists).
```bash
eval "$(dbus-launch --sh-syntax)"
eval "$(printf '\n' | gnome-keyring-daemon --unlock)"
eval "$(printf '\n' | /usr/bin/gnome-keyring-daemon --start)"
```
Close out your D-bus session and GNOME Keyring:
```bash
pkill gnome
pkill dbus
```
If you do not use Keyring to store your credentials, the CrashPlan CLI will ask permission to store your credentials in a local flat file with read/write permissions for only the operating system user who set the password. Alternatively, you can enter your password with each command you enter.

### Ubuntu
If Keyring doesn't support your Ubuntu system, the CrashPlan CLI will ask permission to store your credentials in a local flat file with read/write permissions for only the operating system user who set the password. Alternatively, you can enter your password with each command you enter.



To learn more about authenticating in the CLI, follow the [Configure profile guide](profile.md).

## Troubleshooting and support

### CrashPlan command not found

If your python installation has added itself to your environment's PATH variable, then running `crashplan` _should_ just work.

However, if after installation the `crashplan` command is not found, the CLI has some helpers for this (added in version 1.10):

You can execute the CLI by calling the python module directly:

```bash
python3 -m crashplancli
```

And the base `crashplan` command now has a `--script-dir` option that will print out the directory the `crashplan` script was
installed into, so you can manually add it to your PATH, enabling the `crashplan` command to work.

#### On Mac/Linux:

Run the following to make `crashplan` visible in your shell's PATH (to persist the change, add it to your shell's configuration file):

```bash
export PATH=$PATH:$(python3 -m crashplancli --script-dir)
```

#### On Windows:

```powershell
$env:Path += ";$(python -m crashplancli --script-dir)"
```

To persist the change, add the updated PATH to your registry:

```powershell
Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $env:Path
```

### Debug mode

Debug mode may be useful if you are trying to determine if you are experiencing permissions issues. When debug mode is
on, the CLI logs HTTP request data to the console. Use the `-d` flag to enable debug mode for a particular command.
`-d` can appear anywhere in the command chain:

```bash
crashplan <command> <subcommand> <args> -d
```

### File an issue on GitHub

If you are experiencing an issue with the CrashPlan CLI, select *New issue* at the
[project repository](https://github.com/CrashPlan-Labs/crashplancli/issues) to create an issue. See the Github
[guide on creating an issue](https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue) for more information.

### Contact CrashPlan Support

If you don't have a GitHub account and are experiencing issues, contact
[crashplan support](https://support.crashplan.com/).

## What's next?

Learn how to [Set up a profile](profile.md).
