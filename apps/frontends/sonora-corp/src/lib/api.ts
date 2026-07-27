const API_BASE = "https://abe.sonoradigitalcorp.com/api";

async function fetchAPI(path: string) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getStats() {
  return fetchAPI("/stats");
}

export async function getServices() {
  return fetchAPI("/services");
}

export async function getHealth() {
  return fetchAPI("/health");
}
