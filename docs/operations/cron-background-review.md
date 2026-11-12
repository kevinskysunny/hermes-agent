# Cron background review opt-out

Operational patch: `cron-background-review-1.0.0` (2026-11-12).

A completed agent turn can start a separate memory/skill review that writes
after the main report has been produced. Cron delivery contains the main
result, not the review's final response. A read-only audit should therefore
disable this review explicitly in its job record:

```json
{"background_review": false}
```

This optional job-store field is consumed by `cron.scheduler.run_job` and
preserved by the existing job store. Missing or `true` keeps existing behavior.
The field controls background review only: it does not sandbox task tools,
disable explicitly requested task writes, or stop the periodic curator.
Operators must still use appropriate task instructions and tool permissions.

The agent-level `background_review_enabled=False` constructor argument stops
both memory and skill review before any worker or model fork is started.
Ordinary interactive agents retain their existing default.

Change job records through the job-store locking API during an idle window;
do not overwrite a cached copy of jobs.json. Back up the changed source and
job records before deployment. Restart only the gateway loading the patch,
after confirming its workers are idle. Other profiles need no restart.

Verify the report still completes, no background worker is created for the
opted-out job, and unrelated jobs still retain their prior review behavior.
Rollback restores the prior source and only removes the added field from
the selected job, preserving current scheduling and run metadata.
