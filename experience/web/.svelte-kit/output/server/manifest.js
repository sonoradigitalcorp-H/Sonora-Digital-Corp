export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start.DVSlGlZ-.js",app:"_app/immutable/entry/app.nzxkcsmG.js",imports:["_app/immutable/entry/start.DVSlGlZ-.js","_app/immutable/chunks/9qqpwPIQ.js","_app/immutable/chunks/BKv9dmJM.js","_app/immutable/chunks/C4-aX6ab.js","_app/immutable/entry/app.nzxkcsmG.js","_app/immutable/chunks/BKv9dmJM.js","_app/immutable/chunks/BekaiDz9.js","_app/immutable/chunks/C5XPv7eZ.js","_app/immutable/chunks/C4-aX6ab.js","_app/immutable/chunks/C5P3QgPo.js","_app/immutable/chunks/D9pYLyBP.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
