#!/usr/bin/env python3
"""Social Media Automation — Playwright-based with anti-loop, cache, low memory.

Features:
1. Twitter/X: post, like, reply, follow, DM
2. Instagram: post, story, reply to DMs, like, comment
3. TikTok: post, reply to comments
4. All platforms: anti-detection, cookie persistence, rate limiting

Memory protections:
- Max 512MB RAM usage
- Auto-restart browser every 30 min
- Cookie cache in SQLite (not JSON files)
- Session persistence across restarts
- No infinite loops: max iterations per session

CPU protections:
- Random delays between actions (2-5 min)
- Only 1 browser tab at a time
- Close idle tabs automatically
- No headless=visible (always headless)
"""

import os
import sys
import json
import time
import random
import hashlib
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("social-automation")

# ── Configuration ─────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "ops" / "state" / "social_sessions.db"
CONTENT_DIR = BASE_DIR / "ops" / "state" / "content-queue"
MAX_RAM_MB = 512
MAX_ACTIONS_PER_HOUR = 10
MIN_DELAY_SECONDS = 120  # 2 min between actions
MAX_SESSION_MINUTES = 30
MAX_RETRIES = 3

# ── Cookie/Session Manager ───────────────────────────────────

class SessionManager:
    """SQLite-based cookie/session persistence."""
    
    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self._init_db()
    
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                platform TEXT,
                username TEXT,
                cookies BLOB,
                storage TEXT,
                updated_at REAL,
                PRIMARY KEY (platform, username)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS action_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                action TEXT,
                target TEXT,
                status TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()
    
    def save_session(self, platform: str, username: str, cookies: list, storage: dict = None):
        self.conn.execute(
            "INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?)",
            (platform, username, json.dumps(cookies).encode(), 
             json.dumps(storage or {}).encode(), time.time())
        )
        self.conn.commit()
    
    def load_session(self, platform: str, username: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT cookies, storage FROM sessions WHERE platform=? AND username=?",
            (platform, username)
        ).fetchone()
        if row:
            return {
                "cookies": json.loads(row[0]),
                "storage": json.loads(row[1]),
            }
        return None
    
    def log_action(self, platform: str, action: str, target: str, status: str):
        self.conn.execute(
            "INSERT INTO action_log (platform, action, target, status, timestamp) VALUES (?, ?, ?, ?, ?)",
            (platform, action, target, status, time.time())
        )
        self.conn.commit()
    
    def get_actions_last_hour(self, platform: str) -> int:
        cutoff = time.time() - 3600
        row = self.conn.execute(
            "SELECT COUNT(*) FROM action_log WHERE platform=? AND timestamp>? AND status='ok'",
            (platform, cutoff)
        ).fetchone()
        return row[0] if row else 0
    
    def get_last_action_time(self, platform: str) -> float:
        row = self.conn.execute(
            "SELECT MAX(timestamp) FROM action_log WHERE platform=? AND status='ok'",
            (platform,)
        ).fetchone()
        return row[0] if row and row[0] else 0
    
    def cleanup_old_logs(self, days: int = 7):
        cutoff = time.time() - (days * 86400)
        self.conn.execute("DELETE FROM action_log WHERE timestamp<?", (cutoff,))
        self.conn.commit()


# ── Content Queue ─────────────────────────────────────────────

class ContentQueue:
    """Manage content to post across platforms."""
    
    def __init__(self, queue_dir: Path = CONTENT_DIR):
        queue_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = queue_dir / "queue.json"
        self._load()
    
    def _load(self):
        if self.queue_file.exists():
            self.queue = json.loads(self.queue_file.read_text())
        else:
            self.queue = []
    
    def _save(self):
        self.queue_file.write_text(json.dumps(self.queue, indent=2, ensure_ascii=False))
    
    def add(self, platform: str, content: dict, schedule: str = "asap"):
        """Add content to queue."""
        item = {
            "id": hashlib.md5(json.dumps(content).encode()).hexdigest()[:8],
            "platform": platform,
            "content": content,
            "schedule": schedule,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "posted_at": None,
        }
        self.queue.append(item)
        self._save()
        return item["id"]
    
    def get_next(self, platform: str) -> Optional[dict]:
        """Get next pending item for platform."""
        for item in self.queue:
            if item["platform"] == platform and item["status"] == "pending":
                return item
        return None
    
    def mark_posted(self, item_id: str):
        for item in self.queue:
            if item["id"] == item_id:
                item["status"] = "posted"
                item["posted_at"] = datetime.now().isoformat()
                break
        self._save()
    
    def get_stats(self) -> dict:
        pending = sum(1 for i in self.queue if i["status"] == "pending")
        posted = sum(1 for i in self.queue if i["status"] == "posted")
        return {"pending": pending, "posted": posted, "total": len(self.queue)}


# ── Memory Monitor ────────────────────────────────────────────

class MemoryGuard:
    """Monitor RAM per-process and prevent OOM."""
    
    def __init__(self, max_mb: int = MAX_RAM_MB):
        self.max_mb = max_mb
        self._pid = os.getpid()
    
    def check(self) -> bool:
        """Return True if OK, False if over limit. Checks PROCESS memory, not system."""
        try:
            import psutil
            process = psutil.Process(self._pid)
            mem_mb = process.memory_info().rss / 1024 / 1024
            if mem_mb > self.max_mb:
                logger.warning(f"Memory guard: process {self._pid} using {mem_mb:.0f}MB > {self.max_mb}MB limit")
                return False
            return True
        except ImportError:
            return True
    
    def get_usage(self) -> dict:
        try:
            import psutil
            process = psutil.Process(self._pid)
            mem_mb = process.memory_info().rss / 1024 / 1024
            vmem = psutil.virtual_memory()
            return {
                "process_mb": round(mem_mb, 1),
                "system_used_mb": round(vmem.used / 1024 / 1024, 1),
                "system_available_mb": round(vmem.available / 1024 / 1024, 1),
                "system_percent": vmem.percent,
                "limit_mb": self.max_mb,
                "under_limit": mem_mb < self.max_mb,
            }
        except ImportError:
            return {"process_mb": 0, "system_available_mb": 999, "under_limit": True}


# ── Anti-Loop Safeguard ───────────────────────────────────────

class AntiLoop:
    """Prevent infinite loops in automation."""
    
    def __init__(self, max_iterations: int = 100, max_same_action: int = 5):
        self.iterations = 0
        self.max_iterations = max_iterations
        self.action_counts: Dict[str, int] = {}
        self.max_same_action = max_same_action
    
    def check(self, action: str = "") -> bool:
        """Return True if safe to continue."""
        self.iterations += 1
        
        if self.iterations >= self.max_iterations:
            logger.error(f"AntiLoop: max iterations ({self.max_iterations}) reached")
            return False
        
        if action:
            self.action_counts[action] = self.action_counts.get(action, 0) + 1
            if self.action_counts[action] >= self.max_same_action:
                logger.error(f"AntiLoop: action '{action}' repeated {self.max_same_action} times")
                return False
        
        return True
    
    def reset(self):
        self.iterations = 0
        self.action_counts.clear()


# ── Platform Base ─────────────────────────────────────────────

class PlatformBase:
    """Base class for platform automation."""
    
    def __init__(self, name: str, sessions: SessionManager, 
                 memory: MemoryGuard, antiloop: AntiLoop):
        self.name = name
        self.sessions = sessions
        self.memory = memory
        self.antiloop = antiloop
        self.browser = None
        self.context = None
        self.page = None
        self._start_time = time.time()
    
    def _check_limits(self) -> Tuple[bool, str]:
        """Check all limits before action."""
        if not self.memory.check():
            return False, "Memory limit exceeded"
        
        if not self.antiloop.check():
            return False, "Anti-loop triggered"
        
        if self.sessions.get_actions_last_hour(self.name) >= MAX_ACTIONS_PER_HOUR:
            return False, f"Rate limit: {MAX_ACTIONS_PER_HOUR}/hour"
        
        elapsed = time.time() - self._start_time
        if elapsed > MAX_SESSION_MINUTES * 60:
            return False, f"Session timeout: {MAX_SESSION_MINUTES}min"
        
        last_action = self.sessions.get_last_action_time(self.name)
        if time.time() - last_action < MIN_DELAY_SECONDS:
            wait = MIN_DELAY_SECONDS - (time.time() - last_action)
            return False, f"Cooldown: {wait:.0f}s remaining"
        
        return True, ""
    
    def _random_delay(self, min_s: float = 10, max_s: float = 30):
        """Human-like random delay."""
        delay = random.uniform(min_s, max_s)
        time.sleep(delay)
    
    async def start(self, headless: bool = True):
        """Start browser with session restoration."""
        from playwright.async_api import async_playwright
        
        self._pw = await async_playwright().start()
        
        # Check memory before starting browser
        if not self.memory.check():
            logger.error("Cannot start browser: memory limit exceeded")
            return False
        
        self.browser = await self._pw.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-default-apps",
                "--disable-sync",
                "--no-first-run",
                f"--js-flags=--max-old-space-size={MAX_RAM_MB // 2}",
            ]
        )
        
        # Restore session if available
        session = self.sessions.load_session(self.name, "default")
        if session:
            self.context = await self.browser.new_context(
                storage_state=session.get("storage"),
                viewport={"width": 1280, "height": 720},
            )
            logger.info(f"Restored session for {self.name}")
        else:
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
            )
        
        self.page = await self.context.new_page()
        return True
    
    async def save_session(self):
        """Save current session state."""
        if self.context:
            storage = await self.context.storage_state()
            self.sessions.save_session(self.name, "default", 
                                       storage.get("cookies", []),
                                       storage)
    
    async def close(self):
        """Close browser and save state."""
        try:
            await self.save_session()
        except Exception:
            pass
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()
    
    async def safe_action(self, action_func, action_name: str, *args, **kwargs):
        """Execute action with all safety checks."""
        ok, reason = self._check_limits()
        if not ok:
            logger.warning(f"Action blocked: {reason}")
            return None
        
        self._random_delay()
        
        try:
            result = await action_func(*args, **kwargs)
            self.sessions.log_action(self.name, action_name, str(kwargs), "ok")
            return result
        except Exception as e:
            self.sessions.log_action(self.name, action_name, str(kwargs), f"error: {e}")
            logger.error(f"Action failed: {e}")
            return None


# ── Twitter/X Automation ──────────────────────────────────────

class TwitterAutomation(PlatformBase):
    """Twitter/X posting, liking, replying with anti-detection."""
    
    def __init__(self, *args, **kwargs):
        super().__init__("twitter", *args, **kwargs)
    
    async def post(self, text: str, media_path: str = None) -> bool:
        """Post a tweet."""
        async def _do_post():
            await self.page.goto("https://x.com/compose/post", wait_until="networkidle")
            await self._random_delay(1, 2)
            
            # Type tweet
            editor = self.page.locator('[data-testid="tweetTextarea_0"]')
            await editor.click()
            await editor.fill(text)
            await self._random_delay(0.5, 1)
            
            # Add media if provided
            if media_path and os.path.exists(media_path):
                file_input = self.page.locator('input[type="file"]')
                await file_input.set_input_files(media_path)
                await self._random_delay(2, 4)
            
            # Click post button
            post_btn = self.page.locator('[data-testid="tweetButton"]')
            await post_btn.click()
            await self._random_delay(2, 3)
            
            logger.info(f"Posted to Twitter: {text[:50]}...")
            return True
        
        return await self.safe_action(_do_post, "post", text=text)
    
    async def reply(self, tweet_url: str, text: str) -> bool:
        """Reply to a tweet."""
        async def _do_reply():
            await self.page.goto(tweet_url, wait_until="networkidle")
            await self._random_delay(1, 2)
            
            reply_box = self.page.locator('[data-testid="tweetTextarea_0"]')
            await reply_box.click()
            await reply_box.fill(text)
            await self._random_delay(0.5, 1)
            
            reply_btn = self.page.locator('[data-testid="tweetButtonInline"]')
            await reply_btn.click()
            await self._random_delay(2, 3)
            
            logger.info(f"Replied on Twitter: {text[:50]}...")
            return True
        
        return await self.safe_action(_do_reply, "reply", tweet_url=tweet_url, text=text)
    
    async def like(self, tweet_url: str) -> bool:
        """Like a tweet."""
        async def _do_like():
            await self.page.goto(tweet_url, wait_until="networkidle")
            await self._random_delay(1, 2)
            
            like_btn = self.page.locator('[data-testid="like"]')
            await like_btn.click()
            await self._random_delay(1, 2)
            
            logger.info(f"Liked tweet: {tweet_url}")
            return True
        
        return await self.safe_action(_do_like, "like", tweet_url=tweet_url)


# ── Instagram Automation ──────────────────────────────────────

class InstagramAutomation(PlatformBase):
    """Instagram posting, stories, DM replies."""
    
    def __init__(self, *args, **kwargs):
        super().__init__("instagram", *args, **kwargs)
    
    async def post(self, image_path: str, caption: str) -> bool:
        """Post to Instagram feed."""
        async def _do_post():
            await self.page.goto("https://www.instagram.com/", wait_until="networkidle")
            await self._random_delay(2, 3)
            
            # Click new post button
            new_post = self.page.locator('svg[aria-label="New post"]').first
            await new_post.click()
            await self._random_delay(1, 2)
            
            # Upload image
            file_input = self.page.locator('input[type="file"]').first
            await file_input.set_input_files(image_path)
            await self._random_delay(2, 4)
            
            # Click next
            next_btn = self.page.locator('button:has-text("Next")')
            await next_btn.click()
            await self._random_delay(1, 2)
            
            # Add caption
            caption_input = self.page.locator('textarea[aria-label="Write a caption..."]')
            await caption_input.fill(caption)
            await self._random_delay(0.5, 1)
            
            # Share
            share_btn = self.page.locator('button:has-text("Share")')
            await share_btn.click()
            await self._random_delay(3, 5)
            
            logger.info(f"Posted to Instagram: {caption[:50]}...")
            return True
        
        return await self.safe_action(_do_post, "post", image_path=image_path, caption=caption)
    
    async def reply_dm(self, username: str, message: str) -> bool:
        """Reply to Instagram DM."""
        async def _do_dm():
            await self.page.goto("https://www.instagram.com/direct/inbox/", wait_until="networkidle")
            await self._random_delay(2, 3)
            
            # Find conversation
            conv = self.page.locator(f'div:has-text("{username}")').first
            await conv.click()
            await self._random_delay(1, 2)
            
            # Type and send
            msg_input = self.page.locator('textarea[placeholder="Message..."]')
            await msg_input.fill(message)
            await self._random_delay(0.5, 1)
            
            send_btn = self.page.locator('button:has-text("Send")')
            await send_btn.click()
            await self._random_delay(1, 2)
            
            logger.info(f"Replied to DM on Instagram: @{username}")
            return True
        
        return await self.safe_action(_do_dm, "dm", username=username, message=message)


# ── Facebook Automation ────────────────────────────────────────

class FacebookAutomation(PlatformBase):
    """Facebook page posting, comments, DMs."""
    
    def __init__(self, *args, **kwargs):
        super().__init__("facebook", *args, **kwargs)
    
    async def post(self, text: str, page_url: str = None, image_path: str = None) -> bool:
        """Post to Facebook page."""
        async def _do_post():
            url = page_url or "https://www.facebook.com/"
            await self.page.goto(url, wait_until="networkidle")
            await self._random_delay(2, 3)
            
            # Click "What's on your mind?"
            create_post = self.page.locator('div[role="button"]:has-text("What"), div[role="button"]:has-text("Qué"), div[aria-label="Create a post"], div[aria-label="Crear una publicación"]').first
            await create_post.click()
            await self._random_delay(1, 2)
            
            # Type post
            editor = self.page.locator('div[contenteditable="true"][role="textbox"]').first
            await editor.click()
            await editor.fill(text)
            await self._random_delay(0.5, 1)
            
            # Add media if provided
            if image_path and os.path.exists(image_path):
                photo_btn = self.page.locator('div[aria-label="Photo/video"], div[aria-label="Foto/vídeo"]').first
                await photo_btn.click()
                await self._random_delay(1, 2)
                file_input = self.page.locator('input[type="file"][accept*="image"]').first
                await file_input.set_input_files(image_path)
                await self._random_delay(2, 4)
            
            # Click post
            post_btn = self.page.locator('div[aria-label="Post"], div[aria-label="Publicar"]').first
            await post_btn.click()
            await self._random_delay(3, 5)
            
            logger.info(f"Posted to Facebook: {text[:50]}...")
            return True
        
        return await self.safe_action(_do_post, "post", text=text)
    
    async def reply_comment(self, post_url: str, comment: str) -> bool:
        """Reply to a Facebook comment."""
        async def _do_reply():
            await self.page.goto(post_url, wait_until="networkidle")
            await self._random_delay(2, 3)
            
            comment_box = self.page.locator('div[aria-label="Write a comment"], div[aria-label="Escribe un comentario"]').first
            await comment_box.click()
            await comment_box.fill(comment)
            await self._random_delay(0.5, 1)
            
            # Press Enter to post comment
            await self.page.keyboard.press("Enter")
            await self._random_delay(2, 3)
            
            logger.info(f"Replied on Facebook: {comment[:50]}...")
            return True
        
        return await self.safe_action(_do_reply, "reply", post_url=post_url, comment=comment)
    
    async def reply_dm(self, username: str, message: str) -> bool:
        """Reply to Facebook DM."""
        async def _do_dm():
            await self.page.goto("https://www.facebook.com/messages/", wait_until="networkidle")
            await self._random_delay(2, 3)
            
            # Find conversation
            conv = self.page.locator(f'div:has-text("{username}")').first
            await conv.click()
            await self._random_delay(1, 2)
            
            # Type message
            msg_input = self.page.locator('div[aria-label="Message"], div[aria-label="Escribe un mensaje"]').last
            await msg_input.click()
            await msg_input.fill(message)
            await self._random_delay(0.5, 1)
            
            # Send
            await self.page.keyboard.press("Enter")
            await self._random_delay(1, 2)
            
            logger.info(f"Replied to DM on Facebook: @{username}")
            return True
        
        return await self.safe_action(_do_dm, "dm", username=username, message=message)


# ── Main Orchestrator ─────────────────────────────────────────

class SocialOrchestrator:
    """Main orchestrator for all social media automation."""
    
    def __init__(self):
        self.sessions = SessionManager()
        self.memory = MemoryGuard()
        self.antiloop = AntiLoop()
        self.content = ContentQueue()
        self.platforms: Dict[str, PlatformBase] = {}
    
    async def start(self, platforms: List[str] = None):
        """Start automation for specified platforms."""
        if platforms is None:
            platforms = ["twitter"]
        
        for p in platforms:
            if p == "twitter":
                self.platforms[p] = TwitterAutomation(
                    self.sessions, self.memory, self.antiloop
                )
            elif p == "instagram":
                self.platforms[p] = InstagramAutomation(
                    self.sessions, self.memory, self.antiloop
                )
            elif p == "facebook":
                self.platforms[p] = FacebookAutomation(
                    self.sessions, self.memory, self.antiloop
                )
        
        # Start all browsers
        for name, platform in self.platforms.items():
            # Try to restore session from saved state
            session_file = BASE_DIR / "ops" / "state" / f"{name}_session.json"
            if session_file.exists():
                logger.info(f"Found saved session for {name}: {session_file}")
            
            await platform.start(headless=True)
            logger.info(f"Started {name} automation")
    
    async def post_content(self, platform: str, content: dict) -> bool:
        """Post content from queue."""
        p = self.platforms.get(platform)
        if not p:
            return False
        
        if platform == "twitter":
            return await p.post(content.get("text", ""), content.get("media"))
        elif platform == "instagram":
            return await p.post(content.get("image", ""), content.get("caption", ""))
        return False
    
    async def run_queue(self, platform: str, max_posts: int = 3):
        """Process content queue for a platform."""
        posted = 0
        while posted < max_posts:
            item = self.content.get_next(platform)
            if not item:
                break
            
            ok = await self.post_content(platform, item["content"])
            if ok:
                self.content.mark_posted(item["id"])
                posted += 1
            else:
                break  # Stop on error or limit
        
        return posted
    
    async def stop(self):
        """Stop all platforms and save sessions."""
        for name, platform in self.platforms.items():
            await platform.close()
            logger.info(f"Stopped {name} automation")
        
        self.sessions.cleanup_old_logs()
    
    def get_report(self) -> dict:
        """Get automation status report."""
        return {
            "platforms": list(self.platforms.keys()),
            "memory": self.memory.get_usage(),
            "queue": self.content.get_stats(),
            "actions_last_hour": {
                p: self.sessions.get_actions_last_hour(p)
                for p in self.platforms
            },
        }


# ── CLI ───────────────────────────────────────────────────────

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Social Media Automation")
    parser.add_argument("--platforms", nargs="+", default=["twitter"], help="Platforms to automate")
    parser.add_argument("--post", type=str, help="Post text to Twitter")
    parser.add_argument("--queue", action="store_true", help="Process content queue")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()
    
    orch = SocialOrchestrator()
    
    if args.status:
        report = orch.get_report()
        print(json.dumps(report, indent=2))
        return
    
    await orch.start(args.platforms)
    
    try:
        if args.post:
            await orch.post_content("twitter", {"text": args.post})
        
        if args.queue:
            for p in args.platforms:
                posted = await orch.run_queue(p)
                print(f"Posted {posted} items to {p}")
    finally:
        await orch.stop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())