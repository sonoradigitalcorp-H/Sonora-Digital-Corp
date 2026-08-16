import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './views/HomeView.vue'
import Servicios from './views/ServiciosView.vue'
import Asistente from './views/AsistenteView.vue'
import Video from './views/VideoView.vue'
import Faq from './views/FaqView.vue'
import Contacto from './views/ContactoView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/servicios', name: 'servicios', component: Servicios },
    { path: '/asistente', name: 'asistente', component: Asistente },
    { path: '/video', name: 'video', component: Video },
    { path: '/faq', name: 'faq', component: Faq },
    { path: '/contacto', name: 'contacto', component: Contacto },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ],
  scrollBehavior() { return { top: 0 } }
})

export default router