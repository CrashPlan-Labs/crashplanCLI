# Configure profile

Use the [crashplan profile](../commands/profile.md) set of commands to establish the crashplan environment you're working
within and your user information.

## User token authentication

Use the following command to create your profile with user token authentication:
```bash
crashplan profile create --name MY_FIRST_PROFILE --server example.authority.com --username security.admin@example.com
```

Your profile contains the necessary properties for authenticating with crashplan. After running `crashplan profile create`,
the program prompts you about storing a password. If you agree, you are then prompted to enter your password.

Your password is not shown when you do `crashplan profile show`. However, `crashplan profile show` will confirm that a
password exists for your profile. If you do not set a password, you will be securely prompted to enter a password each
time you run a command.

## API client authentication

Once you've generated an API Client in your crashplan console, use the following command to create your profile with API client authentication:
```bash
crashplan profile create-api-client --name MY_API_CLIENT_PROFILE --server example.authority.com --api-client-id 'key-42' --secret 'crashplan%api%client%secret'
```

```{eval-rst}
.. note:: Remember to wrap your API client secret with single quotes to avoid issues with bash expansion and special characters.
```

## View profiles

You can add multiple profiles with different names and the change the default profile with the `use` command:

```bash
crashplan profile use MY_SECOND_PROFILE
```

When you use the `--profile` flag with other commands, such as those in `audit-logs`, that profile is used
instead of the default profile. For example,

```bash
crashplan audit-logs search -b 2020-02-02 --profile MY_SECOND_PROFILE
```

To see all your profiles, do:

```bash
crashplan profile list
```

## Profiles with Multi-Factor Authentication

If your crashplan user account requires multi-factor authentication, the MFA token can either be passed in with the `--totp`
option, or if not passed you will be prompted to enter it before the command executes.
