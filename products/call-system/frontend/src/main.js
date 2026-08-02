import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import Landing from './pages/Landing.vue'
import Call from './pages/Call.vue'

const routes = [
  { path: '/', component: Landing },
  { path: '/call', component: Call },
]

const router = createRouter({ history: createWebHistory(), routes })
createApp(App).use(router).mount('#app')
