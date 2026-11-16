---
name: inbox-triage-tasks
description: "When Jack asks to triage unread email or turn actionable messages into tasks, review the requested Gmail scope and create traceable Google Tasks only through verified connected actions."
---

# Inbox triage to Google Tasks

1. Call Zapier `inspect_zapier_actions` before any Gmail or Google Tasks operation. Verify Gmail search is enabled on the intended account. If Jack gives no scope, search unread mail with `is:unread`; otherwise honor his sender, label, or date-window scope.
2. Verify Google Tasks is enabled and authorized, and inspect its available task-create, task-list enumeration, and task-retrieval actions. If any is unavailable, stop before creating tasks and report the specific missing capability; never claim task creation succeeded.
3. Resolve the destination task list by inspecting available lists. Use Jack's explicit list preference when supplied; if not, ask him which list to use rather than guessing a default. Confirm the account and list before any external write.
4. Review matching messages and create tasks only for clear actionable requests. For each, use a concise verb-led title and include the action, sender, subject, and traceable message reference in the description. Do not invent deadlines or facts absent from the email. Flag ambiguous messages for Jack instead of creating tasks.
5. Prevent duplicates by checking the destination list for an existing task with the same Gmail message identifier before creation. If message identifiers cannot be reliably compared, do not create that task; report the limitation.
6. Before creating tasks, summarize the actionable messages and proposed task titles/list to Jack and obtain confirmation because this changes an external account. Do not archive, label, delete, or mark mail read unless Jack separately asks.
7. Create one task per confirmed actionable message. If a create result is missing or ambiguous, retrieve the task list and check for the task before retrying.
8. Verify every created task by its returned identifier or by retrieving it from the chosen list. Report verified tasks, their list, and messages needing clarification; clearly distinguish unavailable or unverified tasks.
