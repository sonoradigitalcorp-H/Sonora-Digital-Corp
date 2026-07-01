'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import { MessageCircle, X, Send, Loader2, Sparkles, ChevronDown } from 'lucide-react';

interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp: number;
}

interface ChatResponse {
  response: string;
  suggestions: string[];
}

const STORAGE_KEY = 'signal-chat-history';
const WELCOME_MESSAGE = {
  role: 'agent' as const,
  content: '👋 Welcome to **SIGNAL Assist**. I\'m your AI intelligence guide for this platform. Ask me anything about the current page, your data, or how things work — I adapt to your experience level.\n\nTry one of these to get started:',
  timestamp: Date.now(),
};

const PAGE_CONTEXT_HINTS: Record<string, string[]> = {
  '/dashboard': ['What do these KPIs mean?', 'How is the discovery score calculated?', 'What should I check first?'],
  '/command-center': ['How do I deploy a mission?', 'What agents are available?', 'Can I automate tasks?'],
  '/workflows': ['How do I create a workflow?', 'What templates exist?', 'Can I add approvals?'],
  '/agents': ['What does each agent do?', 'How do I check agent performance?', 'Can I customize agents?'],
  '/artists': ['How do I track a new artist?', 'What does the score mean?', 'Can I export artist data?'],
  '/discovery': ['How does discovery work?', 'What platforms are scanned?', 'Can I save discoveries?'],
  '/analytics': ['How do I create a chart?', 'Can I export data?', 'What metrics are available?'],
  '/alerts': ['How do I create an alert?', 'Can I get Slack notifications?', 'What triggers alerts?'],
  '/reports': ['How do I generate a report?', 'Can I schedule reports?', 'What templates exist?'],
  '/contracts': ['How do I draft a contract?', 'What does legal review check?', 'How do I send for signature?'],
  '/signings': ['What are the pipeline stages?', 'How do I advance a deal?', 'Can SIGNAL suggest offers?'],
  '/war-rooms': ['How do I open a War Room?', 'Who can I invite?', 'What intelligence is shown?'],
  '/market': ['What genres are trending?', 'Can I see regional data?', 'What is the Opportunity Index?'],
  '/playlists': ['What playlists are tracked?', 'How do playlist adds affect growth?', 'Can I get playlist alerts?'],
  '/finance': ['How do I track budget?', 'Can I see ROI projections?', 'What financial reports exist?'],
  '/settings': ['How do I invite team members?', 'What integrations are available?', 'How do I enable 2FA?'],
};

function formatMessage(text: string): string {
  // Bold
  let formatted = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic
  formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Line breaks
  formatted = formatted.replace(/\n/g, '<br />');
  return formatted;
}

export function ChatAgent() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const initialized = useRef(false);

  // Load saved history on mount
  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          const parsed = JSON.parse(saved) as Message[];
          setMessages(parsed);
        }
      } catch {
        // Ignore parse errors
      }
    }
  }, []);

  // Save history when messages change
  useEffect(() => {
    if (initialized.current && messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50)));
    }
  }, [messages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  // Contextual hints when page changes and panel is open
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const hints = PAGE_CONTEXT_HINTS[pathname] ?? PAGE_CONTEXT_HINTS['/dashboard'];
      setSuggestions(hints);
    }
  }, [pathname, isOpen, messages.length]);

  const sendMessage = useCallback(async (text: string) => {
    const userMsg: Message = { role: 'user', content: text, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setSuggestions([]);
    setIsLoading(true);

    try {
      const res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          page: pathname,
          history: messages.concat(userMsg).map(m => ({ role: m.role, content: m.content })),
        }),
      });

      if (!res.ok) throw new Error('API error');

      const data: ChatResponse = await res.json();
      const agentMsg: Message = { role: 'agent', content: data.response, timestamp: Date.now() };

      setMessages(prev => [...prev, agentMsg]);
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions);
      }
    } catch {
      const errorMsg: Message = {
        role: 'agent',
        content: 'I apologize — I encountered an issue processing your request. Please try again or reach out to support@signal.agent for help.',
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [pathname, messages]);

  const handleSubmit = useCallback((e?: React.FormEvent) => {
    e?.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    sendMessage(trimmed);
  }, [input, isLoading, sendMessage]);

  const handleSuggestion = useCallback((suggestion: string) => {
    sendMessage(suggestion);
  }, [sendMessage]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  const clearHistory = useCallback(() => {
    setMessages([]);
    setSuggestions(PAGE_CONTEXT_HINTS[pathname] ?? PAGE_CONTEXT_HINTS['/dashboard']);
    localStorage.removeItem(STORAGE_KEY);
  }, [pathname]);

  const togglePanel = useCallback(() => {
    setIsOpen(prev => {
      if (!prev && messages.length === 0) {
        // First open — show welcome + contextual hints
        setMessages([WELCOME_MESSAGE]);
        const hints = PAGE_CONTEXT_HINTS[pathname] ?? PAGE_CONTEXT_HINTS['/dashboard'];
        setSuggestions(hints);
      }
      return !prev;
    });
  }, [pathname, messages.length]);

  return (
    <>
      {/* Floating button */}
      <button
        onClick={togglePanel}
        className={`fixed bottom-5 right-5 z-50 flex items-center justify-center w-11 h-11 rounded-xl transition-all duration-200 shadow-lg ${
          isOpen
            ? 'bg-surface-hover border border-border scale-90 opacity-0 pointer-events-none'
            : 'bg-primary text-primary-foreground hover:bg-primary/90 active:scale-95'
        }`}
        aria-label={isOpen ? 'Close chat' : 'Open SIGNAL Assist'}
      >
        {isOpen ? <X className="h-5 w-5" /> : <MessageCircle className="h-5 w-5" />}
      </button>

      {/* Chat panel */}
      <div
        className={`fixed bottom-20 right-5 z-50 w-[360px] max-h-[600px] h-[60vh] rounded-xl glass shadow-2xl flex flex-col transition-all duration-200 origin-bottom-right ${
          isOpen
            ? 'opacity-100 scale-100 pointer-events-auto'
            : 'opacity-0 scale-95 pointer-events-none'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg signal-gradient flex items-center justify-center">
              <Sparkles className="h-3.5 w-3.5 text-white" />
            </div>
            <div>
              <p className="text-xs font-semibold tracking-tight">SIGNAL Assist</p>
              <p className="text-[10px] text-muted-foreground">AI Intelligence Guide</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={clearHistory}
              className="p-1.5 rounded-md hover:bg-surface-hover transition-colors text-muted-foreground hover:text-foreground"
              title="Clear conversation"
            >
              <ChevronDown className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={togglePanel}
              className="p-1.5 rounded-md hover:bg-surface-hover transition-colors text-muted-foreground hover:text-foreground"
              title="Close"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-10 h-10 rounded-xl signal-gradient flex items-center justify-center mb-3">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <p className="text-sm font-semibold tracking-tight mb-1">SIGNAL Assist</p>
              <p className="text-xs text-muted-foreground max-w-[240px]">
                Your AI intelligence guide. Ask me anything about the platform.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-[13px] leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-br-sm'
                    : 'bg-surface border border-border rounded-bl-sm'
                }`}
              >
                <div
                  dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
                  className={msg.role === 'user' ? 'text-primary-foreground' : 'text-foreground'}
                />
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-surface border border-border rounded-lg rounded-bl-sm px-3 py-2.5">
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          {/* Suggestions */}
          {suggestions.length > 0 && !isLoading && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestion(s)}
                  className="text-[11px] px-2.5 py-1 rounded-full bg-surface-hover border border-border text-muted-foreground hover:text-foreground hover:border-border/50 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="shrink-0 border-t border-border p-3">
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask SIGNAL anything..."
              disabled={isLoading}
              className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-xs placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary/40 transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-30 disabled:cursor-not-allowed transition-all shrink-0"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
          <p className="text-[9px] text-muted-foreground/40 mt-1.5 text-center">
            Responses are AI-generated. Verify critical information.
          </p>
        </div>
      </div>
    </>
  );
}
