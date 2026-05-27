#!/usr/bin/env python3
"""
tasks.py — A simple, powerful CLI Task Manager
Usage: python tasks.py [command] [options]
"""

import json
import os
import sys
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks_data.json")

# ── ANSI Colors ──────────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"
    STRIKE = "\033[9m"

PRIORITY_COLOR = {"high": C.RED, "medium": C.YELLOW, "low": C.GREEN}
PRIORITY_ICON  = {"high": "▲", "medium": "●", "low": "▼"}
STATUS_ICON    = {True: f"{C.GREEN}✓{C.RESET}", False: f"{C.DIM}○{C.RESET}"}

# ── Data Layer ───────────────────────────────────────────────────────────────
def load() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"tasks": [], "next_id": 1}

def save(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Helpers ──────────────────────────────────────────────────────────────────
def find_task(data, task_id: int):
    for t in data["tasks"]:
        if t["id"] == task_id:
            return t
    return None

def fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%b %d, %Y")
    except:
        return iso

def fmt_due(due: str) -> str:
    if not due:
        return ""
    try:
        d = datetime.strptime(due, "%Y-%m-%d").date()
        today = datetime.today().date()
        delta = (d - today).days
        s = f"due {fmt_date(due)}"
        if delta < 0:
            return f"{C.RED}⚠ overdue ({abs(delta)}d ago){C.RESET}"
        elif delta == 0:
            return f"{C.YELLOW}⚡ due today{C.RESET}"
        elif delta <= 3:
            return f"{C.YELLOW}{s}{C.RESET}"
        return f"{C.DIM}{s}{C.RESET}"
    except:
        return due

def print_task(t: dict, verbose=False):
    done  = t.get("done", False)
    pri   = t.get("priority", "medium")
    pc    = PRIORITY_COLOR[pri]
    title = f"{C.STRIKE}{t['title']}{C.RESET}" if done else t["title"]
    tags  = (f"  {C.CYAN}[{', '.join(t['tags'])}]{C.RESET}" if t.get("tags") else "")
    due   = ("  " + fmt_due(t.get("due","")) if t.get("due") else "")

    print(f"  {STATUS_ICON[done]}  {C.BOLD}#{t['id']:<3}{C.RESET} "
          f"{pc}{PRIORITY_ICON[pri]}{C.RESET}  {title}{tags}{due}")

    if verbose:
        if t.get("notes"):
            print(f"         {C.DIM}Notes: {t['notes']}{C.RESET}")
        print(f"         {C.DIM}Created: {fmt_date(t['created'])}{C.RESET}")

def print_header(text: str):
    print(f"\n{C.BOLD}{C.BLUE}{'─'*50}{C.RESET}")
    print(f"  {C.BOLD}{text}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'─'*50}{C.RESET}")

# ── Commands ─────────────────────────────────────────────────────────────────
def cmd_add(args):
    """add <title> [-p high|medium|low] [-d YYYY-MM-DD] [-t tag1,tag2] [-n notes]"""
    if not args:
        print(f"{C.RED}Error: Provide a task title.{C.RESET}")
        return
    data = load()

    title    = args[0]
    priority = "medium"
    due      = ""
    tags     = []
    notes    = ""

    i = 1
    while i < len(args):
        flag = args[i]
        val  = args[i+1] if i+1 < len(args) else ""
        if   flag == "-p": priority = val.lower(); i += 2
        elif flag == "-d": due = val;              i += 2
        elif flag == "-t": tags = [x.strip() for x in val.split(",")]; i += 2
        elif flag == "-n": notes = val;            i += 2
        else: i += 1

    if priority not in ("high", "medium", "low"):
        print(f"{C.RED}Error: Priority must be high, medium, or low.{C.RESET}")
        return

    task = {
        "id":       data["next_id"],
        "title":    title,
        "done":     False,
        "priority": priority,
        "due":      due,
        "tags":     tags,
        "notes":    notes,
        "created":  datetime.now().isoformat(),
    }
    data["tasks"].append(task)
    data["next_id"] += 1
    save(data)

    pc = PRIORITY_COLOR[priority]
    print(f"{C.GREEN}✓ Added{C.RESET} #{task['id']}: {C.BOLD}{title}{C.RESET}  "
          f"{pc}[{priority}]{C.RESET}")

def cmd_list(args):
    """list [-p high|medium|low] [-t tag] [-d] [--done] [--all]"""
    data    = load()
    tasks   = data["tasks"]
    show_all   = "--all"  in args
    done_only  = "--done" in args
    due_sort   = "-d"     in args

    # filters
    if not show_all and not done_only:
        tasks = [t for t in tasks if not t["done"]]
    elif done_only:
        tasks = [t for t in tasks if t["done"]]

    if "-p" in args:
        idx = args.index("-p")
        pri = args[idx+1] if idx+1 < len(args) else ""
        tasks = [t for t in tasks if t.get("priority") == pri]

    if "-t" in args:
        idx = args.index("-t")
        tag = args[idx+1] if idx+1 < len(args) else ""
        tasks = [t for t in tasks if tag in t.get("tags", [])]

    if due_sort:
        tasks.sort(key=lambda t: (t.get("due") or "9999"))
    else:
        tasks.sort(key=lambda t: (
            {"high": 0, "medium": 1, "low": 2}.get(t.get("priority"), 1),
            t["id"]
        ))

    label = "All Tasks" if show_all else ("Completed" if done_only else "Pending Tasks")
    print_header(label)

    if not tasks:
        print(f"  {C.DIM}No tasks found.{C.RESET}\n")
        return

    for t in tasks:
        print_task(t)

    pending   = sum(1 for t in data["tasks"] if not t["done"])
    completed = sum(1 for t in data["tasks"] if t["done"])
    print(f"\n  {C.DIM}Total: {len(data['tasks'])} | "
          f"Pending: {pending} | Completed: {completed}{C.RESET}\n")

def cmd_done(args):
    """done <id> [id2 ...]"""
    if not args:
        print(f"{C.RED}Error: Provide task ID(s).{C.RESET}"); return
    data = load()
    for a in args:
        try:
            t = find_task(data, int(a))
            if t:
                t["done"] = True
                print(f"{C.GREEN}✓ Done{C.RESET}  #{t['id']}: {t['title']}")
            else:
                print(f"{C.RED}Task #{a} not found.{C.RESET}")
        except ValueError:
            print(f"{C.RED}Invalid ID: {a}{C.RESET}")
    save(data)

def cmd_undone(args):
    """undone <id>"""
    if not args:
        print(f"{C.RED}Error: Provide task ID.{C.RESET}"); return
    data = load()
    t = find_task(data, int(args[0]))
    if t:
        t["done"] = False
        save(data)
        print(f"{C.YELLOW}↩ Reopened{C.RESET} #{t['id']}: {t['title']}")
    else:
        print(f"{C.RED}Task not found.{C.RESET}")

def cmd_edit(args):
    """edit <id> [-ti new title] [-p priority] [-d due] [-t tags] [-n notes]"""
    if not args:
        print(f"{C.RED}Error: Provide task ID.{C.RESET}"); return
    data = load()
    t = find_task(data, int(args[0]))
    if not t:
        print(f"{C.RED}Task not found.{C.RESET}"); return

    i = 1
    changed = False
    while i < len(args):
        flag = args[i]
        val  = args[i+1] if i+1 < len(args) else ""
        if   flag == "-ti": t["title"]    = val;                                  changed = True; i += 2
        elif flag == "-p":  t["priority"] = val.lower();                          changed = True; i += 2
        elif flag == "-d":  t["due"]      = val;                                  changed = True; i += 2
        elif flag == "-t":  t["tags"]     = [x.strip() for x in val.split(",")]; changed = True; i += 2
        elif flag == "-n":  t["notes"]    = val;                                  changed = True; i += 2
        else: i += 1

    if changed:
        save(data)
        print(f"{C.CYAN}✎ Updated{C.RESET} #{t['id']}: {t['title']}")
        print_task(t, verbose=True)
    else:
        print(f"{C.DIM}Nothing changed.{C.RESET}")

def cmd_delete(args):
    """delete <id> [id2 ...]"""
    if not args:
        print(f"{C.RED}Error: Provide task ID(s).{C.RESET}"); return
    data = load()
    for a in args:
        try:
            tid = int(a)
            t = find_task(data, tid)
            if t:
                data["tasks"].remove(t)
                print(f"{C.RED}✗ Deleted{C.RESET} #{tid}: {t['title']}")
            else:
                print(f"{C.RED}Task #{a} not found.{C.RESET}")
        except ValueError:
            print(f"{C.RED}Invalid ID: {a}{C.RESET}")
    save(data)

def cmd_show(args):
    """show <id>"""
    if not args:
        print(f"{C.RED}Error: Provide task ID.{C.RESET}"); return
    data = load()
    t = find_task(data, int(args[0]))
    if t:
        print_header(f"Task #{t['id']}")
        print_task(t, verbose=True)
        print()
    else:
        print(f"{C.RED}Task not found.{C.RESET}")

def cmd_search(args):
    """search <keyword>"""
    if not args:
        print(f"{C.RED}Error: Provide a search term.{C.RESET}"); return
    data  = load()
    kw    = " ".join(args).lower()
    found = [t for t in data["tasks"]
             if kw in t["title"].lower()
             or kw in t.get("notes","").lower()
             or any(kw in tag for tag in t.get("tags",[]))]
    print_header(f'Search: "{kw}"')
    if not found:
        print(f"  {C.DIM}No matches.{C.RESET}\n"); return
    for t in found:
        print_task(t, verbose=True)
    print()

def cmd_clear(args):
    """clear — delete all completed tasks"""
    data = load()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if not t["done"]]
    removed = before - len(data["tasks"])
    save(data)
    print(f"{C.GREEN}✓ Cleared {removed} completed task(s).{C.RESET}")

def cmd_stats(args):
    """stats — show summary statistics"""
    data  = load()
    tasks = data["tasks"]
    if not tasks:
        print(f"{C.DIM}No tasks yet.{C.RESET}"); return

    total     = len(tasks)
    done      = sum(1 for t in tasks if t["done"])
    pending   = total - done
    pct       = int(done / total * 100)
    bar_done  = "█" * (pct // 5)
    bar_rest  = "░" * (20 - pct // 5)
    today     = datetime.today().date()
    overdue   = sum(1 for t in tasks if not t["done"] and t.get("due")
                    and datetime.strptime(t["due"], "%Y-%m-%d").date() < today)
    by_pri    = {p: sum(1 for t in tasks if not t["done"] and t.get("priority")==p)
                 for p in ("high","medium","low")}

    print_header("Statistics")
    print(f"  Progress   {C.GREEN}{bar_done}{C.RESET}{C.DIM}{bar_rest}{C.RESET}  "
          f"{C.BOLD}{pct}%{C.RESET}  ({done}/{total})")
    print(f"  Pending    {C.YELLOW}{pending}{C.RESET}")
    print(f"  Completed  {C.GREEN}{done}{C.RESET}")
    if overdue:
        print(f"  Overdue    {C.RED}{overdue}{C.RESET}")
    print(f"\n  By priority (pending):")
    for p, cnt in by_pri.items():
        pc = PRIORITY_COLOR[p]
        print(f"    {pc}{PRIORITY_ICON[p]} {p:<8}{C.RESET} {cnt}")
    print()

def cmd_help(args=None):
    print(f"""
{C.BOLD}{C.BLUE}╔══════════════════════════════════════╗
║       CLI Task Manager  v1.0         ║
╚══════════════════════════════════════╝{C.RESET}

{C.BOLD}COMMANDS{C.RESET}
  {C.CYAN}add{C.RESET} <title> [flags]     Add a new task
    {C.DIM}-p high|medium|low     Priority (default: medium)
    -d YYYY-MM-DD          Due date
    -t tag1,tag2           Tags
    -n "notes"{C.RESET}             Notes

  {C.CYAN}list{C.RESET} [flags]             List tasks
    {C.DIM}--all                  Show all (including done)
    --done                 Show only completed
    -p <priority>          Filter by priority
    -t <tag>               Filter by tag
    -d                     Sort by due date{C.RESET}

  {C.CYAN}done{C.RESET} <id> [id2 ...]      Mark task(s) complete
  {C.CYAN}undone{C.RESET} <id>              Reopen a completed task
  {C.CYAN}edit{C.RESET} <id> [flags]        Edit a task (-ti -p -d -t -n)
  {C.CYAN}delete{C.RESET} <id> [id2 ...]    Delete task(s)
  {C.CYAN}show{C.RESET} <id>               Show task details
  {C.CYAN}search{C.RESET} <keyword>         Search tasks
  {C.CYAN}clear{C.RESET}                    Remove all completed tasks
  {C.CYAN}stats{C.RESET}                    Show statistics
  {C.CYAN}help{C.RESET}                     Show this help

{C.BOLD}EXAMPLES{C.RESET}
  python tasks.py add "Write report" -p high -d 2024-12-31 -t work
  python tasks.py list
  python tasks.py done 1 2 3
  python tasks.py edit 4 -p low -d 2025-01-15
  python tasks.py search work
  python tasks.py stats
""")

# ── Entry Point ──────────────────────────────────────────────────────────────
COMMANDS = {
    "add":    cmd_add,
    "list":   cmd_list,
    "ls":     cmd_list,
    "done":   cmd_done,
    "undone": cmd_undone,
    "edit":   cmd_edit,
    "delete": cmd_delete,
    "del":    cmd_delete,
    "show":   cmd_show,
    "search": cmd_search,
    "find":   cmd_search,
    "clear":  cmd_clear,
    "stats":  cmd_stats,
    "help":   cmd_help,
}

def main():
    args = sys.argv[1:]
    if not args:
        cmd_list([])
        return
    cmd_name = args[0].lower()
    fn = COMMANDS.get(cmd_name)
    if fn:
        fn(args[1:])
    else:
        print(f"{C.RED}Unknown command: {cmd_name}{C.RESET}")
        print(f"Run {C.CYAN}python tasks.py help{C.RESET} for usage.")

if __name__ == "__main__":
    main()
