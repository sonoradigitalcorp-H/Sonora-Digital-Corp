#!/usr/bin/env python3
"""Playwright MCP Wrapper — OpenCode integration for social media automation.

This script wraps the social automation system into an MCP-compatible interface
that OpenCode can use to delegate social media tasks to sub-agents.

Usage in opencode.jsonc:
  "playwright-social": {
    "type": "local",
    "command": ["python3", "scripts/playwright_social_mcp.py"],
    "enabled": true
  }
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from social_automation import (
    SessionManager, ContentQueue, MemoryGuard, AntiLoop,
    TwitterAutomation, InstagramAutomation, SocialOrchestrator,
)
from content_scheduler import ContentScheduler, generate_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("playwright-social-mcp")


class PlaywrightSocialMCP:
    """MCP-compatible interface for social media automation."""
    
    def __init__(self):
        self.orchestrator = SocialOrchestrator()
        self.scheduler = ContentScheduler()
    
    async def handle_tool(self, tool_name: str, params: dict) -> dict:
        """Handle MCP tool calls."""
        try:
            if tool_name == "social_post":
                return await self._post(params)
            elif tool_name == "social_schedule":
                return await self._schedule(params)
            elif tool_name == "social_queue":
                return await self._queue_status(params)
            elif tool_name == "social_generate":
                return self._generate_content(params)
            elif tool_name == "social_response":
                return self._generate_response(params)
            elif tool_name == "social_status":
                return self._status()
            elif tool_name == "social_memory_check":
                return self._memory_check()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool error: {e}")
            return {"error": str(e)}
    
    async def _post(self, params: dict) -> dict:
        """Post content to a platform."""
        platform = params.get("platform", "twitter")
        text = params.get("text", "")
        media = params.get("media")
        
        if not text:
            return {"error": "text required"}
        
        await self.orchestrator.start([platform])
        try:
            if platform == "twitter":
                ok = await self.orchestrator.platforms[platform].post(text, media)
            elif platform == "instagram":
                ok = await self.orchestrator.platforms[platform].post(media or "", text)
            else:
                return {"error": f"Platform {platform} not supported"}
            
            return {"success": ok, "platform": platform, "text": text[:100]}
        finally:
            await self.orchestrator.stop()
    
    async def _schedule(self, params: dict) -> dict:
        """Schedule content for later posting."""
        platform = params.get("platform", "twitter")
        count = params.get("count", 5)
        
        posts = self.scheduler.generate_content(platform, count)
        scheduled = self.scheduler.schedule_posts(platform, posts)
        
        return {
            "generated": len(posts),
            "scheduled": scheduled,
            "platform": platform,
        }
    
    async def _queue_status(self, params: dict) -> dict:
        """Check content queue status."""
        return self.scheduler.get_stats()
    
    def _generate_content(self, params: dict) -> dict:
        """Generate content without scheduling."""
        platform = params.get("platform", "twitter")
        count = params.get("count", 3)
        
        posts = self.scheduler.generate_content(platform, count)
        return {
            "platform": platform,
            "posts": [{"topic": p["topic"], "content": p["content"][:200]} for p in posts],
        }
    
    def _generate_response(self, params: dict) -> dict:
        """Generate a response for a mention/DM."""
        platform = params.get("platform", "twitter")
        context = params.get("context", "mentions")
        username = params.get("username", "amigo")
        
        response = generate_response(platform, context, username)
        return {"response": response, "platform": platform}
    
    def _status(self) -> dict:
        """Get full status."""
        return {
            "scheduler": self.scheduler.get_stats(),
            "memory": self.orchestrator.memory.get_usage(),
        }
    
    def _memory_check(self) -> dict:
        """Check memory status."""
        return self.orchestrator.memory.get_usage()


async def stdio_handler():
    """Handle MCP stdio protocol."""
    mcp = PlaywrightSocialMCP()
    
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            tool = request.get("tool", "")
            params = request.get("params", {})
            
            result = await mcp.handle_tool(tool, params)
            
            response = json.dumps(result)
            print(response)
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except EOFError:
            break
        except Exception as e:
            logger.error(f"Handler error: {e}")


if __name__ == "__main__":
    asyncio.run(stdio_handler())