<script lang="ts">
  import { OrbMachine } from '$lib/orb-machine.svelte';
  import { KernelClient, type KernelMessage, type KernelResponse } from '$lib/kernel-client';
  import Orb from '$components/orb/Orb.svelte';

  let input = $state('');
  let messages: { role: string; text: string }[] = $state([]);

  const orb = new OrbMachine();
  const kernel = new KernelClient();

  kernel.onStateChange((msg: KernelMessage) => {
    orb.transition(msg.state as any, { message: msg.message, progress: msg.progress, actions: msg.actions });
  });

  kernel.onResult((result: KernelResponse) => {
    messages = [...messages, { role: 'assistant', text: JSON.stringify(result.output || result, null, 2) }];
    orb.complete('Done');
    setTimeout(() => orb.reset(), 2000);
  });

  $effect(() => { kernel.connect(); });

  function send() {
    if (!input.trim()) return;
    messages = [...messages, { role: 'user', text: input }];
    orb.think();
    kernel.send(input);
    input = '';
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  }
</script>

<div class="chat-container">
  <header class="chat-header">
    <Orb state={orb.state} message={orb.message} progress={orb.progress} />
    <h1>Hermes</h1>
  </header>

  <main class="messages">
    {#each messages as msg}
      <div class="message {msg.role}">
        {msg.text}
      </div>
    {/each}
  </main>

  <footer class="chat-input">
    <textarea
      bind:value={input}
      onkeydown={handleKeydown}
      placeholder="Type a message..."
      rows="1"
    ></textarea>
    <button onclick={send} disabled={!input.trim()}>Send</button>
  </footer>
</div>

<style>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 800px;
    margin: 0 auto;
    font-family: system-ui, sans-serif;
  }

  .chat-header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-bottom: 1px solid #eee;
  }

  .chat-header h1 {
    margin: 0.5rem 0 0;
    font-size: 1.2rem;
    color: #333;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .message {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    max-width: 80%;
    line-height: 1.4;
  }

  .message.user {
    background: #3b82f6;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  }

  .message.assistant {
    background: #f3f4f6;
    color: #1f2937;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
    white-space: pre-wrap;
    font-size: 0.9rem;
  }

  .chat-input {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    border-top: 1px solid #eee;
  }

  .chat-input textarea {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    resize: none;
    font-family: inherit;
    font-size: 0.95rem;
  }

  .chat-input button {
    padding: 0.75rem 1.5rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
  }

  .chat-input button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
