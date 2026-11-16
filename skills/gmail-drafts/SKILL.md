---
name: gmail-drafts
description: "When Jack asks for an email to be drafted or polished, compose it in his direct, solution-focused voice and save only as an unsent Gmail draft when a verified method exists."
---

# Gmail drafts

1. Collect the recipient, purpose, essential facts, desired outcome, constraints, and tone. For replies, inspect the original email or thread using the connected Gmail read action when available; otherwise ask Jack to provide it. Do not invent facts or imply commitments Jack has not authorized.
2. Ask Jack for a writing sample or preference when the requested voice depends on a style not captured here. Otherwise use a direct, solution-focused tone, and close with “Best regards, Jack” when appropriate.
3. Before saving, call Zapier `inspect_zapier_actions` and verify Gmail is enabled on the intended account and that an unsent draft-creation action is available. Do not use a send action, infer capabilities from the MCP configuration, or enable an unapproved alternate method.
4. If no verified draft-creation action is available, present the subject and body in chat, clearly label them **Chat-only draft — not saved in Gmail**, and explain that Gmail draft saving is unavailable. Never claim it was saved.
5. Show the complete subject and body to Jack and obtain confirmation before creating the external draft. Never send the message.
6. Create the Gmail draft using the verified draft-only action. If the result is missing or ambiguous, inspect Gmail drafts before considering another create call to avoid duplicates.
7. Verify the draft exists by its returned identifier or by retrieving it from Gmail. Report the draft link or identifier only when returned and verified; otherwise state the limitation plainly.
