# Manage legal hold custodians

Once you [create a legal hold matter in the CrashPlan console](https://support.crashplan.com/hc/en-us/articles/8603769878157-Create-a-legal-hold-matter), you can use the CrashPlan CLI to add or release custodians from the matter.

To see a list of all the users currently in your organization:
- Export a list from the [Users action menu](https://support.crashplan.com/hc/en-us/articles/9218711102989--Users-reference#01GD3GQS4DA14X4JGVV0SPC7YA).
- Use the [CLI users commands](./users.md).

Use the `legal-hold` commands to manage legal hold custodians.
 - To view a list of legal hold matters for your organization, including the matter ID, use the following command:
   `crashplan legal-hold list`
 - To see a list of all the custodians currently associated with a legal hold matter, enter `crashplan legal-hold show <matterID>`.


## Get CSV template

To add multiple custodians to a legal hold matter:

1. Generate a CSV template. Below is an example command that generates a template to use when bulk adding custodians to legal hold matter. Once generated, the CSV file is saved to your current working directory.

    ```bash
    crashplan legal-hold bulk generate-template add
    ```

    To generate a template to use when bulk releasing custodians from a legal hold matter:

    ```bash
    crashplan legal-hold bulk generate-template remove
    ```

    The CSV templates for `add` and `remove` have the same columns, but the commands generate different default filenames.

2. Use the CSV template to enter the matter ID(s) and CrashPlan usernames for the custodians you want to add to the matters.
To get the ID for a matter, enter `crashplan legal-hold list`.
3. Save the CSV file.

## Add custodians to a legal hold matter

You can add one or more custodians to a legal hold matter using the CrashPlan CLI.

### Add multiple custodians
Once you have entered the matter ID and user information in the CSV file, use the `bulk add` command with the CSV file path to add multiple custodians at once. For example:

 ```bash
    crashplan legal-hold bulk add /Users/admin/add_users_to_legal_hold.csv
    ```

### Add a single custodian

To add a single custodian to a legal hold matter, use the following command as an example:

 ```bash
    crashplan legal-hold add-user --matter-id 123456789123456789 --username user@example.com
    ```

#### Options

 - `--matter-id` (required):   The identification number of the legal hold matter. To get the ID for a matter, run the command `crashplan legal-hold list`.
 - `--username` (required):    The CrashPlan username of the custodian to add to the matter.
 - `--profile` (optional):     The profile to use to execute the command. If not specified, the default profile is used.

## Release custodians
You can [release one or more custodians](https://support.crashplan.com/hc/en-us/articles/8603769878157-Create-a-legal-hold-matter#Release-or-reactivate-custodians) from a legal hold matter using the CrashPlan CLI.

### Release multiple custodians

To release multiple custodians at once:

1. Enter the matter ID(s) and CrashPlan usernames to the [CSV file template you generated](#get-csv-template).
2. Save the file to your current working directory.
3. Use the `bulk remove` command with the file path of the CSV you created. For example:
    ```bash
    crashplan legal-hold bulk remove /Users/admin/remove_users_from_legal_hold.csv
    ```

### Release a single custodian

Use `remove-user` to release a single custodian. For example:

 ```bash
    crashplan legal-hold remove-user --matter-id  123456789123456789 --username user@example.com
    ```

Options are the same as `add-user` shown above.

## View matters and custodians

You can use the CrashPlan CLI to get a list of all the [legal hold matters](https://support.crashplan.com/hc/en-us/articles/9225467244045--Legal-Hold-reference#All-matters) for your organization, or get full details for a matter.

### List legal hold matters

To view a list of legal hold matters for your organization, use the following command:

 ```bash
    crashplan legal-hold list
    ```

This command produces the matter ID, name, description, creator, and creation date for the legal hold matters.

### View matter details

To view active custodians for a legal hold matter, enter

```bash
crashplan legal-hold show
```
 with the matter ID, for example:

 ```bash
    crashplan legal-hold show 123456789123456789
    ```

To view active custodians for a legal hold matter, as well as the details of the preservation policy, enter

 ```bash
    crashplan legal-hold show <matterID> --include-policy
    ```

To view all custodians (including inactive) for a legal hold matter, enter

 ```bash
    crashplan legal-hold show <matterID> --include-inactive
    ```

### List legal hold events

To view a list of legal hold administrative events, use the following command:

 ```bash
    crashplan legal-hold search-events -m <matterID>
    ```

This command takes the required filters of a specific matter uid, and optional filters of beginning timestamp, end timestamp, and event type.

Future versions of the crashplancli will allow searching events from all legal holds.

Learn more about the [Legal Hold](../commands/legalhold.md) commands.
