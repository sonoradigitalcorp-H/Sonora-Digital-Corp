# Feature Specification: Hermes One — Potencial Máximo

**Feature Branch**: `005-hermes-potencial-maximo`

**Created**: 2026-06-11

**Status**: Draft

**Input**: Full optimization of the Hermes One ecosystem — Desktop (Electron), Office productivity, Kanban multi-agent orchestration, Models & Providers, Memory capabilities, Cron schedules, and Gateway multi-platform settings.

---

## User Scenarios & Testing

### User Story 1 — Desktop + Office Setup (Priority: P1)

The user configures Hermes One Desktop (Electron) as the central interface with full tool access, office productivity integration (Obsidian, Linear, Google Workspace), and multi-monitor support.

**Why this priority**: Desktop is the primary interface. Without it configured, the user's daily workflow is incomplete.

**Independent Test**: Launch Hermes One Desktop, verify all tools load, verify Linear MCP shows issues, verify Obsidian vault is accessible.

**Acceptance Scenarios**:
1. **Given** Hermes One Desktop installed, **When** launched, **Then** it connects to the Hermes Gateway API and displays the chat interface.
2. **Given** Linear MCP configured, **When** user asks for issues, **Then** Hermes queries Linear and returns results.
3. **Given** Obsidian vault path configured, **When** user asks to save/search notes, **Then** Hermes reads/writes from the vault.
4. **Given** dual-monitor setup, **When** Hermes One opens, **Then** it appears on the external monitor (1920x1080).

---

### User Story 2 — Models & Providers Optimization (Priority: P1)

The user has deepseek-v4-flash via opencode-go as primary provider. The system needs fallback model for resilience, and auxiliary models for vision/compression/search.

**Why this priority**: Without model resilience, a single provider outage stops the entire system.

**Independent Test**: Simulate primary provider failure → observe automatic fallback to secondary provider.

**Acceptance Scenarios**:
1. **Given** primary provider (opencode-go/deepseek-v4-flash) is online, **When** user sends a message, **Then** it routes through primary.
2. **Given** primary provider returns 429/503, **When** configured fallback exists, **Then** it routes to fallback automatically.
3. **Given** vision task required, **When** auxiliary vision provider is configured, **Then** it processes images without using primary model.
4. **Given** context compression triggers, **When** auxiliary compression provider is configured, **Then** compression uses the designated model.

---

### User Story 3 — Multi-Profile Kanban System (Priority: P2)

The user sets up multiple Hermes profiles (worker, research, cron) with a Kanban board for task orchestration and parallel work execution.

**Why this priority**: Kanban enables parallel multi-agent workflows. Depends on multi-profile setup.

**Independent Test**: Create a kanban task on one profile, claim and complete it from another profile, verify the board reflects the lifecycle.

**Acceptance Scenarios**:
1. **Given** two Hermes profiles exist, **When** a kanban task is created assigned to profile B, **Then** profile B can claim and execute it.
2. **Given** a task is completed on the board, **When** the orchestrator checks, **Then** the task shows `done` status with summary.
3. **Given** parallel tasks with no dependencies, **When** created, **Then** they can run concurrently.
4. **Given** a task fails, **When** retry is configured, **Then** the dispatcher retries up to failure_limit times.

---

### User Story 4 — Memory Capabilities (Priority: P2)

The user configures persistent cross-session memory with provider backend (built-in or Honcho) and user profile memory.

**Why this priority**: Memory is what makes Hermes learn across sessions. Without it, every conversation starts from zero.

**Independent Test**: Save a fact in session 1, start session 2, ask about it → verify recall.

**Acceptance Scenarios**:
1. **Given** memory enabled, **When** user shares a preference, **Then** it's saved to persistent memory.
2. **Given** a new session starts, **When** user asks about previously saved info, **Then** Hermes recalls it from memory.
3. **Given** user profile enabled, **When** user introduces themselves, **Then** profile updates and persists.
4. **Given** memory provider configured (built-in/honcho/mem0), **When** system starts, **Then** it connects to the provider without errors.

---

### User Story 5 — Cron Schedules & Automation (Priority: P2)

The user configures scheduled jobs for system health monitoring, resource tracking, and business automation.

**Why this priority**: Cron jobs run the ecosystem autonomously without manual intervention.

**Independent Test**: Create a cron job that runs every 5 minutes, verify it fires at least twice.

**Acceptance Scenarios**:
1. **Given** a cron job is created with `"every 5m"` schedule, **When** time passes, **Then** the job runs on schedule.
2. **Given** a cron job monitors service health, **When** a service is down, **Then** it reports the failure.
3. **Given** a cron job delivers to Telegram, **When** it runs, **Then** the message arrives in the configured chat.
4. **Given** a cron job has a script, **When** the script exits non-zero, **Then** an error alert is delivered.

---

### User Story 6 — Gateway Multi-Platform Settings (Priority: P1)

The user configures the Hermes Gateway as a systemd service with Telegram and WhatsApp connected, proper security, and cross-platform message routing.

**Why this priority**: Gateway is how users interact with Hermes from anywhere. Depends on stable systemd service.

**Independent Test**: Send a message from Telegram, verify response comes back through WhatsApp.

**Acceptance Scenarios**:
1. **Given** gateway running as systemd, **When** system reboots, **Then** gateway auto-starts.
2. **Given** a Telegram message received, **When** processed, **Then** response delivers back to Telegram within 10s.
3. **Given** a WhatsApp message received (self-chat mode), **When** processed, **Then** response delivers back to WhatsApp.
4. **Given** approvals mode set to `smart`, **When** a low-risk command is requested, **Then** it auto-approves; when high-risk, it prompts the user.

---

### Edge Cases

- **Desktop crashes**: Hermes One must reconnect to the gateway on relaunch without data loss.
- **All providers down**: must report degraded state clearly, not hang or crash.
- **Kanban dispatcher crashes**: pending tasks must survive restart (SQLite persistence).
- **Memory provider offline**: must fall back to built-in in-memory store transparently.
- **Cron job hangs (>180s)**: must be killed and alert sent, not block the scheduler.
- **Gateway port conflict**: must detect and report the conflicting process.
- **Multiple profiles writing same memory**: tenant isolation must prevent context leakage.

## Requirements

### Functional Requirements

**Desktop Setup**
- **FR-001**: Hermes One Desktop MUST auto-connect to the configured gateway API.
- **FR-002**: The system MUST support Linear MCP for issue tracking.
- **FR-003**: The system MUST support Obsidian vault integration for notes.

**Models & Providers**
- **FR-004**: The system MUST have a primary model provider configured.
- **FR-005**: The system MUST support at least one fallback provider for resilience.
- **FR-006**: Auxiliary models (vision, compression) MUST be independently configurable.

**Kanban**
- **FR-007**: The board MUST support cross-profile task assignment.
- **FR-008**: Tasks MUST support dependency chains (parent/child).
- **FR-009**: The dispatcher MUST retry failed tasks up to configurable limit.

**Memory**
- **FR-010**: Persistent memory MUST survive across sessions.
- **FR-011**: User profile memory MUST be independently toggleable.
- **FR-012**: Memory provider MUST be configurable (built-in, Honcho, Mem0).

**Schedules**
- **FR-013**: Cron jobs MUST support both duration and cron-expression schedules.
- **FR-014**: Cron jobs MUST support multi-platform delivery.
- **FR-015**: Cron jobs MUST have a 3-minute hard interrupt timeout.

**Gateway**
- **FR-016**: The gateway MUST run as a systemd service for auto-recovery.
- **FR-017**: Both Telegram and WhatsApp platforms MUST be operational.
- **FR-018**: Approvals mode MUST be configurable (manual/smart/off).
