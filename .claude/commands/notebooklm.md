---
description: Run notebooklm CLI commands (list, ask, create, source, generate, login, etc.)
argument-hint: [subcommand] [args...]
allowed-tools: Bash(notebooklm:*), Bash(uv tool run notebooklm:*)
---

Run the NotebookLM CLI (https://github.com/teng-lin/notebooklm-py) with the arguments the user provided after `/notebooklm`.

Arguments: `$ARGUMENTS`

Steps:
1. If `$ARGUMENTS` is empty, run `notebooklm status` to show the current notebook/profile context.
2. Otherwise run `notebooklm $ARGUMENTS` via Bash.
3. If the `notebooklm` executable is not found, tell the user to install it first with:
   `uv tool install "notebooklm-py[browser]"`
4. If the command fails with an authentication error, tell the user to run `notebooklm login` first (this opens a browser window for Google sign-in and must be run somewhere with a display — it won't work in a headless remote sandbox).
5. Show the raw command output back to the user, unmodified.
