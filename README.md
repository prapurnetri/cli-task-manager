# CLI Task Manager

A simple, powerful command-line task manager built with Python. Zero dependencies — just Python 3.6+.

## Features
- Add tasks with priority, due dates, tags, and notes
- Color-coded output with overdue warnings
- Search, filter, and sort tasks
- Progress stats with visual progress bar

## Usage
```bash
python tasks.py add "Your task" -p high -d 2026-06-01 -t work
python tasks.py list
python tasks.py done 1
python tasks.py stats
python tasks.py help
` ``

## Commands
| Command | Description |
|---|---|
| `add` | Add a new task |
| `list` | View tasks |
| `done <id>` | Mark complete |
| `delete <id>` | Delete a task |
| `search <word>` | Search tasks |
| `stats` | View progress |
```

**Step 2 — Now run these commands in your terminal:**

```bash
git add tasks.py README.md
git commit -m "Initial commit: CLI task manager"
```

**Step 3 — Then push to GitHub:**
```bash
git remote add origin https://github.com/YOURUSERNAME/cli-task-manager.git
git branch -M main
git push -u origin main
```

---

The error happened because `README.md` didn't exist when Git tried to add it. Git can only add files that are actually there. Now that you'll create it first, it'll work fine.

Also notice `tasks_data.json` is showing as untracked — you don't want to commit that (it's your personal data). Run this first:

```bash
echo "tasks_data.json" > .gitignore
git add .gitignore
```

Then do the `git add tasks.py README.md` step above. That keeps your task data private.