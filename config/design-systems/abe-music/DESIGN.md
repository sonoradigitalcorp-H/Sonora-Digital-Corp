# ABE Music — Design System

## Tokens

```css
:root {
  /* Brand */
  --abe-gold: #FFD700;
  --abe-gold-light: #FFE44D;
  --abe-gold-dark: #B8960F;
  --abe-bg: #0a0a12;
  --abe-surface: rgba(255,255,255,.05);
  --abe-surface-hover: rgba(255,255,255,.08);
  --abe-border: rgba(255,255,255,.1);
  --abe-text: #f0f0f0;
  --abe-text-secondary: rgba(255,255,255,.4);
  --abe-accent: #7c5cfc;
  --abe-success: #34d399;
  --abe-error: #ff3b5c;
  --abe-gradient: linear-gradient(135deg, #FFD700, #7c5cfc);
  --abe-radius: 16px;
  --abe-radius-sm: 10px;
  --abe-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Glassmorphism */
.glass {
  background: var(--abe-surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--abe-border);
  border-radius: var(--abe-radius);
}

.glass-sm {
  background: var(--abe-surface-hover);
  backdrop-filter: blur(12px);
  border: 1px solid var(--abe-border);
  border-radius: var(--abe-radius-sm);
}

/* Gradients */
.gradient-gold {
  background: linear-gradient(135deg, var(--abe-gold), var(--abe-gold-dark));
}

.gradient-accent {
  background: linear-gradient(135deg, var(--abe-accent), #5a3dcc);
}

/* Stats */
.stat-card { padding: 1.2rem; }
.stat-card .label {
  font-size: .7rem;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--abe-text-secondary);
}
.stat-card .value {
  font-size: 1.8rem;
  font-weight: 700;
  letter-spacing: -.02em;
}

/* Artist Cards */
.artist-card { padding: 1.2rem; cursor: pointer; transition: all .2s; }
.artist-card:hover {
  border-color: var(--abe-gold);
  transform: translateY(-2px);
}
.artist-card .avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, var(--abe-gold), var(--abe-gold-dark));
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.2rem;
}

/* Tags */
.tag { display: inline-block; padding: .1rem .4rem; border-radius: 4px; font-size: .65rem; }
.tag-gold { background: rgba(255,215,0,.15); color: var(--abe-gold); }
.tag-success { background: rgba(52,211,153,.15); color: var(--abe-success); }
.tag-error { background: rgba(255,59,92,.15); color: var(--abe-error); }
.tag-accent { background: rgba(124,92,252,.15); color: var(--abe-accent); }

/* Progress Bars */
.bar { height: 6px; border-radius: 3px; background: rgba(255,255,255,.06); overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; }
.bar-gold { background: var(--abe-gold); }
.bar-accent { background: var(--abe-accent); }
.bar-success { background: var(--abe-success); }

/* Buttons */
.btn {
  padding: .5rem 1rem; border-radius: var(--abe-radius-sm);
  font-family: var(--abe-font); font-size: .8rem; font-weight: 500;
  cursor: pointer; border: none; transition: all .15s;
}
.btn-gold { background: var(--abe-gold); color: #000; }
.btn-gold:hover { opacity: .85; }
.btn-ghost {
  background: transparent; border: 1px solid var(--abe-border);
  color: var(--abe-text);
}
.btn-ghost:hover { border-color: var(--abe-gold); }
```

