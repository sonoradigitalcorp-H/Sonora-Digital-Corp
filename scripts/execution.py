#!/usr/bin/env python3
"""Execution Kernel CLI — submit, status, cancel, retry, list [FR5]"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
from apps.decide.execution.queue import TaskQueue


def cmd_submit(args):
    q = TaskQueue()
    result = q.submit(args.agent, args.operation,
                      params=json.loads(args.params) if args.params else {},
                      priority=args.priority, max_retries=args.max_retries,
                      spec_id=args.spec_id)
    print(json.dumps(result, indent=2))


def cmd_status(args):
    q = TaskQueue()
    task = q.status(args.task_id)
    if task:
        print(json.dumps(task, indent=2, default=str))
    else:
        print(json.dumps({"error": "task not found", "id": args.task_id}))


def cmd_cancel(args):
    q = TaskQueue()
    q.cancel(args.task_id)
    print(json.dumps({"status": "cancelled", "id": args.task_id}))


def cmd_retry(args):
    q = TaskQueue()
    task = q.status(args.task_id)
    if not task:
        print(json.dumps({"error": "task not found", "id": args.task_id}))
        return
    if task["status"] not in ("failed", "cancelled"):
        print(json.dumps({"error": f"task is {task['status']}, not retryable", "id": args.task_id}))
        return
    q.fail(args.task_id, "manual retry", retry=True)
    updated = q.status(args.task_id)
    print(json.dumps({"status": "retry_submitted", "new_status": updated["status"], "id": args.task_id}))


def cmd_list(args):
    q = TaskQueue()
    tasks = q.list_tasks(status=args.status, agent=args.agent, limit=args.limit)
    print(json.dumps(tasks, indent=2, default=str))


def cmd_stats(args):
    q = TaskQueue()
    print(json.dumps(q.stats(), indent=2))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Execution Kernel CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_submit = sub.add_parser("submit", help="Submit a new task")
    p_submit.add_argument("--agent", required=True)
    p_submit.add_argument("--operation", required=True)
    p_submit.add_argument("--params", default="{}")
    p_submit.add_argument("--priority", type=int, default=0)
    p_submit.add_argument("--max-retries", type=int, default=3)
    p_submit.add_argument("--spec-id")
    p_submit.set_defaults(func=cmd_submit)

    p_status = sub.add_parser("status", help="Get task status")
    p_status.add_argument("task_id")
    p_status.set_defaults(func=cmd_status)

    p_cancel = sub.add_parser("cancel", help="Cancel a task")
    p_cancel.add_argument("task_id")
    p_cancel.set_defaults(func=cmd_cancel)

    p_retry = sub.add_parser("retry", help="Retry a failed task")
    p_retry.add_argument("task_id")
    p_retry.set_defaults(func=cmd_retry)

    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--status")
    p_list.add_argument("--agent")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_stats = sub.add_parser("stats", help="Queue statistics")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
