

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/fallbacks/layout.svelte.js')).default;
export const imports = ["_app/immutable/nodes/0.BWjSoqUW.js","_app/immutable/chunks/C5XPv7eZ.js","_app/immutable/chunks/BKv9dmJM.js","_app/immutable/chunks/D9pYLyBP.js"];
export const stylesheets = [];
export const fonts = [];
