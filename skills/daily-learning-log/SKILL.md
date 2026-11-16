---
name: daily-learning-log
description: "When Jack shares daily learning notes or asks to log what he learned, shape them into a dated journal entry and append it to his chosen Google Doc."
---

# Daily learning log

1. Treat Jack's notes as source material; preserve their meaning and do not invent learning outcomes, examples, or next steps. Clarify ambiguous points before drafting, and build on his incremental AI-engineering learning when relevant.
2. Use the supplied date when Jack specifies one; otherwise use today's date in Europe/Madrid. Keep the entry concise but explanatory, with these headings: **Topic / project**, **Key concepts learned**, **Examples and connections**, and **Questions / next steps**. Omit a heading only when its content is genuinely absent.
3. Before any document write, call Zapier `inspect_zapier_actions` and verify Google Docs is enabled, the correct account connection is selected, and the actions `append` (`google_docs_append_text_to_document`) and `get_document_content` (`google_docs_get_document_content`) are available. Stop if any check fails; do not infer access from MCP configuration alone.
4. If Jack has not designated a journal Doc, ask him for its link or ID. Retrieve its content and confirm it is the intended journal; do not choose a matching document based on title alone when multiple candidates exist.
5. Draft the complete entry, show it to Jack, and obtain confirmation before appending because this changes an external document. Do not call the append action before confirmation.
6. Append the confirmed entry to the specified document using `google_docs_append_text_to_document`; treat a missing or ambiguous success result as unverified and do not retry until checking the document to avoid duplicates.
7. Retrieve the document using `google_docs_get_document_content` and confirm the exact dated entry appears at the end. If read-back fails or does not match, report the actual state without claiming success.
8. On success, report the document link and a brief summary of the appended entry. Never include unrelated private document content in the report.
