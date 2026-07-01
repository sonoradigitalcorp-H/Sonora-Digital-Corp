/**
 * Professional Design Tools — Open Design + Claude Design + Token Systems
 * 152 design systems de marcas reales para generar interfaces profesionales
 */

const fs = require('fs');
const path = require('path');

const DESIGNS_DIR = '/home/mystic/open-design/design-systems';
const CACHE_FILE = path.join(__dirname, '..', '..', 'state', 'design-systems-index.json');

function _scanSystems() {
  try {
    if (fs.existsSync(CACHE_FILE)) return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8'));
  } catch {}
  
  const systems = [];
  if (fs.existsSync(DESIGNS_DIR)) {
    for (const dir of fs.readdirSync(DESIGNS_DIR)) {
      const dirPath = path.join(DESIGNS_DIR, dir);
      if (!fs.statSync(dirPath).isDirectory()) continue;
      const tokensPath = path.join(dirPath, 'tokens.css');
      const htmlPath = path.join(dirPath, 'index.html');
      const readmePath = path.join(dirPath, 'README.md');
      
      let tokens = '', description = '', category = 'general';
      if (fs.existsSync(readmePath)) {
        const content = fs.readFileSync(readmePath, 'utf-8').substring(0, 300);
        description = content.split('\n').slice(0, 3).join(' ').substring(0, 200);
        if (content.toLowerCase().includes('dashboard')) category = 'dashboard';
        else if (content.toLowerCase().includes('landing') || content.toLowerCase().includes('page')) category = 'landing';
        else if (content.toLowerCase().includes('ecommerce') || content.toLowerCase().includes('shop')) category = 'ecommerce';
        else if (content.toLowerCase().includes('music') || content.toLowerCase().includes('entertainment')) category = 'entertainment';
        else if (content.toLowerCase().includes('finance') || content.toLowerCase().includes('bank')) category = 'finance';
        else if (content.toLowerCase().includes('social')) category = 'social';
      }
      if (fs.existsSync(tokensPath)) tokens = fs.readFileSync(tokensPath, 'utf-8').substring(0, 1000);
      
      systems.push({
        name: dir, category, description: description.substring(0, 200),
        has_tokens: fs.existsSync(tokensPath),
        has_html: fs.existsSync(htmlPath),
        tokens_preview: tokens.substring(0, 500),
      });
    }
  }
  
  try { fs.writeFileSync(CACHE_FILE, JSON.stringify(systems, null, 2)); } catch {}
  return systems;
}

function _recommendSystem(client, purpose) {
  const systems = _scanSystems();
  const t = (client + ' ' + purpose).toLowerCase();
  
  const scores = systems.map(s => {
    let score = 0;
    const name = s.name.toLowerCase();
    if (t.includes('music') && ['energy', 'spotify', 'apple', 'discord'].some(k => name.includes(k))) score += 5;
    if (t.includes('dashboard') && ['stripe', 'linear', 'vercel', 'notion'].some(k => name.includes(k))) score += 5;
    if (t.includes('landing') && ['arc', 'doodle', 'brutalism', 'bold', 'cafe'].some(k => name.includes(k))) score += 5;
    if (t.includes('ecommerce') && ['shopify', 'stripe', 'airbnb'].some(k => name.includes(k))) score += 5;
    if (t.includes('luxury') && ['bugatti', 'bentley', 'lamborghini', 'bmw', 'premium'].some(k => name.includes(k))) score += 5;
    if (t.includes('finance') && ['stripe', 'binance', 'visa', 'mastercard'].some(k => name.includes(k))) score += 5;
    if (t.includes('social') && ['tiktok', 'instagram', 'twitter', 'linkedin'].some(k => name.includes(k))) score += 5;
    if (t.includes('studio') || t.includes('brand') || t.includes('portfolio')) score += 3;
    return { ...s, score };
  });
  
  scores.sort((a, b) => b.score - a.score);
  return scores.slice(0, 3);
}

function _generateHTML(systemName, content, title) {
  const systemPath = path.join(DESIGNS_DIR, systemName);
  let tokensCSS = '';
  if (fs.existsSync(path.join(systemPath, 'tokens.css'))) {
    tokensCSS = fs.readFileSync(path.join(systemPath, 'tokens.css'), 'utf-8');
  }
  
  return `<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>${title || 'Page'} — ${systemName}</title>
<style>
${tokensCSS}
${content?.css || ''}
</style>
</head>
<body>
${content?.html || '<h1>Hello</h1>'}
</body>
</html>`;
}

const tools = {
  // ── List Design Systems ──
  design_list: {
    description: 'Lista los 152 design systems disponibles de marcas reales',
    inputSchema: { type: 'object', properties: { category: { type: 'string', enum: ['dashboard', 'landing', 'ecommerce', 'entertainment', 'finance', 'social', 'general'] } } },
    handler: async (args) => {
      const systems = _scanSystems();
      if (args.category) {
        return { systems: systems.filter(s => s.category === args.category), total: systems.length };
      }
      // Group by category
      const byCategory = {};
      systems.forEach(s => {
        if (!byCategory[s.category]) byCategory[s.category] = [];
        byCategory[s.category].push(s.name);
      });
      return { systems: byCategory, total: systems.length };
    },
  },

  // ── Recommend Design System ──
  design_recommend: {
    description: 'Recomienda el mejor design system para un proyecto',
    inputSchema: { type: 'object', properties: {
      client: { type: 'string', description: 'Cliente o marca' },
      purpose: { type: 'string', description: 'Propósito (dashboard, landing, ecommerce, etc.)' },
      style: { type: 'string', description: 'Estilo preferido (opcional)' },
    }, required: ['client', 'purpose'] },
    handler: async (args) => {
      const recommendations = _recommendSystem(args.client, args.purpose);
      return {
        client: args.client, purpose: args.purpose,
        recommendations: recommendations.map(r => ({
          name: r.name, category: r.category, score: r.score,
          has_tokens: r.has_tokens, has_html: r.has_html,
          description: r.description,
        })),
      };
    },
  },

  // ── Get Design System Tokens ──
  design_tokens: {
    description: 'Obtiene los tokens CSS de un design system',
    inputSchema: { type: 'object', properties: {
      system: { type: 'string', description: 'Nombre del design system' },
    }, required: ['system'] },
    handler: async (args) => {
      const tokensPath = path.join(DESIGNS_DIR, args.system, 'tokens.css');
      if (!fs.existsSync(tokensPath)) return { error: 'Design system no encontrado: ' + args.system };
      const tokens = fs.readFileSync(tokensPath, 'utf-8');
      return { system: args.system, tokens, variables: tokens.match(/--[\w-]+/g) || [] };
    },
  },

  // ── Generate Page with Design System ──
  design_generate: {
    description: 'Genera una página profesional usando un design system de marca real',
    inputSchema: { type: 'object', properties: {
      system: { type: 'string', description: 'Design system a usar' },
      title: { type: 'string', description: 'Título de la página' },
      type: { type: 'string', enum: ['dashboard', 'landing', 'pricing', 'portfolio', 'admin'] },
      content: { type: 'string', description: 'Descripción del contenido a generar' },
    }, required: ['system', 'title'] },
    handler: async (args) => {
      const systemPath = path.join(DESIGNS_DIR, args.system);
      if (!fs.existsSync(systemPath)) return { error: 'Design system no encontrado. Usá design_list para ver disponibles.' };
      
      const tokensPath = path.join(systemPath, 'tokens.css');
      const tokens = fs.existsSync(tokensPath) ? fs.readFileSync(tokensPath, 'utf-8') : '';
      
      // Generate appropriate layout based on type
      let layout = '';
      if (args.type === 'dashboard') {
        layout = `<div class="dashboard">
          <aside class="sidebar"><div class="logo">${args.title}</div>
            <nav><a href="#">Dashboard</a><a href="#">Analytics</a><a href="#">Settings</a></nav>
          </aside>
          <main class="content">
            <header><h1>${args.title}</h1></header>
            <div class="stats-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem">
              <div class="stat-card"><h3>Revenue</h3><div class="value">$0</div></div>
              <div class="stat-card"><h3>Users</h3><div class="value">0</div></div>
              <div class="stat-card"><h3>Active</h3><div class="value">0</div></div>
            </div>
            <p>${args.content || 'Complete dashboard with metrics and analytics.'}</p>
          </main>
        </div>`;
      } else {
        layout = `<header class="header">
          <div class="logo">${args.title}</div>
          <nav><a href="#">Home</a><a href="#">Features</a><a href="#">Pricing</a><a href="#">Contact</a></nav>
        </header>
        <section class="hero">
          <h1>${args.title}</h1>
          <p>${args.content || 'Professional page powered by ' + args.system + ' design system.'}</p>
          <a href="#" class="btn">Get Started</a>
        </section>
        <footer><p>&copy; ${new Date().getFullYear()} ${args.title}</p></footer>`;
      }
      
      const html = `<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>${args.title} — ${args.system}</title>
<style>
${tokens}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font-family,'Inter',sans-serif);background:var(--color-bg,#0a0a12);color:var(--color-text,#f0f0f0);-webkit-font-smoothing:antialiased}
${args.type === 'dashboard' ? `
.dashboard{display:grid;grid-template-columns:240px 1fr;min-height:100vh}
.sidebar{background:var(--color-surface,rgba(255,255,255,.05));padding:2rem 1rem;border-right:1px solid var(--color-border,rgba(255,255,255,.1))}
.sidebar .logo{font-size:1.2rem;font-weight:700;margin-bottom:2rem;color:var(--color-primary,#7c5cfc)}
.sidebar nav a{display:block;padding:.5rem;color:var(--color-text-secondary,rgba(255,255,255,.6));text-decoration:none;border-radius:6px;margin-bottom:.3rem}
.sidebar nav a:hover{background:rgba(255,255,255,.05);color:var(--color-text,#f0f0f0)}
.content{padding:2rem}
.content header{margin-bottom:2rem}
.stat-card{background:var(--color-surface,rgba(255,255,255,.05));border:1px solid var(--color-border,rgba(255,255,255,.1));border-radius:12px;padding:1.5rem}
.stat-card h3{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--color-text-secondary,rgba(255,255,255,.4));margin-bottom:.3rem}
.stat-card .value{font-size:1.8rem;font-weight:700}
` : `
.header{display:flex;justify-content:space-between;align-items:center;padding:1rem 2rem;border-bottom:1px solid var(--color-border,rgba(255,255,255,.1))}
.header .logo{font-size:1.3rem;font-weight:700;color:var(--color-primary,#7c5cfc)}
.header nav a{margin-left:1.5rem;color:var(--color-text-secondary,rgba(255,255,255,.6));text-decoration:none;font-size:.9rem}
.hero{text-align:center;padding:4rem 2rem;max-width:800px;margin:0 auto}
.hero h1{font-size:2.5rem;margin-bottom:.5rem}
.hero p{color:var(--color-text-secondary,rgba(255,255,255,.6));font-size:1.1rem;margin-bottom:2rem}
.hero .btn{display:inline-block;padding:.8rem 2rem;background:var(--color-primary,#7c5cfc);color:#fff;text-decoration:none;border-radius:8px;font-weight:600}
footer{text-align:center;padding:2rem;color:var(--color-text-secondary,rgba(255,255,255,.4));font-size:.8rem;border-top:1px solid var(--color-border,rgba(255,255,255,.1))}
`}
</style>
</head>
<body>${layout}</body>
</html>`;
      
      // Save to state
      const outDir = path.join(__dirname, '..', '..', 'state', 'designs');
      fs.mkdirSync(outDir, { recursive: true });
      const filename = args.system + '-' + Date.now() + '.html';
      fs.writeFileSync(path.join(outDir, filename), html);
      
      return {
        system: args.system, title: args.title, type: args.type || 'landing',
        html_preview: html.substring(0, 1500),
        saved_as: filename,
        variables: tokens.match(/--[\w-]+/g) || [],
      };
    },
  },

  // ── Claude Design Prompt Generator ──
  design_claude_prompt: {
    description: 'Genera un prompt profesional para Claude Design para crear UI completas',
    inputSchema: { type: 'object', properties: {
      project: { type: 'string', description: 'Nombre del proyecto' },
      type: { type: 'string', enum: ['dashboard', 'landing', 'saas', 'portfolio', 'ecommerce', 'admin'] },
      style: { type: 'string', description: 'Estilo visual (glassmorphism, neobrutalism, minimal, etc.)' },
      features: { type: 'string', description: 'Características principales' },
      colors: { type: 'string', description: 'Paleta de colores preferida' },
    }, required: ['project', 'type'] },
    handler: async (args) => {
      const designSystem = _recommendSystem(args.project, args.type)[0];
      
      const prompt = `Create a professional ${args.type} for "${args.project}".

Style: ${args.style || 'Modern glassmorphism with dark mode'}
Colors: ${args.colors || 'Dark background with vibrant accent'}
Features: ${args.features || 'Responsive, animated, professional'}
Design System Reference: ${designSystem?.name || 'Custom'}

Requirements:
- ${args.type === 'dashboard' ? 'Sidebar navigation, stat cards, data tables, charts' : 'Hero section, features grid, call-to-action'}
- Responsive design (mobile-first)
- Dark mode by default
- Smooth animations and transitions
- Professional typography
- Clean, modern aesthetic

Deliver: Complete single-file HTML with embedded CSS and JS.`;
      
      return {
        project: args.project, type: args.type,
        recommended_system: designSystem?.name || 'custom',
        prompt,
        design_system_tokens: designSystem?.tokens_preview || '',
        next_step: `Usá este prompt con Claude Design o ejecutá design_generate con system="${designSystem?.name || 'arc'}"`,
      };
    },
  },

  // ── Design System Search ──
  design_search: {
    description: 'Busca design systems por nombre o keyword',
    inputSchema: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] },
    handler: async (args) => {
      const systems = _scanSystems();
      const q = args.query.toLowerCase();
      const results = systems.filter(s => s.name.toLowerCase().includes(q) || s.description.toLowerCase().includes(q));
      return { query: args.query, results: results.slice(0, 20), total: results.length };
    },
  },
};

module.exports = { tools };
