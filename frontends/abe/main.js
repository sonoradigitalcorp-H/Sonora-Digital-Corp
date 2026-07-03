// ===== ABE Music Group - Application Logic =====
const API = "/api";
let token = localStorage.getItem("abe_token");

function navigate(e, path) {
  if (e) e.preventDefault();
  const hash = path || location.hash.slice(1) || "/";
  const clean = hash.replace("/", "") || "home";
  showPage(clean);
}

window.addEventListener("hashchange", () => navigate());
window.addEventListener("load", () => { navigate(); initNetwork(); });

function showPage(name) {
  const el = document.getElementById("page-" + name);
  if (!el) return;
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  el.classList.add("active");
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  const link = document.querySelector(`.nav-link[data-page="${name}"]`);
  if (link) link.classList.add("active");
  if (window.pageRenderers && window.pageRenderers[name]) {
    window.pageRenderers[name]();
  }
}

function initNetwork() {
  const canvas = document.getElementById("network-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let particles = [];
  let mouse = { x: 0, y: 0 };

  function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
  resize();
  window.addEventListener("resize", resize);
  document.addEventListener("mousemove", e => { mouse.x = e.clientX; mouse.y = e.clientY; });

  const count = Math.min(80, Math.floor(window.innerWidth * 0.04));
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * canvas.width, y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5, vy: (Math.random() - 0.5) * 0.5,
      r: Math.random() * 2 + 0.5
    });
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of particles) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      const dx = mouse.x - p.x, dy = mouse.y - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 200) { p.x -= dx * 0.005; p.y -= dy * 0.005; }
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(108, 92, 231, 0.3)";
      ctx.fill();
    }
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 150) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = "rgba(108, 92, 231, " + (0.1 * (1 - dist / 150)) + ")";
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(animate);
  }
  animate();
}

async function api(path, opts) {
  opts = opts || {};
  const h = { "Content-Type": "application/json" };
  if (opts.headers) Object.assign(h, opts.headers);
  if (token) h["Authorization"] = "Bearer " + token;
  const r = await fetch(API + path, { ...opts, headers: h });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail || r.statusText);
  }
  return r.json();
}

function toast(msg, type) {
  type = type || "success";
  const t = document.createElement("div");
  t.className = "toast toast-" + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

function loadingEl() { return '<div class="loading"><div class="spinner"></div></div>'; }

function statCard(label, value, icon) {
  return '<div class="stat-card"><div style="font-size:24px;margin-bottom:4px">' + icon + '</div><div class="stat-value">' + value + '</div><div class="stat-label">' + label + '</div></div>';
}

function dashboardCard(icon, value, label) {
  return '<div class="dashboard-card"><div class="dashboard-card-icon">' + icon + '</div><div class="dashboard-card-value">' + value + '</div><div class="dashboard-card-label">' + label + '</div></div>';
}

function serviceCard(s) {
  var icon = s.icon || "\u{1F4E6}";
  return '<div class="service-card"><div class="service-icon">' + icon + '</div><div class="service-title">' + s.title + '</div><div class="service-desc">' + (s.desc || s.description || "") + '</div></div>';
}

function artistCardHtml(a) {
  var img = a.image || "\u{1F3A4}";
  var extra = "";
  if (a.monthly_listeners) {
    extra = '<div class="artist-stats-row"><div class="artist-stat"><div class="artist-stat-value">' + Math.round(a.monthly_listeners/1000) + 'K</div><div class="artist-stat-label">Monthly</div></div></div>';
  }
  return '<div class="artist-card"><div class="artist-avatar">' + img + '</div><div class="artist-name">' + a.name + '</div><div class="artist-streams">' + Number(a.streams).toLocaleString() + ' streams</div><div class="artist-label">' + (a.label || "ABE Music Group") + '</div>' + extra + '</div>';
}

function renderHome() {
  var el = document.getElementById("page-home");
  if (!el || el.dataset.rendered) return;
  el.dataset.rendered = "1";
  el.innerHTML = '<section class="hero"><div><div class="hero-badge"><span class="hero-badge-dot"></span>Record Label & Artist Management</div><h1 class="hero-title"><span class="gradient-text">ABE Music Group</span></h1><p class="hero-subtitle">Distribution, management, and AI-powered growth for independent artists and labels. Based in Compton/Torrance, CA.</p><div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-bottom:40px"><a href="#/services" class="btn btn-primary">Our Services</a><a href="#/artists" class="btn btn-secondary">View Artists</a><a href="#/contact" class="btn btn-secondary">Contact Us</a></div><div id="home-stats" class="hero-stats">' + loadingEl() + '</div></div></section>';
  loadHomeStats();
}

async function loadHomeStats() {
  try {
    var d = await api("/stats");
    document.getElementById("home-stats").innerHTML = statCard("Artists", d.artists || 3, "\u{1F3A4}") + statCard("Total Streams", Number(d.total_streams || 119650000).toLocaleString(), "\u{1F3B5}") + statCard("Services", d.services || 6, "\u26A1");
  } catch(e) {
    document.getElementById("home-stats").innerHTML = statCard("Artists", "3", "\u{1F3A4}") + statCard("Total Streams", "119,650,000", "\u{1F3B5}") + statCard("Services", "6", "\u26A1");
  }
}

function renderServices() {
  var el = document.getElementById("page-services");
  if (!el || el.dataset.rendered) return;
  el.dataset.rendered = "1";
  el.innerHTML = '<div class="section"><div class="section-inner"><div class="section-header"><div class="section-tag">What We Offer</div><h2 class="section-title">Services</h2><p class="section-desc">End-to-end solutions for artists and labels.</p></div><div id="services-grid" class="services-grid">' + loadingEl() + '</div></div></div>';
  loadServices();
}

async function loadServices() {
  var fb = [
    { title: "Digital Distribution", desc: "Multi-platform distribution to Spotify, Apple Music, TikTok, and 150+ streaming services.", icon: "\u{1F3B5}" },
    { title: "Artist Management", desc: "Full-service management including booking, marketing, and career strategy.", icon: "\u{1F3A4}" },
    { title: "Revenue Intelligence", desc: "Real-time royalty tracking, revenue analytics, and predictive modeling.", icon: "\u{1F4CA}" },
    { title: "AI Content Factory", desc: "Automated music video production, visualizers, cover art, and social media content.", icon: "\u{1F3AC}" },
    { title: "Fan CRM", desc: "Fan engagement platform with email campaigns, analytics, and segmentation.", icon: "\u{1F91D}" },
    { title: "Merch Store", desc: "Print-on-demand merch, digital products, and subscription management.", icon: "\u{1F6D2}" }
  ];
  try {
    var d = await api("/services");
    document.getElementById("services-grid").innerHTML = d.map(serviceCard).join("");
  } catch(e) {
    document.getElementById("services-grid").innerHTML = fb.map(serviceCard).join("");
  }
}

function renderArtists() {
  var el = document.getElementById("page-artists");
  if (!el || el.dataset.rendered) return;
  el.dataset.rendered = "1";
  el.innerHTML = '<div class="section"><div class="section-inner"><div class="section-header"><div class="section-tag" style="color:var(--abe-gold)">Our Roster</div><h2 class="section-title">Artists</h2><p class="section-desc">Meet the talent powered by ABE Music Group.</p></div><div id="artists-grid" class="artists-grid">' + loadingEl() + '</div></div></div>';
  loadArtists();
}

async function loadArtists() {
  var fb = [
    { name: "Hector Rubio", streams: 115000000, label: "ABE Music Group", image: "\u{1F3B8}", monthly_listeners: 1100000 },
    { name: "Jesus Urquijo", streams: 4600000, label: "ABE Music Group", image: "\u{1F3B9}", monthly_listeners: 29800 },
    { name: "Javier Arvayo", streams: 50000, label: "ABE Music Group", image: "\u{1F3A4}", monthly_listeners: 981 }
  ];
  try {
    var r = await fetch(API + "/artists");
    var d = await r.json();
    document.getElementById("artists-grid").innerHTML = d.map(artistCardHtml).join("");
  } catch(e) {
    document.getElementById("artists-grid").innerHTML = fb.map(artistCardHtml).join("");
  }
}

function renderLogin() {
  var el = document.getElementById("page-login");
  if (!el || el.dataset.rendered) return;
  el.dataset.rendered = "1";
  el.innerHTML = '<div class="auth-container"><div class="auth-card glass-strong"><h2 class="auth-title">Welcome back</h2><p class="auth-subtitle">Sign in to your ABE Music account.</p><form id="login-form"><div class="form-group"><label class="form-label">Email</label><input class="form-input" type="email" id="login-email" placeholder="admin@abe.com" required></div><div class="form-group"><label class="form-label">Password</label><input class="form-input" type="password" id="login-password" placeholder="Enter your password" required></div><div id="login-error" class="form-error" style="display:none"></div><div class="form-actions"><button type="submit" class="btn btn-primary" style="width:100%;justify-content:center">Sign In</button></div></form><div style="margin-top:16px;text-align:center"><a href="#/contact" class="nav-link" style="font-size:13px">Don\'t have an account? Contact us</a></div></div></div>';
  setTimeout(function() {
    var form = document.getElementById("login-form");
    if (form) form.addEventListener("submit", handleLogin);
  }, 50);
}

async function handleLogin(e) {
  e.preventDefault();
  var email = document.getElementById("login-email").value;
  var password = document.getElementById("login-password").value;
  var errEl = document.getElementById("login-error");
  try {
    var r = await api("/auth/login", { method: "POST", body: JSON.stringify({ email: email, password: password }) });
    token = r.token;
    localStorage.setItem("abe_token", token);
    toast("Welcome back, " + r.user.name + "!");
    location.hash = "#/portal";
  } catch(err) {
    errEl.style.display = "block";
    errEl.textContent = err.message || "Invalid credentials";
  }
}

function renderPortal() {
  var el = document.getElementById("page-portal");
  if (!el) return;
  if (!token) {
    el.innerHTML = '<div class="auth-container"><div class="auth-card glass-strong" style="text-align:center"><h2 class="auth-title">Client Portal</h2><p class="auth-subtitle">Sign in to access your dashboard.</p><div style="margin-top:24px"><a href="#/login" class="btn btn-primary">Sign In</a></div></div></div>';
    el.dataset.rendered = "1";
    return;
  }
  if (el.dataset.rendered) return;
  el.dataset.rendered = "1";
  try { var payload = JSON.parse(atob(token.split(".")[1])); } catch(e) { payload = { name: "User" }; }
  el.innerHTML = '<div class="section"><div class="section-inner"><div class="admin-header"><h2 class="admin-title">Dashboard</h2><div style="display:flex;gap:8px;align-items:center"><span style="font-size:13px;color:var(--text-secondary)">' + (payload.name || "User") + '</span><button onclick="logout()" class="btn btn-sm btn-danger">Logout</button></div></div><div id="portal-content">' + loadingEl() + '</div></div></div>';
  loadPortal();
}

async function loadPortal() {
  try {
    var d = await api("/portal/dashboard");
    document.getElementById("portal-content").innerHTML = '<div class="dashboard-grid">' +
      dashboardCard("\u{1F3B5}", Number(d.total_streams || 0).toLocaleString(), "Total Streams") +
      dashboardCard("\u{1F4B0}", "$" + Number(d.revenue || 0).toLocaleString(), "Revenue") +
      dashboardCard("\u{1F4E2}", d.campaigns || 0, "Active Campaigns") +
      dashboardCard("\u{1F4C8}", (d.engagement || 0) + "%", "Engagement Rate") +
      '</div>';
  } catch(e) {
    document.getElementById("portal-content").innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:40px">Unable to load dashboard data.</p>';
  }
}

function logout() {
  token = null;
  localStorage.removeItem("abe_token");
  toast("Logged out");
  location.hash = "#/";
}

var adminTab = "services";

function renderAdmin() {
  var el = document.getElementById("page-admin");
  if (!el) return;
  if (!token) { renderPortal(); return; }
  if (el.dataset.rendered) return;
  el.dataset.rendered = "1";
  el.innerHTML = '<div class="section"><div class="section-inner"><div class="admin-header"><h2 class="admin-title">Admin Panel</h2></div><div class="admin-tabs"><button class="admin-tab ' + (adminTab==="services"?"active":"") + '" onclick="switchAdminTab(\'services\')">Services</button><button class="admin-tab ' + (adminTab==="artists"?"active":"") + '" onclick="switchAdminTab(\'artists\')">Artists</button></div><div id="admin-content">' + loadingEl() + '</div></div></div>';
  loadAdminTab();
}

function switchAdminTab(tab) {
  adminTab = tab;
  var el = document.getElementById("page-admin");
  if (el) delete el.dataset.rendered;
  renderAdmin();
}

async function loadAdminTab() {
  try {
    var payload = JSON.parse(atob(token.split(".")[1]));
    if (payload.role !== "admin") {
      document.getElementById("admin-content").innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:40px">Admin access required.</p>';
      return;
    }
  } catch(e) {
    document.getElementById("admin-content").innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:40px">Please sign in again.</p>';
    return;
  }
  if (adminTab === "services") {
    try {
      var d = await api("/services");
      document.getElementById("admin-content").innerHTML = '<div style="margin-bottom:16px"><button onclick="showAddService()" class="btn btn-primary btn-sm">+ Add Service</button></div><div class="admin-list">' + d.map(function(s) {
        var icon = s.icon || "\u{1F4E6}";
        var desc = (s.desc||"").substring(0,60);
        if ((s.desc||"").length > 60) desc += "...";
        return '<div class="admin-item"><div class="admin-item-left"><span class="admin-item-icon">' + icon + '</span><div><div class="admin-item-title">' + s.title + '</div><div class="admin-item-sub">' + desc + '</div></div></div><div class="admin-item-actions"><button onclick="deleteService(\'' + (s.id||s.title) + '\')" class="btn btn-sm btn-danger">Delete</button></div></div>';
      }).join("") + '</div>';
    } catch(e) {
      document.getElementById("admin-content").innerHTML = '<p style="color:var(--text-secondary)">Failed to load services.</p>';
    }
  } else {
    try {
      var r = await fetch(API + "/artists");
      var d = await r.json();
      document.getElementById("admin-content").innerHTML = '<div style="margin-bottom:16px"><button onclick="showAddArtist()" class="btn btn-primary btn-sm">+ Add Artist</button></div><div class="admin-list">' + d.map(function(a) {
        return '<div class="admin-item"><div class="admin-item-left"><span class="admin-item-icon">' + (a.image || "\u{1F3A4}") + '</span><div><div class="admin-item-title">' + a.name + '</div><div class="admin-item-sub">' + Number(a.streams).toLocaleString() + ' streams</div></div></div><div class="admin-item-actions"><button onclick="deleteArtist(\'' + (a.id||a.name) + '\')" class="btn btn-sm btn-danger">Delete</button></div></div>';
      }).join("") + '</div>';
    } catch(e) {
      document.getElementById("admin-content").innerHTML = '<p style="color:var(--text-secondary)">Failed to load artists.</p>';
    }
  }
}

function showAddService() {
  var overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.id = "modal-overlay";
  overlay.innerHTML = '<div class="modal glass-strong"><h3 class="modal-title">Add Service</h3><form id="add-service-form"><div class="form-group"><label class="form-label">Title</label><input class="form-input" name="title" placeholder="Service name" required></div><div class="form-group"><label class="form-label">Description</label><textarea class="form-input" name="description" rows="3" placeholder="Describe the service" required style="resize:vertical"></textarea></div><div class="form-group"><label class="form-label">Icon (emoji)</label><input class="form-input" name="icon" placeholder="\u{1F3B5}" value="\u{1F4E6}"></div><div class="form-actions" style="display:flex;gap:8px"><button type="submit" class="btn btn-primary" style="flex:1;justify-content:center">Create</button><button type="button" class="btn btn-secondary" onclick="closeModal()" style="flex:1;justify-content:center">Cancel</button></div></form></div>';
  document.body.appendChild(overlay);
  setTimeout(function() {
    var form = document.getElementById("add-service-form");
    if (form) {
      form.addEventListener("submit", async function(e) {
        e.preventDefault();
        var fd = new FormData(this);
        try {
          await api("/admin/services", { method: "POST", body: JSON.stringify({ title: fd.get("title"), description: fd.get("description"), icon: fd.get("icon") }) });
          toast("Service created!");
          closeModal();
          adminTab = "services";
          var el = document.getElementById("page-admin");
          if (el) delete el.dataset.rendered;
          renderAdmin();
        } catch(err) { toast(err.message, "error"); }
      });
    }
  }, 50);
}

function showAddArtist() {
  var overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.id = "modal-overlay";
  overlay.innerHTML = '<div class="modal glass-strong"><h3 class="modal-title">Add Artist</h3><form id="add-artist-form"><div class="form-group"><label class="form-label">Name</label><input class="form-input" name="name" placeholder="Artist name" required></div><div class="form-group"><label class="form-label">Streams</label><input class="form-input" name="streams" type="number" placeholder="0" value="0"></div><div class="form-group"><label class="form-label">Image (emoji)</label><input class="form-input" name="image" placeholder="\u{1F3A4}" value="\u{1F3A4}"></div><div class="form-actions" style="display:flex;gap:8px"><button type="submit" class="btn btn-primary" style="flex:1;justify-content:center">Create</button><button type="button" class="btn btn-secondary" onclick="closeModal()" style="flex:1;justify-content:center">Cancel</button></div></form></div>';
  document.body.appendChild(overlay);
  setTimeout(function() {
    var form = document.getElementById("add-artist-form");
    if (form) {
      form.addEventListener("submit", async function(e) {
        e.preventDefault();
        var fd = new FormData(this);
        try {
          await api("/admin/artists", { method: "POST", body: JSON.stringify({ name: fd.get("name"), streams: parseInt(fd.get("streams")) || 0, image: fd.get("image") }) });
          toast("Artist added!");
          closeModal();
          adminTab = "artists";
          var el = document.getElementById("page-admin");
          if (el) delete el.dataset.rendered;
          renderAdmin();
        } catch(err) { toast(err.message, "error"); }
      });
    }
  }, 50);
}

async function deleteService(id) {
  if (!confirm("Delete this service?")) return;
  try {
    await api("/admin/services/" + encodeURIComponent(id), { method: "DELETE" });
    toast("Service deleted");
    adminTab = "services";
    var el = document.getElementById("page-admin");
    if (el) delete el.dataset.rendered;
    renderAdmin();
  } catch(err) { toast(err.message, "error"); }
}

async function deleteArtist(id) {
  if (!confirm("Delete this artist?")) return;
  try {
    await api("/admin/artists/" + encodeURIComponent(id), { method: "DELETE" });
    toast("Artist deleted");
    adminTab = "artists";
    var el = document.getElementById("page-admin");
    if (el) delete el.dataset.rendered;
    renderAdmin();
  } catch(err) { toast(err.message, "error"); }
}

function closeModal() {
  var el = document.getElementById("modal-overlay");
  if (el) el.remove();
}

function renderContact() {
  var el = document.getElementById("page-contact");
  if (!el || el.dataset.rendered) return;
  el.dataset.rendered = "1";
  el.innerHTML = '<div class="section"><div class="section-inner"><div class="section-header"><div class="section-tag">Get In Touch</div><h2 class="section-title">Contact Us</h2><p class="section-desc">Ready to take your music career to the next level? Let\'s talk.</p></div><form id="contact-form" class="contact-form" style="max-width:520px;margin:0 auto"><div class="form-group"><label class="form-label">Name</label><input class="form-input" id="c-name" placeholder="Your full name" required></div><div class="form-group"><label class="form-label">Email</label><input class="form-input" type="email" id="c-email" placeholder="your@email.com" required></div><div class="form-group"><label class="form-label">Service Interest</label><select class="form-input" id="c-service"><option value="">Select a service...</option><option>Digital Distribution</option><option>Artist Management</option><option>Revenue Intelligence</option><option>AI Content Factory</option><option>Fan CRM</option><option>Merch Store</option><option>Other</option></select></div><div class="form-group"><label class="form-label">Message</label><textarea class="form-input" id="c-message" rows="4" placeholder="Tell us about your project..." required style="resize:vertical"></textarea></div><div class="form-actions"><button type="submit" class="btn btn-primary" style="width:100%;justify-content:center">Send Message</button></div></form></div></div>';
  setTimeout(function() {
    var form = document.getElementById("contact-form");
    if (form) form.addEventListener("submit", handleContact);
  }, 50);
}

async function handleContact(e) {
  e.preventDefault();
  var name = document.getElementById("c-name").value;
  var email = document.getElementById("c-email").value;
  var service = document.getElementById("c-service").value;
  var message = document.getElementById("c-message").value;
  var btn = e.target.querySelector("button[type=submit]");
  btn.textContent = "Sending...";
  btn.disabled = true;
  try {
    await api("/contact", { method: "POST", body: JSON.stringify({ name: name, email: email, service: service, message: message }) });
    toast("Message sent! We\'ll get back to you soon.");
    document.getElementById("c-name").value = "";
    document.getElementById("c-email").value = "";
    document.getElementById("c-service").value = "";
    document.getElementById("c-message").value = "";
  } catch(err) {
    toast(err.message, "error");
  } finally {
    btn.textContent = "Send Message";
    btn.disabled = false;
  }
}

window.pageRenderers = {
  home: renderHome,
  services: renderServices,
  artists: renderArtists,
  portal: renderPortal,
  admin: renderAdmin,
  login: renderLogin,
  contact: renderContact,
};
