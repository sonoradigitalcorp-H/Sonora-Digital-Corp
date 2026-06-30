import json
import os
import re
import subprocess
from typing import Any

from src.core.agents.agent_base import (
    AgentBase,
    error_response,
    match_keywords,
    success_response,
)


def _find_gh():
    for p in ["/usr/bin/gh", "/home/mystic/.local/bin/gh", "/snap/bin/gh"]:
        if os.path.exists(p):
            return p
    return "gh"


class PRAgent(AgentBase):
    name = "pr"
    description = "Pull Request management — create, list, view, merge PRs on GitHub"
    timeout = 60

    def __init__(self):
        super().__init__()
        self.gh_bin = _find_gh()

    def _gh(self, args):
        try:
            r = subprocess.run(
                [self.gh_bin] + args, capture_output=True, text=True, timeout=30
            )
            return {
                "stdout": r.stdout.strip(),
                "stderr": r.stderr.strip(),
                "returncode": r.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"error": "gh command timed out"}
        except FileNotFoundError:
            return {"error": "gh CLI not found. Install: npm i -g gh or apt install gh"}
        except Exception as e:
            return {"error": str(e)}

    def _get_remote(self):
        r = self._gh(["repo", "view", "--json", "nameWithOwner"])
        if r.get("returncode") == 0 and r.get("stdout"):
            try:
                return json.loads(r["stdout"]).get("nameWithOwner", "")
            except json.JSONDecodeError:
                pass
        return ""

    def _get_current_branch(self):
        try:
            return subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
        except Exception:
            return "main"

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"PR task: {task[:100]}...")

        if match_keywords(
            task, ["crea", "creá", "create", "nuevo", "new", "abrí", "abre"]
        ):
            return self._create_pr(task)
        elif match_keywords(
            task, ["lista", "listá", "list", "muestra", "mostrá", "show"]
        ):
            return self._list_prs(task)
        elif match_keywords(
            task, ["view", "ve", "ver", "detalle", "detail", "muestra"]
        ):
            return self._view_pr(task)
        elif match_keywords(
            task, ["merge", "fusiona", "fusioná", "combina", "combiná"]
        ):
            return self._merge_pr(task)
        elif match_keywords(task, ["revisa", "review", "valida", "validá", "check"]):
            return self._review_pr(task)
        else:
            return self._create_pr(task)

    def _create_pr(self, task: str) -> dict[str, Any]:
        remote = self._get_remote()
        if not remote:
            return error_response(
                self.name, task, "No GitHub remote found. Configure gh auth first."
            )

        branch = self._get_current_branch()
        title_match = re.search(
            r"(?:title|título|titulo)[:\s]+(.+)", task, re.IGNORECASE
        )
        title = (
            title_match.group(1).strip().split("\n")[0]
            if title_match
            else f"feat: auto PR from {branch}"
        )
        body_match = re.search(r"(?:body|cuerpo|desc)[:\s]+(.+)", task, re.IGNORECASE)
        body = (
            body_match.group(1).strip()
            if body_match
            else f"PR generado por JARVIS desde {branch}"
        )
        base_match = re.search(r"(?:base)[:\s]+(\S+)", task, re.IGNORECASE)
        base = base_match.group(1) if base_match else "main"

        args = [
            "pr",
            "create",
            "--repo",
            remote,
            "--title",
            title,
            "--body",
            body,
            "--base",
            base,
            "--head",
            branch,
        ]
        r = self._gh(args)
        if r.get("returncode") == 0:
            pr_url = r.get("stdout", "").strip()
            pr_num = pr_url.rstrip("/").split("/")[-1] if pr_url else ""
            return success_response(
                self.name,
                task,
                action="create_pr",
                repo=remote,
                branch=branch,
                title=title,
                url=pr_url,
                number=pr_num,
            )
        return error_response(
            self.name, task, r.get("stderr", r.get("error", "Unknown error"))
        )

    def _list_prs(self, task: str) -> dict[str, Any]:
        remote = self._get_remote()
        if not remote:
            return error_response(self.name, task, "No GitHub remote found.")
        repo_match = re.search(r"(?:repo)[:\s]+(\S+)", task, re.IGNORECASE)
        repo = repo_match.group(1) if repo_match else remote
        state_match = re.search(r"(?:state|estado)[:\s]+(\w+)", task, re.IGNORECASE)
        state = state_match.group(1) if state_match else "open"

        r = self._gh(
            [
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                state,
                "--limit",
                "20",
                "--json",
                "number,title,state,headRefName,baseRefName,createdAt,url",
            ]
        )
        if r.get("returncode") == 0:
            try:
                prs = json.loads(r["stdout"]) if r["stdout"] else []
            except json.JSONDecodeError:
                prs = []
            return success_response(
                self.name,
                task,
                action="list_prs",
                repo=repo,
                state=state,
                count=len(prs),
                prs=prs,
            )
        return error_response(self.name, task, r.get("stderr", "Failed to list PRs"))

    def _view_pr(self, task: str) -> dict[str, Any]:
        remote = self._get_remote()
        if not remote:
            return error_response(self.name, task, "No GitHub remote found.")
        num_match = re.search(
            r"(?:#|number|número|numero|PR)\s*(\d+)", task, re.IGNORECASE
        )
        pr_num = num_match.group(1) if num_match else ""
        if not pr_num:
            return error_response(
                self.name, task, "Specify PR number (e.g., 'view PR #42')"
            )

        r = self._gh(
            [
                "pr",
                "view",
                pr_num,
                "--repo",
                remote,
                "--json",
                "number,title,state,body,headRefName,baseRefName,author,additions,deletions,url",
            ]
        )
        if r.get("returncode") == 0:
            try:
                data = json.loads(r["stdout"]) if r["stdout"] else {}
            except json.JSONDecodeError:
                data = {}
            return success_response(
                self.name, task, action="view_pr", repo=remote, number=pr_num, pr=data
            )
        return error_response(
            self.name, task, r.get("stderr", f"PR #{pr_num} not found")
        )

    def _merge_pr(self, task: str) -> dict[str, Any]:
        remote = self._get_remote()
        if not remote:
            return error_response(self.name, task, "No GitHub remote found.")
        num_match = re.search(
            r"(?:#|number|número|numero|PR)\s*(\d+)", task, re.IGNORECASE
        )
        pr_num = num_match.group(1) if num_match else ""
        if not pr_num:
            return error_response(
                self.name, task, "Specify PR number (e.g., 'merge PR #42')"
            )
        strategy_match = re.search(
            r"(?:--(\w+)-merge|strategy|merge\s+method)[:\s]+(\w+)", task, re.IGNORECASE
        )
        strategy = "merge"
        if strategy_match:
            s = (strategy_match.group(1) or strategy_match.group(2) or "").lower()
            if s in ("squash", "rebase"):
                strategy = s

        r = self._gh(["pr", "merge", pr_num, "--repo", remote, f"--{strategy}"])
        status = "merged" if r.get("returncode") == 0 else "failed"
        return success_response(
            self.name,
            task,
            action="merge_pr",
            repo=remote,
            number=pr_num,
            strategy=strategy,
            status=status,
            output=r.get("stdout", ""),
            error=r.get("stderr", "") if status == "failed" else "",
        )

    def _review_pr(self, task: str) -> dict[str, Any]:
        remote = self._get_remote()
        if not remote:
            return error_response(self.name, task, "No GitHub remote found.")
        num_match = re.search(
            r"(?:#|number|número|numero|PR)\s*(\d+)", task, re.IGNORECASE
        )
        pr_num = num_match.group(1) if num_match else ""

        if pr_num:
            r = self._gh(["pr", "diff", pr_num, "--repo", remote])
        else:
            branch = self._get_current_branch()
            r = self._gh(["pr", "diff", "--repo", remote, "--head", branch])

        if r.get("returncode") == 0:
            diff = r.get("stdout", "")[:3000]
            return success_response(
                self.name,
                task,
                action="review_pr",
                repo=remote,
                number=pr_num or "current",
                diff_preview=diff[:2000],
            )
        return error_response(self.name, task, r.get("stderr", "No diff available"))
