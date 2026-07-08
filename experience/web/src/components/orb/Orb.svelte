<script lang="ts">
  import type { OrbState } from '$lib/orb-machine.svelte';

  let { state = 'idle' as OrbState, message = '' as string, progress = null as number | null } = $props();

  const COLORS: Record<OrbState, string> = {
    idle: '#a0a0a0',
    listening: '#3b82f6',
    thinking: '#8b5cf6',
    executing: '#f59e0b',
    completed: '#22c55e',
    alert: '#ef4444',
  };

  const color = $derived(COLORS[state] || COLORS.idle);
  const pulse = $derived(state === 'listening' || state === 'thinking');
  const showProgress = $derived(state === 'executing' && progress !== null);
</script>

<div class="orb-container">
  <div
    class="orb"
    style="background: {color}; box-shadow: 0 0 30px {color}40; animation: {pulse ? 'pulse 2s infinite' : 'none'}"
  >
    {#if showProgress}
      <div class="progress-ring">
        <svg viewBox="0 0 36 36" class="progress-svg">
          <path class="progress-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          <path class="progress-fill" stroke-dasharray="{progress}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
        </svg>
      </div>
    {/if}
  </div>
  {#if message}
    <p class="orb-message">{message}</p>
  {/if}
</div>

<style>
  .orb-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .orb {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    transition: background 0.3s ease, box-shadow 0.3s ease;
    position: relative;
  }

  .progress-ring {
    position: absolute;
    top: -8px;
    left: -8px;
    width: 136px;
    height: 136px;
  }

  .progress-svg {
    width: 100%;
    height: 100%;
  }

  .progress-bg {
    fill: none;
    stroke: #ffffff20;
    stroke-width: 2;
  }

  .progress-fill {
    fill: none;
    stroke: #ffffff;
    stroke-width: 2;
    stroke-linecap: round;
    transition: stroke-dasharray 0.5s ease;
  }

  .orb-message {
    color: #666;
    font-size: 0.9rem;
    text-align: center;
    max-width: 300px;
  }

  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
  }
</style>
