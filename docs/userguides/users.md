# Manage Users

You can use the CLI to manage user information, update user roles, and move users between organizations.

To view a all the users currently in your organization, you can export a list from the [Users list in the crashplan console](https://support.crashplan.com/hc/en-us/articles/9218711102989--Users-reference) or you can use the `list` command.

You can use optional flags to filter the users you want to view. The following command will print all active users with the `Desktop User` role who belong to the organization with UID `1234567890`:
```bash
crashplan users list --org-uid 1234567890 --role-name "Desktop User" --active
```

To change the information for one or more users, provide the user UID and updated information with the `update` or `bulk update` commands.

## Manage User Roles

Apply [crashplan's user roles](https://support.crashplan.com/hc/en-us/articles/9112366299789-Roles-reference#Standard-roles) to user accounts to provide administrators with the desired set of permissions.  Each role has associated permissions, limitations, and recommended use cases.

#### View User Roles
View a user's current roles and other details with the `show` command:
```bash
crashplan users show "arthur.pendragon@example.com"
```
Alternatively, pass the `--include-roles` flag to the `list ` command.  The following command will print a list of all active users and their current roles:
```bash
crashplan users list --active --include-roles
```

#### Update User Roles

Use the following command to add a role to a user:
```bash
crashplan users add-role --username "arthur.pendragon@example.com" --role-name "Desktop User"
```

Similarly, use the `remove-role` command to remove a role from a user.

## Deactivate a User

You can deactivate a user with the following command:
```bash
crashplan users deactivate arthur.pendragon@example.com
```

To deactivate multiple users at once, enter each username on a new line in a CSV file, then use the `bulk deactivate` command with the CSV file path. For example:
```bash
crashplan users bulk deactivate users_to_deactivate.csv
```

Similarly, use the `reactivate` and `bulk reactivate` commands to reactivate a user.

## Assign an Organization

Use [Organizations](https://support.crashplan.com/hc/en-us/articles/9222924876941-Organizations-reference) to group users together in the crashplan environment.

You'll need an organization's unique identifier number (UID) to move a user into it.  You can use the `list` command to view a list of all current user organizations, including UIDs:
```bash
crashplan users orgs list
```

Use the `show` command to view all the details of a user organization.
As an example, to print the details of an organization associated with the UID `123456789` in JSON format:
```bash
crashplan users show 123456789 -f JSON
```

Once you've identified your organizations UID number, use the `move` command to move a user into that organization.  In the following example a user is moved into the organization associated with the UID `1234567890`:
```bash
crashplan users move --username arthur.pendragon@example.com --org-id 1234567890
```

Alternatively, to move multiple users between organizations, fill out the `move` CSV file template, then use the `bulk move` command with the CSV file path.
```bash
crashplan users bulk move bulk-command.csv
```

## Get CSV Template for bulk commands

The following command generates a CSV template for each of the available bulk user commands.  The CSV file is saved to the current working directory.
```bash
crashplan users bulk generate-template [update|move|add-alias|remove-alias|update-risk-profile]
```

Once generated, fill out and use each of the CSV templates with their respective bulk commands.
```bash
crashplan users bulk [update|move|deactivate|reactivate] bulk-command.csv
```

A CSV with a `username` column and a single username on each new line is used for the `reactivate` and `deactivate` bulk commands.  These commands are not available as options for `generate-template`.

Learn more about [Managing Users](../commands/users.md).
