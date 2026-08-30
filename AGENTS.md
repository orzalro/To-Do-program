# Repository instructions

## Code maintenance

- Add concise comments to changed code when they help explain the intent or a non-obvious decision.
- When a bug is discovered, add its case as a regression test and verify that the test passes after the fix.

## Verification

- Before creating a release, run the full test suite and stop the release if any test fails.

## Git commits

- When commits are requested, split changes into logical feature-focused commits and use messages that clearly describe each change.

## GitHub issue operations

- Do not comment on, close, or reopen issues directly with the repository owner's `gh` credentials.
- Dispatch `.github/workflows/issue-bot.yml` so issue activity is attributed to `github-actions[bot]`.
- Wait for the workflow run to succeed, then verify the issue state or comment author.
- Write concise Korean comments that match the repository owner's usual tone.
