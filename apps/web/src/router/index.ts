import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('@/views/LandingView.vue'),
      meta: { public: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/app',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/app/dashboard',
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/app/DashboardView.vue'),
        },
        {
          path: 'locations',
          name: 'locations',
          component: () => import('@/views/app/LocationsView.vue'),
        },
        {
          path: 'services',
          name: 'services',
          component: () => import('@/views/app/ServicesView.vue'),
        },
        {
          path: 'packages',
          name: 'packages',
          component: () => import('@/views/app/PackagesView.vue'),
        },
        {
          path: 'tickets',
          name: 'tickets',
          component: () => import('@/views/app/TicketsView.vue'),
        },
        {
          path: 'tickets/:id',
          name: 'ticket-detail',
          component: () => import('@/views/app/TicketDetailView.vue'),
        },
        {
          path: 'kanban',
          name: 'kanban',
          component: () => import('@/views/app/KanbanView.vue'),
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/app/SettingsView.vue'),
        },
      ],
    },
    {
      path: '/app/onboarding',
      name: 'onboarding',
      component: () => import('@/views/app/OnboardingView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/display',
      name: 'display',
      component: () => import('@/views/DisplayView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/t/:code',
      name: 'public-ticket',
      component: () => import('@/views/public/PublicTicketView.vue'),
      meta: { public: true },
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('@/views/legal/TermsView.vue'),
      meta: { public: true },
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('@/views/legal/PrivacyView.vue'),
      meta: { public: true },
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  // Skip all checks for public routes
  if (to.meta.public) {
    next()
    return
  }

  const authStore = useAuthStore()

  // Fetch user if authenticated but no user data
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }

  // Redirect to login if route requires auth and not authenticated
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Redirect to app if on guest route and authenticated
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router
