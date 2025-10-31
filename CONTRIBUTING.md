CONTRIBUTING
=============

Brief: how to contribute, approvals, and the append-only documentation rules.

1) Append-only documentation policy

- The repository uses an append-only documentation policy for historical traceability. Do not modify or delete existing docs (e.g., `agents.md`, `gemini.md`, `qwen.md`, `SRS.md`, files under `docs/`) without explicit written approval from a project approver.
- Allowed edits without prior approval:
  - Appending new entries to `tasks.md` or journal/log files.
  - Adding new documents that do not alter existing documents' content.
- If a change to an existing doc is required, **open a PR** and add an approval comment from a designated approver. Once approved, perform the edit in the PR and include a short rationale.

2) How to add tasks

- Add microgoals to `tasks.md` by appending them to the bottom following the existing format.
- Mark completion by checking the box and adding ` (completed YYYY-MM-DD by @username)`.
- To deprecate a task, strike through the line and add ` (superseded YYYY-MM-DD by @username: reason)`.

3) Pull request & approval process

- Create a branch named `feature/<short-desc>` or `fix/<short-desc>`.
- Open a PR targeting `dev` and include the motivation and tests/validation steps.
- At least one designated approver must comment `Approved - <approver name>` on the PR before merge if it touches documentation or security-sensitive code.
- For backend, provider adapters, or anything handling user data, request a security review by adding the `security-review` label and @-mentioning the security approver.

4) Contact & approvers

- Project owners / approvers: maintainers listed in project header (see `README.md`). For urgent changes, DM the approver and include the PR link and rationale.

5) Emergency edits

- In the rare emergency case (security or privacy incident), an approver may perform an immediate edit. The approver must then file an audit entry in `docs/audit.log` explaining the change, reason, and timestamp.

*Document created: 2025-10-31*
