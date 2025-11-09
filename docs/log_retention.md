# Log Retention Policy

Flowcase stores application logs in the database using the `Log` model. To prevent unbounded growth of the log table, a log retention policy has been implemented.

## Pruning Logs

- **Function**: `utils.logger.prune_logs(older_than_days: int = 90)`
- **Default Retention**: 90 days
- **Behavior**: Deletes all log entries older than the specified number of days and logs an informational message about the number of entries removed.

## Admin API

A new admin endpoint has been added:

- **Endpoint**: `POST /api/admin/logs/prune`
- **Payload**: `{ "days": <int> }` (optional, defaults to 90)
- **Permissions**: Requires admin panel permission.
- **Response**:
  ```json
  {
    "success": true,
    "message": "Pruned logs older than <days> days"
  }
  ```

## CLI Command

A CLI command is available for manual pruning:

```bash
python run.py prune-logs --days 90
```

- This command invokes `utils.logger.prune_logs` with the provided number of days.
- It can be scheduled via cron or any task scheduler to run periodically (e.g., daily).

## Scheduling (Optional)

To automate log pruning, you can add a cron job on the host machine:

```cron
0 2 * * * cd /path/to/flowcase && /usr/bin/python3 run.py prune-logs --days 90 >> /var/log/flowcase_prune.log 2>&1
```

This runs the pruning command every day at 2 AM.

## Benefits

- Prevents the log table from growing indefinitely.
- Reduces database storage usage.
- Keeps recent logs available for troubleshooting while discarding stale entries.

---

*Implemented by the senior Python/DevOps developer as part of the log retention task.* 