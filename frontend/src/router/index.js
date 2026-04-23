import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login',       name: 'Login',       component: () => import('@/views/LoginView.vue'),      meta: { public: true } },
  { path: '/',            name: 'Home',        component: () => import('@/views/HomeView.vue') },
  { path: '/history',     name: 'History',     component: () => import('@/views/HistoryView.vue') },
  { path: '/groups',      name: 'Groups',      component: () => import('@/views/GroupsView.vue') },
  { path: '/groups/:id',  name: 'GroupDetail', component: () => import('@/views/GroupDetailView.vue') },
  { path: '/reports',     name: 'Reports',     component: () => import('@/views/ReportsView.vue') },
  { path: '/profile',     name: 'Profile',     component: () => import('@/views/ProfileView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory('/app-mobile/'),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.user) await auth.init()
  if (!to.meta.public && auth.isGuest) return { name: 'Login' }
  if (to.name === 'Login' && !auth.isGuest) return { name: 'Home' }
})

export default router
