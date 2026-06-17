/* JARVIS Web UI — Main Application Script */

// ===== State =====
const state = {
    sessions: [],
    currentSessionId: 'default',
    messages: [],
    streaming: false,
    eventSource: null,
    workspacePath: '.',
    gitStatus: null,
    filters: { pinned: null, project: null, tag: null },
    tokenCount: 0,
    maxTokens: 8192,
    voice: {
        listening: false,
        recognition: null,
        wakeEnabled: true,
        wakeRecognition: null,
        interim: '',
        volume: 0,
        ttsEnabled: true,
    },
};

// ===== DOM References =====
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const DOM = {};

function initDOM() {
    DOM.sessionList = $('#session-list');
    DOM.sessionSearch = $('#session-search');
    DOM.chatMessages = $('#chat-messages');
    DOM.chatInput = $('#chat-input');
    DOM.sendBtn = $('#send-btn');
    DOM.voiceBtn = $('#voice-btn');
    DOM.streamIndicator = $('#streaming-indicator');
    DOM.workspaceTree = $('#workspace-tree');
    DOM.filePreview = $('#file-preview');
    DOM.breadcrumb = $('#workspace-breadcrumb');
    DOM.gitStatus = $('#git-status');
    DOM.connectionDot = $('#connection-dot');
    DOM.tokenCount = $('#token-count');
    DOM.tokenFill = $('#token-fill');
    DOM.newSessionBtn = $('#new-session-btn');
    DOM.statusModel = $('#status-model');
    DOM.statusLatency = $('#status-latency');
    DOM.statusServices = $('#status-services');
    DOM.filterPinned = $('#filter-pinned');
    DOM.filterProjects = $('#filter-projects');
    DOM.commandInput = null;
}

// ===== API Helper =====
const API = {
    base: '',

    async get(path) {
        const r = await fetch(`${this.base}${path}`);
        if (!r.ok) throw new Error(`GET ${path}: ${r.status}`);
        return r.json();
    },

    async post(path, data) {
        const r = await fetch(`${this.base}${path}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!r.ok) throw new Error(`POST ${path}: ${r.status}`);
        return r.json();
    },

    async put(path, data) {
        const r = await fetch(`${this.base}${path}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!r.ok) throw new Error(`PUT ${path}: ${r.status}`);
        return r.json();
    },

    async del(path) {
        const r = await fetch(`${this.base}${path}`, { method: 'DELETE' });
        if (!r.ok) throw new Error(`DELETE ${path}: ${r.status}`);
        return r.json();
    },
};

// ===== Session Management =====

async function loadSessions() {
    try {
        const params = new URLSearchParams();
        if (state.filters.pinned !== null) params.set('pinned', state.filters.pinned);
        if (state.filters.project) params.set('project', state.filters.project);
        if (state.filters.tag) params.set('tag', state.filters.tag);

        const data = await API.get(`/api/sessions?${params}`);
        state.sessions = data.sessions || [];
        renderSessionList();
    } catch (e) {
        console.error('Failed to load sessions:', e);
    }
}

async function createSession() {
    const title = prompt('Nombre de la nueva sesión:');
    if (!title) return;

    try {
        const session = await API.post('/api/sessions', { title });
        state.sessions.unshift(session);
        await switchSession(session.id);
        renderSessionList();
    } catch (e) {
        console.error('Failed to create session:', e);
    }
}

async function switchSession(sessionId) {
    state.currentSessionId = sessionId;
    try {
        const session = await API.get(`/api/sessions/${sessionId}`);
        state.messages = session.messages || [];
        renderMessages();
        renderSessionList();
        updateTokenCounter(session.token_count || 0);
    } catch (e) {
        console.error('Failed to load session:', e);
    }
}

async function togglePin(sessionId) {
    try {
        const result = await API.post(`/api/sessions/${sessionId}/pin`);
        await loadSessions();
    } catch (e) {
        console.error('Failed to toggle pin:', e);
    }
}

async function toggleArchive(sessionId) {
    try {
        await API.post(`/api/sessions/${sessionId}/archive`);
        // Remove from visible list
        state.sessions = state.sessions.filter(s => s.id !== sessionId);
        renderSessionList();
        if (state.currentSessionId === sessionId) {
            const next = state.sessions[0];
            if (next) await switchSession(next.id);
        }
    } catch (e) {
        console.error('Failed to archive:', e);
    }
}

async function deleteSession(sessionId) {
    if (!confirm('¿Eliminar esta sesión?')) return;
    try {
        await API.del(`/api/sessions/${sessionId}`);
        state.sessions = state.sessions.filter(s => s.id !== sessionId);
        renderSessionList();
        if (state.currentSessionId === sessionId) {
            const next = state.sessions[0];
            if (next) await switchSession(next.id);
        }
    } catch (e) {
        console.error('Failed to delete:', e);
    }
}

async function exportSession(sessionId, format) {
    try {
        const r = await fetch(`/api/sessions/${sessionId}/export/${format}`);
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `session.${format}`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error('Export failed:', e);
    }
}

function renderSessionList() {
    if (!DOM.sessionList) return;

    const search = (DOM.sessionSearch?.value || '').toLowerCase();
    let filtered = state.sessions;

    if (search) {
        filtered = filtered.filter(s =>
            s.title?.toLowerCase().includes(search) ||
            (s.tags || []).some(t => t.includes(search))
        );
    }

    DOM.sessionList.innerHTML = filtered.map(s => `
        <div class="session-item ${s.id === state.currentSessionId ? 'active' : ''}"
             onclick="switchSession('${s.id}')"
             oncontextmenu="showSessionMenu(event, '${s.id}')">
            <div class="session-item-title">
                ${s.pinned ? '📌 ' : ''}${escapeHtml(s.title || 'Sin título')}
            </div>
            <div class="session-item-meta">
                ${s.project ? `<span class="filter-tag project-${s.project?.toLowerCase()}">#${s.project}</span> ` : ''}
                ${(s.tags || []).map(t => `#${t}`).join(' ')}
                · ${s.token_count || 0} tokens
            </div>
            ${s.pinned ? '<span class="pin-icon pinned">📌</span>' : ''}
        </div>
    `).join('');
}

// ===== Chat =====

function renderMessages() {
    if (!DOM.chatMessages) return;
    DOM.chatMessages.innerHTML = state.messages.map(m => `
        <div class="message ${m.role}">
            <div class="message-header">
                <span class="message-role-icon">${m.role === 'user' ? '👤' : m.role === 'assistant' ? '🤖' : '⚙️'}</span>
                ${m.role === 'user' ? 'Tú' : m.role === 'assistant' ? 'JARVIS' : 'Sistema'}
                <span style="margin-left:auto;font-size:10px;">${formatTime(m.timestamp)}</span>
            </div>
            <div class="message-content">${renderMarkdown(m.content)}</div>
        </div>
    `).join('');
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
}

function renderMarkdown(text) {
    if (!text) return '';
    // Escape HTML
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Tables
    html = html.replace(/\|(.+)\|\n\|[-| ]+\|\n((?:\|.+\|\n?)*)/g, (match, header, rows) => {
        const headers = header.split('|').filter(h => h.trim()).map(h => `<th>${h.trim()}</th>`).join('');
        const rowHtml = rows.trim().split('\n').map(row => {
            const cells = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('');
        return `<table><thead><tr>${headers}</tr></thead><tbody>${rowHtml}</tbody></table>`;
    });

    // Lists
    html = html.replace(/^[\d]+\.\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/^[-*]\s+(.*)$/gm, '<li>$1</li>');

    // Newlines to paragraphs
    html = html.split('\n\n').map(p => {
        const trimmed = p.trim();
        if (!trimmed) return '';
        if (trimmed.startsWith('<')) return trimmed;
        return `<p>${trimmed.replace(/\n/g, '<br>')}</p>`;
    }).join('\n');

    return html;
}

function appendToken(token) {
    if (!DOM.chatMessages) return;
    let lastMsg = DOM.chatMessages.lastElementChild;
    if (!lastMsg || !lastMsg.classList.contains('assistant')) {
        // Create new assistant message
        const div = document.createElement('div');
        div.className = 'message assistant';
        div.innerHTML = `
            <div class="message-header">
                <span class="message-role-icon">🤖</span>
                JARVIS
            </div>
            <div class="message-content"></div>
        `;
        DOM.chatMessages.appendChild(div);
        lastMsg = div;
    }

    const content = lastMsg.querySelector('.message-content');
    if (content) {
        content.textContent += token;
        // Re-render with markdown periodically
        DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
    }
}

function appendFullMessage(text) {
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.innerHTML = `
        <div class="message-header">
            <span class="message-role-icon">🤖</span>
            JARVIS
        </div>
        <div class="message-content">${renderMarkdown(text)}</div>
    `;
    DOM.chatMessages.appendChild(div);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
}

// ===== SSE Streaming =====

function sendMessage() {
    if (state.streaming) return;

    const text = DOM.chatInput?.value.trim();
    if (!text) return;

    DOM.chatInput.value = '';
    DOM.chatInput.style.height = 'auto';

    // Handle slash commands
    if (text.startsWith('/')) {
        handleCommand(text);
        return;
    }

    // Add user message immediately
    const userMsg = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
    };
    state.messages.push(userMsg);
    renderMessages();

    // Start SSE streaming
    startStream(text);
}

function startStream(message) {
    if (state.eventSource) {
        state.eventSource.close();
    }

    state.streaming = true;
    DOM.sendBtn.disabled = true;
    DOM.streamIndicator.classList.add('active');

    const sessionId = state.currentSessionId;
    const encodedMsg = encodeURIComponent(message);
    const url = `/api/chat/${sessionId}/stream?message=${encodedMsg}`;

    state.eventSource = new EventSource(url);

    state.eventSource.addEventListener('token', (event) => {
        const data = JSON.parse(event.data);
        appendToken(data.token);
    });

    state.eventSource.addEventListener('tool', (event) => {
        const data = JSON.parse(event.data);
        console.log(`Tool: ${data.tool} - ${data.status}`);
    });

    state.eventSource.addEventListener('done', (event) => {
        const data = JSON.parse(event.data);
        state.eventSource.close();
        state.eventSource = null;
        state.streaming = false;
        DOM.sendBtn.disabled = false;
        DOM.streamIndicator.classList.remove('active');

        // Update token counter
        if (data.usage) {
            updateTokenCounter(data.usage.tokens);
            if (data.usage.latency_ms) {
                DOM.statusLatency.textContent = `${data.usage.latency_ms}ms`;
            }
        }

        // Reload session to get persisted messages
        switchSession(state.currentSessionId);
    });

    state.eventSource.addEventListener('error', (event) => {
        console.error('SSE Error:', event);
        state.eventSource.close();
        state.eventSource = null;
        state.streaming = false;
        DOM.sendBtn.disabled = false;
        DOM.streamIndicator.classList.remove('active');
    });
}

// ===== Slash Commands =====

async function handleCommand(cmd) {
    const text = cmd;

    try {
        const result = await API.post('/api/commands', {
            command: text,
            session_id: state.currentSessionId,
        });

        if (result.type === 'clear') {
            state.messages = [];
            renderMessages();
            return;
        }

        appendFullMessage(result.content);
        state.messages.push({
            role: 'system',
            content: result.content,
            timestamp: new Date().toISOString(),
        });
    } catch (e) {
        console.error('Command error:', e);
        appendFullMessage(`Error ejecutando comando: ${e.message}`);
    }
}

// ===== Workspace File Browser =====

async function loadWorkspace(path) {
    try {
        const data = await API.get(`/api/files?path=${encodeURIComponent(path)}`);
        renderWorkspace(data);
    } catch (e) {
        console.error('Workspace error:', e);
    }
}

function renderWorkspace(data) {
    if (!DOM.workspaceTree) return;

    // Breadcrumb
    if (DOM.breadcrumb) {
        const parts = data.path.split('/');
        let cum = '';
        DOM.breadcrumb.innerHTML = parts.map((p, i) => {
            cum += (i === 0 ? '' : '/') + p;
            if (i === parts.length - 1) {
                return `<span>${p}</span>`;
            }
            return `<span onclick="loadWorkspace('${cum}')">${p}</span><span class="sep">/</span>`;
        }).join('');
    }

    if (data.type === 'file') {
        DOM.workspaceTree.innerHTML = '';
        DOM.filePreview.innerHTML = `<pre>${escapeHtml(data.content || 'No content')}</pre>`;
        return;
    }

    // Render directory tree
    DOM.workspaceTree.innerHTML = data.items.map(item => {
        const isDir = item.type === 'directory';
        const icon = isDir ? '📁' : getFileIcon(item.name);
        return `<li onclick="${isDir ? `loadWorkspace('${item.path}')` : `previewFile('${item.path}')`}"
                    class="${isDir ? '' : 'file-item'}">
            <span class="icon ${isDir ? 'dir-icon' : 'file-icon'}">${icon}</span>
            ${item.name}
            <span style="margin-left:auto;font-size:11px;color:var(--jarvis-text-dim);">
                ${isDir ? '' : formatSize(item.size)}
            </span>
        </li>`;
    }).join('');

    DOM.filePreview.innerHTML = `
        <div class="empty-state">
            <div class="icon">📂</div>
            <div>Selecciona un archivo para previsualizarlo</div>
            <div class="text-muted" style="font-size:12px;">${data.items.length} elementos</div>
        </div>
    `;
}

async function previewFile(path) {
    try {
        const data = await API.get(`/api/files?path=${encodeURIComponent(path)}`);
        if (data.type === 'file') {
            DOM.filePreview.innerHTML = `<pre>${escapeHtml(data.content || '')}</pre>`;
        }
    } catch (e) {
        DOM.filePreview.innerHTML = `<div class="empty-state"><div>Error: ${e.message}</div></div>`;
    }
}

// ===== Syntax Highlighting =====

function highlightCode(code, lang) {
    const keywords = {
        py: /\b(def|class|return|import|from|if|elif|else|for|while|try|except|finally|with|as|pass|None|True|False|async|await|print|raise|yield|lambda|in|not|and|or|is|del|break|continue|self|__init__)\b/g,
        js: /\b(function|const|let|var|return|if|else|for|while|do|switch|case|break|continue|new|this|class|extends|import|export|default|from|async|await|try|catch|throw|typeof|instanceof|null|undefined|true|false|Promise)\b/g,
        ts: /\b(function|const|let|var|return|if|else|for|while|do|switch|case|break|continue|new|this|class|extends|import|export|default|from|async|await|try|catch|throw|typeof|instanceof|null|undefined|true|false|interface|type|enum|implements|abstract|readonly|private|protected|public|static)\b/g,
        sh: /\b(if|then|else|elif|fi|for|while|do|done|case|esac|return|exit|export|source|echo|printf|read|set|unset|function|local|declare|typeset|select|until|in|break|continue)\b/g,
    };
    const langKeywords = keywords[lang] || /\b\w+\b/g;
    const strRe = /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)/g;
    const commentRe = lang === 'py' ? /(#.*)$/gm : /(\/\/.*$|\/\*[\s\S]*?\*\/)/gm;
    const numRe = /\b(\d+\.?\d*)\b/g;

    let escaped = escapeHtml(code);
    escaped = escaped.replace(strRe, '<span style="color:#98c379">$1</span>');
    escaped = escaped.replace(numRe, '<span style="color:#d19a66">$1</span>');
    escaped = escaped.replace(langKeywords, '<span style="color:#c678dd">$1</span>');
    escaped = escaped.replace(commentRe, '<span style="color:#5c6370;font-style:italic">$1</span>');
    return `<code>${escaped}</code>`;
}

function renderPreviewWithHighlight(content, filename) {
    const ext = filename.split('.').pop();
    const langMap = { py: 'py', js: 'js', ts: 'ts', jsx: 'js', tsx: 'ts', sh: 'sh', css: 'css', html: 'html', json: 'json', yml: 'yaml', yaml: 'yaml', md: 'md' };
    const lang = langMap[ext];
    if (lang) {
        return `<pre>${highlightCode(content, lang)}</pre>`;
    }
    return `<pre>${escapeHtml(content || '')}</pre>`;
}

// ===== Drag & Drop for Session Reordering =====

function setupSessionDragDrop() {
    const list = DOM.sessionList;
    if (!list) return;
    let dragItem = null;

    list.addEventListener('dragstart', (e) => {
        const li = e.target.closest('.session-item');
        if (!li) return;
        dragItem = li;
        li.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', li.dataset.sessionId);
    });

    list.addEventListener('dragend', (e) => {
        const li = e.target.closest('.session-item');
        if (li) li.classList.remove('dragging');
        dragItem = null;
        list.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    });

    list.addEventListener('dragover', (e) => {
        e.preventDefault();
        const li = e.target.closest('.session-item');
        if (!li || li === dragItem) return;
        const rect = li.getBoundingClientRect();
        const mid = rect.top + rect.height / 2;
        if (e.clientY < mid) {
            li.classList.add('drag-over');
            list.insertBefore(dragItem, li);
        } else {
            li.classList.remove('drag-over');
            if (li.nextSibling) {
                list.insertBefore(dragItem, li.nextSibling);
            } else {
                list.appendChild(dragItem);
            }
        }
    });

    list.addEventListener('dragleave', (e) => {
        const li = e.target.closest('.session-item');
        if (li) li.classList.remove('drag-over');
    });
}

// ===== Volume Meter =====

function createVolumeMeter() {
    const container = document.createElement('div');
    container.id = 'volume-meter';
    container.style.cssText = 'display:none;position:absolute;bottom:60px;left:50%;transform:translateX(-50%);width:200px;height:24px;background:var(--bg-tertiary);border:1px solid var(--border);border-radius:12px;overflow:hidden;z-index:100;';
    const fill = document.createElement('div');
    fill.id = 'volume-fill';
    fill.style.cssText = 'height:100%;width:0%;background:linear-gradient(90deg,var(--accent),var(--primary));transition:width 0.1s ease;border-radius:12px;';
    const label = document.createElement('span');
    label.id = 'volume-label';
    label.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--text-dim);';
    label.textContent = '🎤 Escuchando...';
    container.appendChild(fill);
    container.appendChild(label);
    document.querySelector('.chat-input-area')?.appendChild(container);
    return { container, fill, label };
}

function updateVolumeMeter(volume) {
    const meter = document.getElementById('volume-meter');
    const fill = document.getElementById('volume-fill');
    if (!meter || !fill) return;
    const pct = Math.min(volume * 100, 100);
    fill.style.width = `${pct}%`;
    if (pct > 70) fill.style.background = 'linear-gradient(90deg,var(--warning),var(--error))';
    else if (pct > 30) fill.style.background = 'linear-gradient(90deg,var(--accent),var(--primary))';
    else fill.style.background = 'linear-gradient(90deg,var(--primary-dim),var(--primary))';
}

function showVolumeMeter() {
    const meter = document.getElementById('volume-meter');
    if (meter) meter.style.display = 'block';
}

function hideVolumeMeter() {
    const meter = document.getElementById('volume-meter');
    if (meter) meter.style.display = 'none';
}

// ===== Settings Panel =====

function openSettings() {
    const modal = document.createElement('div');
    modal.className = 'settings-modal';
    modal.innerHTML = `
        <div class="settings-overlay"></div>
        <div class="settings-panel">
            <div class="settings-header">
                <h3>⚙️ Configuración</h3>
                <button class="btn btn-sm" onclick="this.closest('.settings-modal').remove()">✕</button>
            </div>
            <div class="settings-body">
                <div class="setting-group">
                    <h4>🎤 Voz</h4>
                    <label>Micrófono
                        <select id="setting-mic" class="setting-select">
                            <option value="default">Predeterminado</option>
                        </select>
                    </label>
                    <label>Idioma
                        <select id="setting-lang" class="setting-select">
                            <option value="es-MX">Español (MX)</option>
                            <option value="es-ES">Español (ES)</option>
                            <option value="en-US">English (US)</option>
                        </select>
                    </label>
                    <label>Sensibilidad wake word
                        <input type="range" id="setting-wake" min="0" max="100" value="50" class="setting-range" />
                    </label>
                    <label>Velocidad TTS
                        <input type="range" id="setting-tts-rate" min="50" max="150" value="100" class="setting-range" />
                    </label>
                    <label>Tiempo de escucha (segundos)
                        <input type="range" id="setting-voice-timeout" min="5" max="60" value="30" class="setting-range" />
                    </label>
                    <label class="setting-toggle">
                        <input type="checkbox" id="setting-tts" checked />
                        <span>Activar TTS</span>
                    </label>
                    <label class="setting-toggle">
                        <input type="checkbox" id="setting-wake-enabled" checked />
                        <span>Detección wake word</span>
                    </label>
                </div>
                <div class="setting-group">
                    <h4>🧠 Memoria</h4>
                    <label class="setting-toggle">
                        <input type="checkbox" id="setting-auto-save" checked />
                        <span>Guardar sesiones automáticamente</span>
                    </label>
                </div>
                <div class="setting-group">
                    <h4>🎨 Apariencia</h4>
                    <label>Tema
                        <select id="setting-theme" class="setting-select">
                            <option value="cyberpunk">Cyberpunk</option>
                            <option value="dark">Dark</option>
                            <option value="light">Light</option>
                        </select>
                    </label>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Load saved settings
    const saved = JSON.parse(localStorage.getItem('jarvis-settings') || '{}');
    if (saved.lang) document.getElementById('setting-lang').value = saved.lang;
    if (saved.ttsRate) document.getElementById('setting-tts-rate').value = saved.ttsRate;
    if (saved.wakeSensitivity) document.getElementById('setting-wake').value = saved.wakeSensitivity;
    if (saved.ttsEnabled !== undefined) document.getElementById('setting-tts').checked = saved.ttsEnabled;
    if (saved.wakeEnabled !== undefined) document.getElementById('setting-wake-enabled').checked = saved.wakeEnabled;
    if (saved.voiceTimeout) document.getElementById('setting-voice-timeout').value = saved.voiceTimeout;

    // Save on change
    document.querySelectorAll('.setting-select, .setting-range, .setting-toggle input').forEach(el => {
        el.addEventListener('change', saveSettings);
    });
}

function saveSettings() {
    const settings = {
        lang: document.getElementById('setting-lang')?.value || 'es-MX',
        ttsRate: document.getElementById('setting-tts-rate')?.value || 100,
        wakeSensitivity: document.getElementById('setting-wake')?.value || 50,
        ttsEnabled: document.getElementById('setting-tts')?.checked ?? true,
        wakeEnabled: document.getElementById('setting-wake-enabled')?.checked ?? true,
        voiceTimeout: document.getElementById('setting-voice-timeout')?.value || 30,
    };
    localStorage.setItem('jarvis-settings', JSON.stringify(settings));
    state.voice.ttsEnabled = settings.ttsEnabled;
    state.voice.wakeEnabled = settings.wakeEnabled;
    state.voice.timeout = parseInt(settings.voiceTimeout) * 1000;
}

// Apply syntax highlighting to all code blocks in messages
function applySyntaxHighlighting() {
    document.querySelectorAll('.message-content pre code').forEach(el => {
        if (el.dataset.highlighted) return;
        el.dataset.highlighted = 'true';
        const text = el.textContent;
        const parent = el.closest('pre');
        const lang = parent?.className?.match(/language-(\w+)/)?.[1];
        if (lang) {
            el.innerHTML = highlightCode(text, lang);
        }
    });
}

function getFileIcon(name) {
    const ext = name.split('.').pop();
    const icons = {
        py: '🐍', js: '📜', ts: '📘', jsx: '⚛️', tsx: '⚛️',
        html: '🌐', css: '🎨', json: '📋', yml: '⚙️', yaml: '⚙️',
        md: '📝', txt: '📄', sh: '💻', toml: '🔧', cypher: '🔗',
        pyc: '⚡',
    };
    return icons[ext] || '📄';
}

// ===== Git Status =====

async function loadGitStatus() {
    try {
        const status = await API.get('/api/files/git');
        state.gitStatus = status;
        if (DOM.gitStatus) {
            DOM.gitStatus.innerHTML = `
                <span>🔀</span>
                <span class="branch">${status.branch}</span>
                <span class="${status.dirty ? 'dirty' : 'clean'}">
                    ${status.dirty ? `· ${status.files.length} dirty` : '✅ clean'}
                </span>
            `;
        }
    } catch (e) {
        console.error('Git status error:', e);
    }
}

// ===== System Status =====

async function loadSystemStatus() {
    try {
        const status = await API.get('/api/status');
        if (DOM.connectionDot) {
            DOM.connectionDot.className = 'connection-dot';
        }
        if (DOM.statusServices) {
            DOM.statusServices.textContent = `Sesiones: ${status.services.sessions}`;
        }
    } catch (e) {
        if (DOM.connectionDot) {
            DOM.connectionDot.className = 'connection-dot disconnected';
        }
        console.error('Status check failed:', e);
    }
}

// ===== Token Counter =====

function updateTokenCounter(count) {
    if (count === undefined) return;
    state.tokenCount = count || 0;
    const pct = Math.min((state.tokenCount / state.maxTokens) * 100, 100);

    if (DOM.tokenCount) {
        DOM.tokenCount.textContent = `${state.tokenCount.toLocaleString()} / ${state.maxTokens.toLocaleString()}`;
    }
    if (DOM.tokenFill) {
        DOM.tokenFill.style.width = `${pct}%`;
        if (pct > 80) DOM.tokenFill.style.background = 'var(--jarvis-warning)';
        else if (pct > 95) DOM.tokenFill.style.background = 'var(--jarvis-error)';
        else DOM.tokenFill.style.background = 'var(--jarvis-primary)';
    }
}

// ===== Session Menu (Right Click) =====

function showSessionMenu(event, sessionId) {
    event.preventDefault();
    const menu = document.createElement('div');
    menu.style.cssText = `
        position:fixed;top:${event.clientY}px;left:${event.clientX}px;
        background:var(--jarvis-bg-tertiary);border:1px solid var(--jarvis-border);
        border-radius:var(--jarvis-radius);padding:4px 0;z-index:1000;
        min-width:160px;box-shadow:0 4px 12px rgba(0,0,0,0.5);
    `;

    const items = [
        { label: '📌 Toggle Pin', action: () => togglePin(sessionId) },
        { label: '📦 Archivar', action: () => toggleArchive(sessionId) },
        { label: '📋 Exportar MD', action: () => exportSession(sessionId, 'md') },
        { label: '📋 Exportar JSON', action: () => exportSession(sessionId, 'json') },
        { label: '📋 Duplicar', action: async () => {
            await API.post(`/api/sessions/${sessionId}/duplicate`);
            loadSessions();
        }},
        { label: '❌ Eliminar', action: () => deleteSession(sessionId) },
    ];

    items.forEach(item => {
        const btn = document.createElement('div');
        btn.textContent = item.label;
        btn.style.cssText = `
            padding:6px 12px;cursor:pointer;font-size:13px;
            transition:background var(--jarvis-transition);
        `;
        btn.onmouseenter = () => btn.style.background = 'var(--jarvis-bg)';
        btn.onmouseleave = () => btn.style.background = 'transparent';
        btn.onclick = () => {
            item.action();
            menu.remove();
        };
        menu.appendChild(btn);
    });

    document.body.appendChild(menu);
    document.addEventListener('click', () => menu.remove(), { once: true });
}

// ===== Voice Input =====

const WAKE_WORDS = ['hey jarvis', 'oye jarvis', 'hey jarv', 'oye jarv'];

function startWakeWordDetection() {
    if (!('webkitSpeechRecognition' in window)) {
        console.log('Wake word detection not supported');
        return;
    }

    if (state.voice.wakeRecognition) return;

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'es-MX';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                const text = event.results[i][0].transcript.toLowerCase().trim();
                if (WAKE_WORDS.some(w => text.includes(w))) {
                    console.log('🔊 Wake word detected:', text);
                    onWakeWordDetected();
                }
            }
        }
    };

    recognition.onerror = (e) => {
        console.warn('Wake word recognition error:', e.error);
        if (e.error === 'no-speech' || e.error === 'aborted') {
            // Restart after error
            setTimeout(startWakeWordDetection, 1000);
        }
    };

    recognition.onend = () => {
        // Continuous mode restarts automatically
    };

    state.voice.wakeRecognition = recognition;
    recognition.start();
    console.log('Wake word detection started (listening for "Hey JARVIS")');
}

function stopWakeWordDetection() {
    if (state.voice.wakeRecognition) {
        try { state.voice.wakeRecognition.stop(); } catch(e) {}
        state.voice.wakeRecognition = null;
    }
}

function onWakeWordDetected() {
    // Flash the header
    const header = document.querySelector('.header');
    if (header) {
        header.style.background = 'var(--jarvis-accent)';
        setTimeout(() => header.style.background = '', 1000);
    }

    // Beep feedback via Web Audio API
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.frequency.value = 880;
        gain.gain.value = 0.1;
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.15);
    } catch(e) {}

    // Auto-start voice input
    startVoiceInput();
}

function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window)) return;

    if (state.voice.listening) return;

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'es-MX';
    recognition.continuous = true;
    recognition.interimResults = true;

    DOM.voiceBtn.classList.add('listening');
    DOM.voiceBtn.title = 'Escuchando...';
    showVolumeMeter();

    let finalText = '';

    recognition.onresult = (event) => {
        let interim = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalText += event.results[i][0].transcript;
            } else {
                interim += event.results[i][0].transcript;
            }
        }

        // Show interim in chat input
        if (DOM.chatInput) {
            DOM.chatInput.placeholder = interim ? `🎤 ${interim}...` : 'Escuchando...';
        }
    };

    recognition.onend = () => {
        stopVoiceInput();
        if (finalText.trim()) {
            DOM.chatInput.value = finalText;
            DOM.chatInput.placeholder = 'Escribe un mensaje...';
            sendMessage();
        } else {
            DOM.chatInput.placeholder = 'Escribe un mensaje... (Enter para enviar)';
        }
    };

    recognition.onerror = (e) => {
        console.warn('Voice input error:', e.error);
        stopVoiceInput();
    };

    recognition.start();

    const voiceTimeout = state.voice.timeout || 30000;
    state.voice.recognition = recognition;
    state.voice.listening = true;

    setTimeout(() => {
        if (state.voice.listening) {
            try { recognition.stop(); } catch(e) {}
            stopVoiceInput();
        }
    }, voiceTimeout);
}

function stopVoiceInput() {
    DOM.voiceBtn.classList.remove('listening');
    DOM.voiceBtn.title = 'Activar voz';
    hideVolumeMeter();
    state.voice.listening = false;
    if (DOM.chatInput) {
        DOM.chatInput.placeholder = 'Escribe un mensaje... (Enter para enviar)';
    }
}

function toggleVoice() {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Voice input not supported. Try Chrome or Edge.');
        return;
    }

    if (state.voice.listening) {
        stopVoiceInput();
        return;
    }

    startVoiceInput();
}

// TTS: Read responses aloud
function speakResponse(text) {
    if (!state.voice.ttsEnabled || !text) return;
    if (!('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();

    const shortText = text.length > 300 ? text.slice(0, 300) + "..." : text;
    const utterance = new SpeechSynthesisUtterance(shortText);
    utterance.lang = 'es-MX';
    utterance.rate = 1.2;
    utterance.pitch = 0.9;

    const voices = window.speechSynthesis.getVoices();
    const spanishVoice = voices.find(v => v.lang.startsWith('es'));
    if (spanishVoice) utterance.voice = spanishVoice;

    window.speechSynthesis.speak(utterance);
}

// Attach TTS to messages
function setupTTSObserver() {
    const observer = new MutationObserver(() => {
        if (state.voice.ttsEnabled) {
            const lastMsg = DOM.chatMessages?.lastElementChild;
            if (lastMsg?.classList.contains('assistant')) {
                const text = lastMsg.querySelector('.message-content')?.textContent;
                if (text) speakResponse(text);
            }
        }
    });

    if (DOM.chatMessages) {
        observer.observe(DOM.chatMessages, { childList: true, subtree: false });
    }
}

// ===== Keyboard Shortcuts =====

function setupKeyboard() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter or Cmd+Enter: Send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            sendMessage();
        }
        // Escape: Close any open menu
        if (e.key === 'Escape') {
            const menus = document.querySelectorAll('[data-context-menu]');
            menus.forEach(m => m.remove());
            if (DOM.chatInput) DOM.chatInput.blur();
        }
        // Space in chat input while holding Space: push-to-talk
        if (e.key === ' ' && e.target === DOM.chatInput && DOM.chatInput.value === '') {
            // Don't trigger voice on first space in empty input
        }
    });
}

// ===== Auto-resize Textarea =====

function setupTextarea() {
    if (!DOM.chatInput) return;
    DOM.chatInput.addEventListener('input', () => {
        DOM.chatInput.style.height = 'auto';
        DOM.chatInput.style.height = Math.min(DOM.chatInput.scrollHeight, 120) + 'px';
    });
    DOM.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// ===== Filters =====

function setupFilters() {
    // Tag filters
    $$('.filter-tag').forEach(el => {
        el.addEventListener('click', () => {
            el.classList.toggle('active');
            // Simple filter by tag
            const tag = el.textContent.replace('#', '').trim();
            if (el.classList.contains('active')) {
                state.filters.tag = tag;
            } else {
                state.filters.tag = null;
            }
            loadSessions();
        });
    });

    // Search input debounce
    if (DOM.sessionSearch) {
        let debounceTimer;
        DOM.sessionSearch.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(renderSessionList, 200);
        });
    }

    // New session
    if (DOM.newSessionBtn) {
        DOM.newSessionBtn.addEventListener('click', createSession);
    }
}

// ===== Utility Functions =====

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function formatTime(ts) {
    if (!ts) return '';
    const d = new Date(ts);
    return d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
}

function formatSize(bytes) {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)}MB`;
}

// ===== Unified System Status =====

async function loadUnifiedStatus() {
    try {
        const data = await API.get('/api/unified/status');
        const { jarvis, hermes, openclaw, memory } = data;

        // Update service badges in header
        updateBadge('badge-hermes', hermes.status);
        updateBadge('badge-openclaw', openclaw.status);
        updateBadge('badge-llm', 'ok');

        // Update system grid
        updateSystemCard('jarvis', jarvis.status);
        updateSystemCard('hermes', hermes.status);
        updateSystemCard('openclaw', openclaw.status);
        updateSystemCard('memory', memory.neo4j ? 'ok' : 'warn');
        updateSystemCard('neo4j', memory.neo4j ? 'ok' : 'warn');
        updateSystemCard('qdrant', memory.qdrant ? 'ok' : 'warn');
    } catch (e) {
        console.error('Unified status error:', e);
    }
}

function updateBadge(id, status) {
    const badge = document.getElementById(id);
    if (!badge) return;
    const dot = badge.querySelector('.service-dot');
    if (!dot) return;
    dot.className = 'service-dot';
    if (status === 'ok') dot.classList.add('active');
    else if (status === 'offline') dot.classList.add('error');
    else dot.classList.add('warning');
}

function updateSystemCard(svc, status) {
    const card = document.querySelector(`.system-card[data-svc="${svc}"]`);
    if (!card) return;
    card.classList.remove('loading');
    card.setAttribute('data-status', status === 'ok' ? 'ok' : status === 'offline' ? 'error' : 'warn');
    const statusEl = card.querySelector('.card-status');
    if (statusEl) {
        const labels = { ok: '✅ Operativo', warn: '⚠️ Advertencia', error: '🔴 Offline' };
        statusEl.textContent = labels[status] || status;
    }
}

// ===== Approvals (Human-in-the-Loop) =====

async function loadApprovals() {
    try {
        const data = await API.get('/api/approvals');
        const list = document.getElementById('approval-list');
        const badge = document.getElementById('approval-badge');
        const pending = document.getElementById('pending-count');

        if (badge) badge.textContent = data.count || 0;
        if (pending) pending.textContent = data.count || 0;

        if (!list) return;

        if (data.count === 0) {
            list.innerHTML = '<div class="empty-state-sm">Sin aprobaciones pendientes</div>';
            return;
        }

        list.innerHTML = data.pending.map(item => `
            <div class="approval-item">
                <div class="action-name">${item.action}</div>
                <div class="action-details">${JSON.stringify(item.details)}</div>
                <div class="approval-buttons">
                    <button class="btn-approve" onclick="approveAction('${item.ticket}')">✓ Approve</button>
                    <button class="btn-reject" onclick="rejectAction('${item.ticket}')">✗ Reject</button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Approvals error:', e);
    }
}

async function approveAction(ticket) {
    await API.post(`/api/approvals/${ticket}/approve`, {});
    loadApprovals();
}

async function rejectAction(ticket) {
    await API.post(`/api/approvals/${ticket}/reject`, {});
    loadApprovals();
}

// ===== Tab Switching =====

function setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const content = document.getElementById(`tab-${tabName}`);
            if (content) content.classList.add('active');
            if (tabName === 'approval') loadApprovals();
            if (tabName === 'system') loadUnifiedStatus();
        });
    });
}

// ===== Initialization =====

async function init() {
    initDOM();

    // Load initial data
    await Promise.all([
        loadSessions(),
        loadWorkspace('.'),
        loadGitStatus(),
        loadSystemStatus(),
        loadUnifiedStatus(),
        loadApprovals(),
    ]);

    // Load default session
    if (state.sessions.length > 0) {
        await switchSession(state.sessions[0].id);
    }

    // Setup UI
    setupFilters();
    setupTextarea();
    setupKeyboard();
    setupTabs();

    // Start voice features
    if (state.voice.wakeEnabled) {
        startWakeWordDetection();
    }
    setupTTSObserver();

    // Settings button in header
    const settingsBtn = document.createElement('button');
    settingsBtn.className = 'btn btn-sm';
    settingsBtn.textContent = '⚙️';
    settingsBtn.title = 'Configuración';
    settingsBtn.onclick = openSettings;
    document.querySelector('.header-right')?.appendChild(settingsBtn);

    // Volume meter
    createVolumeMeter();

    // Drag & drop for sessions
    setupSessionDragDrop();

    // Syntax highlighting observer
    const hlObserver = new MutationObserver(applySyntaxHighlighting);
    hlObserver.observe(DOM.chatMessages, { childList: true, subtree: true });
    applySyntaxHighlighting();

    // Event listeners
    if (DOM.sendBtn) DOM.sendBtn.addEventListener('click', sendMessage);
    if (DOM.voiceBtn) DOM.voiceBtn.addEventListener('click', toggleVoice);

    // Periodic status checks
    setInterval(loadSystemStatus, 30000);
    setInterval(loadUnifiedStatus, 15000);
    setInterval(loadApprovals, 10000);

    console.log('JARVIS Unified Web UI initialized');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
