# Ingest Audit Logs into a SIEM tool

This guide provides instructions on using the CLI to ingest crashplan Audit logs
into a security information and event management (SIEM) tool like LogRhythm, Sumo Logic, or IBM QRadar.

## Considerations

To ingest Audit logs into a SIEM tool using the crashplan command-line interface, the crashplan user account running the integration
must be assigned roles that provide the necessary permissions.

## Before you begin

First install and configure the crashplan CLI following the instructions in
[Getting Started](gettingstarted.md).

## Run queries
Audit logs are available in JSON format. You can query the data as a scheduled job or run ad-hoc queries.

Learn more about searching [Audit Logs](../commands/auditlogs.md) using the CLI.

### Run a query as a scheduled job

Use your favorite scheduling tool, such as cron or Windows Task Scheduler, to run a query on a regular basis. Specify
the profile to use by including `--profile`.

#### Audit Logs
An example to send to the syslog server only the audit log events that meet the filter criteria from the last 30 days.
```bash
crashplan audit-logs send-to syslog.example.com:514 -p UDP --profile profile1 --actor-username 'arthur.pendragon@example.com' -b 30d
```

As a best practice, use a separate profile when executing a scheduled task. Using separate profiles can help prevent accidental updates to your stored checkpoints, for example, by adding `--use-checkpoint` to adhoc queries.

#### Audit Logs
Print audit log events since June 5 which affected a certain user:
```bash
crashplan audit-logs search -b 2025-06-05 --affected-username 'arthur.pendragon@examply.com'
```

#### Example Outputs

Example output for a single audit log event (in default JSON format):
```json
{
    "type$": "audit_log::logged_in/1",
    "actorId": "1015070955620029617",
    "actorName": "arthur.pendragon@example.com",
    "actorAgent": "pycpg 1.17.0 python 3.7.10",
    "actorIpAddress": "67.220.16.122",
    "timestamp": "2021-08-30T16:16:19.165Z",
    "actorType": "USER"
}
```
