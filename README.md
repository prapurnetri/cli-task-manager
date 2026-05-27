# CLI Task Manager

A fast, lightweight task manager that runs in your terminal. No installs, no accounts — just Python.

## Quick Start

```bash
python tasks.py add "Your first task" -p high
python tasks.py list
```

## Commands

| Command | Example | Description |
|---|---|---|
| `add` | `python tasks.py add "Buy milk" -p low` | Add a task |
| `list` | `python tasks.py list` | View pending tasks |
| `done` | `python tasks.py done 1` | Mark task complete |
| `undone` | `python tasks.py undone 1` | Reopen a task |
| `edit` | `python tasks.py edit 1 -p high` | Edit a task |
| `delete` | `python tasks.py delete 1` | Delete a task |
| `show` | `python tasks.py show 1` | View task details |
| `search` | `python tasks.py search work` | Search tasks |
| `clear` | `python tasks.py clear` | Remove completed tasks |
| `stats` | `python tasks.py stats` | View progress |

## Flags

| Flag | Description | Example |
|---|---|---|
| `-p` | Priority | `-p high / medium / low` |
| `-d` | Due date | `-d 2026-06-30` |
| `-t` | Tags | `-t work,urgent` |
| `-n` | Notes | `-n "Check with team first"` |
