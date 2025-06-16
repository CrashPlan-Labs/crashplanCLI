# CrashPlan CLI

![Build status](https://github.com/CrashPlan-Labs/crashplancli/workflows/build/badge.svg)
[![codecov.io](https://codecov.io/github/crashplan/crashplancli/coverage.svg?branch=main)](https://codecov.io/github/crashplan/crashplancli?branch=master)
[![versions](https://img.shields.io/pypi/pyversions/crashplancli.svg)](https://pypi.org/project/crashplancli/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/crashplancli/badge/?version=latest)](https://clidocs.crashplan.com/en/latest/?badge=latest)

Use the `crashplan` command to interact with your CrashPlan environment.

## Requirements

- Python 3.11+

## Installation

Install the `crashplan` CLI using:

```bash
$ python3 -m pip install crashplancli
```

## Usage

First, create your profile:
```bash
crashplan profile create --name MY_FIRST_PROFILE --server example.authority.com --username security.admin@example.com
```

Your profile contains the necessary properties for logging into CrashPlan servers. After running `crashplan profile create`,
the program prompts you about storing a password. If you agree, you are then prompted to input your password.

Your password is not shown when you do `crashplan profile show`. However, `crashplan profile show` will confirm that a
password exists for your profile. If you do not set a password, you will be securely prompted to enter a password each
time you run a command.

For development purposes, you may need to ignore ssl errors. If you need to do this, use the `--disable-ssl-errors`
option when creating your profile:

```bash
crashplan profile create -n MY_FIRST_PROFILE -s https://example.authority.com -u security.admin@example.com --disable-ssl-errors
```

You can add multiple profiles with different names and the change the default profile with the `use` command:

```bash
crashplan profile use MY_SECOND_PROFILE
```

When the `--profile` flag is available on other commands, such as those in `audit-log`, it will use that profile
instead of the default one. For example,

```bash
crashplan audit-logs search -b 2025-06-01 --profile MY_SECOND_PROFILE
```

To see all your profiles, do:

```bash
crashplan profile list
```

Begin date will be ignored if provided on subsequent queries using `-c/--use-checkpoint`.

Use other formats with `-f`:

```bash
crashplan audit-logs search -b 2025-06-01 -f JSON
```

The available formats are TABLE,CSV,JSON, and RAW-JSON.

To write events to a file, just redirect your output:

```bash
crashplan audit-logs search -b 2025-06-01  > filename.txt
```

To send events to an external server, use the `send-to` command, which behaves the same as `search` except for defaulting
to `RAW-JSON` output and sending results to an external server instead of to stdout:

The default port (if none is specified on the address) is the standard syslog port 514, and default protocol is UDP:

```bash
crashplan audit-logs send-to 10.10.10.42 -b 1d
```

Results can also be sent over TCP to any port by using the `-p/--protocol` flag and adding a port to the address argument:

```bash
crashplan audit-logs send-to 10.10.10.42:8080 -p TCP -b 1d
```

Note: For more complex requirements when sending to an external server (SSL, special formatting, etc.), use a dedicated
syslog forwarding tool like `rsyslog` or connection tunneling tool like `stunnel`.

If you want to periodically run the same query, but only retrieve the new events each time, use the
`-c/--use-checkpoint` option with a name for your checkpoint. This stores the timestamp of the query's last event to a
file on disk and uses that as the "begin date" timestamp filter on the next query that uses the same checkpoint name.
Checkpoints are stored per profile.

Initial run requires a begin date:
```bash
crashplan audit-logs search -b 30d --use-checkpoint my_checkpoint
```

Subsequent runs do not:
```bash
crashplan audit-logs search --use-checkpoint my_checkpoint
```

You can also use wildcard for queries, but note, if they are not in quotes, you may get unexpected behavior.

```bash
crashplan audit-logs search --actor "*"
```

The search query parameters are as follows:

- `--affected-username` (Filter results by affected usernames.)
- `--affected-user-id` ( Filter results by affected user IDs.)
- `--actor-ip` (Filter results by user IP addresses.)
- `--actor-user-id` (Filter results by actor user IDs.)
- `--actor-username` (Filter results by actor usernames.)
- `--event-type` (Filter results by event types.)

To learn more about acceptable arguments, add the `-h` flag to `crashplan audit-logs`

## Troubleshooting

If you keep getting prompted for your password, try resetting with `crashplan profile reset-pw`.
If that doesn't work, delete your credentials file located at ~/.crashplancli or the entry in keychain.

## Shell tab completion

To enable shell autocomplete when you hit `tab` after the first few characters of a command name, do the following:

For Bash, add this to ~/.bashrc:

```
eval "$(_crashplan_COMPLETE=source_bash crashplan)"
```

For Zsh, add this to ~/.zshrc:

```
eval "$(_crashplan_COMPLETE=source_zsh crashplan)"
```

For Fish, add this to ~/.config/fish/completions/crashplan.fish:

```
eval (env _crashplan_COMPLETE=source_fish crashplan)
```

Open a new shell to enable completion. Or run the eval command directly in your current shell to enable it temporarily.


## Writing Extensions

The CLI exposes a few helpers for writing custom extension scripts powered by the CLI. Read the user-guide [here](https://clidocs.crashplan.com/en/feature-extension_scripts/userguides/extensions.html).
