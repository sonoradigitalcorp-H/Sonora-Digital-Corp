#!/bin/bash
# Web: Create landing page from template
set -e

CLIENT="${1:-}"
TEMPLATE="${2:-saas}"
if [ -z "$CLIENT" ]; then
  echo "Usage: $0 <client-name> [template]"
  echo "Templates: saas, ecommerce, agency, portfolio, app, coming-soon"
  exit 1
fi

LANDING_DIR="sonora-digital-corp/apps/frontends/landings/$CLIENT"
mkdir -p "$LANDING_DIR/src/{components,pages,styles,assets}"

echo "Creating $TEMPLATE landing page for: $CLIENT"

# Package.json
cat > "$LANDING_DIR/package.json" << EOF
{
  "name": "$CLIENT-landing",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "framer-motion": "^11"
  },
  "devDependencies": {
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "@vitejs/plugin-react": "^4",
    "vite": "^5",
    "typescript": "^5",
    "tailwindcss": "^3",
    "postcss": "^8",
    "autoprefixer": "^10"
  }
}
EOF

# Vite config
cat > "$LANDING_DIR/vite.config.ts" << EOF
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ plugins: [react()] })
EOF

# Tailwind config
cat > "$LANDING_DIR/tailwind.config.js" << EOF
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
EOF

# PostCSS config
cat > "$LANDING_DIR/postcss.config.js" << EOF
export default { plugins: { tailwindcss: {}, autoprefixer: {} } }
EOF

# Index.html
cat > "$LANDING_DIR/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>$CLIENT - Landing Page</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# Main entry
mkdir -p "$LANDING_DIR/src"
cat > "$LANDING_DIR/src/main.tsx" << EOF
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>
)
EOF

# CSS
cat > "$LANDING_DIR/src/index.css" << EOF
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# App component based on template
case $TEMPLATE in
  saas)
    cat > "$LANDING_DIR/src/App.tsx" << 'EOF'
import { motion } from 'framer-motion'

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900">
              Transform Your Business with <span className="text-blue-600">SaaS Solutions</span>
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-gray-600">
              Build scalable, modern applications that grow with your business.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <a href="#demo" className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                Start Free Trial
              </a>
              <a href="#features" className="bg-white text-blue-600 border-2 border-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition">
                View Features
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900">Everything You Need</h2>
          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: "Analytics", desc: "Real-time insights", icon: "📊" },
              { title: "Automation", desc: "Workflow automation", icon: "⚡" },
              { title: "Integrations", desc: "Connect your tools", icon: "🔗" },
            ].map((feature, i) => (
              <motion.div key={feature.title} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="p-6 bg-gray-50 rounded-xl">
                <span className="text-4xl">{feature.icon}</span>
                <h3 className="mt-4 text-xl font-semibold">{feature.title}</h3>
                <p className="mt-2 text-gray-600">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="demo" className="py-20 bg-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white">Ready to Get Started?</h2>
          <p className="mt-4 text-blue-100">Join thousands of companies already using our platform.</p>
          <a href="#" className="mt-8 inline-block bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition">
            Start Free Trial
          </a>
        </div>
      </section>
    </div>
  )
}
EOF
    ;;
  *)
    cat > "$LANDING_DIR/src/App.tsx" << EOF
import { motion } from 'framer-motion'

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900">
              Welcome to <span className="text-blue-600">$CLIENT</span>
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-gray-600">
              Your new landing page is ready to customize.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <a href="#" className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                Get Started
              </a>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
EOF
    ;;
esac

echo "Landing page created: $LANDING_DIR"
echo "Run: cd $LANDING_DIR && npm install && npm run dev"