# Skills Design

This document specifies the intended behavior of three skills before implementation. **Design only:** do not create or implement any skill until Jack gives the green light. The current connected-app state was inspected on 2026-11-16 and may change; re-check Zapier actions and permissions before implementation.

For personalization, the five configuration sources are `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, and `config/mcporter.json`. The first four describe work rules, voice, user preferences, and Jasper's identity; the MCP config identifies the Zapier server endpoint/client, not the enabled app actions or their authorization. Never infer access from that config alone.

## 1. Daily learning log

1. **What does this skill do?** Turn Jack's daily learning notes into a clear, dated, structured journal entry and append it to his designated personal-knowledge Google Doc.
2. **What input does the agent need?** Jack provides a few bullet points (optionally naming a project, topic, questions, or next steps); use the current date interpreted in UTC+01:00 unless he supplies another date. The configuration provides his preference for incremental AI-engineering learning, bullet points/examples, detailed explanations when useful, the assistant's butler voice, Zapier safety rules, and Drive-root default for new Docs. It does not identify the journal Doc or its preferred structure; before first use, obtain its link/ID or ask whether to create a new journal, and agree on an entry template.
3. **What does a good output look like?** Append an entry to the designated Google Doc with a date, topic/project, key concepts learned, examples or connections, and open questions/next steps; report the Doc link and entry summary, and verify the append by retrieving the resulting content or another reliable returned confirmation. Do not claim success on an empty or ambiguous result.

## 2. Gmail drafts in Jack's voice

1. **What does this skill do?** Compose polished, context-appropriate email drafts in Jack's preferred voice, ready for minimal editing and never sent automatically.
2. **What input does the agent need?** Jack supplies the recipient, purpose, essential facts, desired outcome, and any constraints or tone; include the original email/thread when it is a reply. The configuration provides his direct, solution-focused communication preference and the sign-off “Best regards, Jack,” plus the safety rule requiring confirmation before sending. It does not yet contain examples of Jack's email-writing voice or types of email he commonly sends; ask for examples/preferences rather than inventing them. The currently connected Gmail Zapier actions can find messages and attachments, add labels, archive, and move messages to trash, but do not create Gmail drafts or send mail.
3. **What does a good output look like?** A complete subject and email body in Jack's voice, with “Best regards, Jack” when appropriate, stored as an **unsent Gmail draft** and accompanied by its draft link/identifier and verification that the draft exists. This destination is not currently supported by the connected Gmail actions; implementation must first establish and verify a permitted draft-creation method. Until then, label any chat-only text as a draft, not as a saved Gmail draft.

## 3. Inbox triage to Google Tasks

1. **What does this skill do?** Review unread Gmail, identify messages that require action, and create one concise, traceable Google Task for each actionable message.
2. **What input does the agent need?** Jack invokes triage and supplies any scope (such as a sender, label, or date window); if no scope is given, search unread mail with Gmail's `is:unread` query. The configuration supplies his timezone, concise/direct style, confirmation and privacy rules, and the connected Gmail account context. The current Gmail connection supports email search, but does not currently list Google Tasks as an enabled app; Google Tasks is discoverable in the Zapier catalog but must be enabled, authorized, and its task-creation action verified before implementation. A preferred task list is not yet specified; ask Jack or use a documented default only after verifying the account's available lists. Never invent due dates or task facts absent from the email.
3. **What does a good output look like?** Create one Google Task per actionable email with a short verb-led title and a description containing the action, sender/subject, and a link or other traceable email reference; avoid duplicate tasks on repeat runs. Report created tasks and their list, flag any messages needing clarification, and verify each task was returned or can be retrieved. Do not create a task for informational mail, and do not claim completion if task creation is unavailable or unverified.

## Implementation gates

- Re-inspect the currently connected Zapier apps/actions before implementation.
- For the learning log, obtain the target Doc and agree on its structure; confirm read-back verification is available.
- For Gmail drafts, obtain and verify a Gmail draft-creation action or other explicitly approved method; the current connected Gmail action set does not provide one.
- For inbox triage, enable and authorize Google Tasks, verify task creation and task-list selection, and establish a duplicate-prevention strategy.
- Obtain Jack's explicit green light before implementing any of these skills.
