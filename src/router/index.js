import { createRouter, createWebHistory } from 'vue-router'

import TripView from '@/views/TripView.vue'
import CarView from '@/views/CarView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/trip' },
    { path: '/trip', component: TripView },
    { path: '/car', component: CarView },
  ],
})

