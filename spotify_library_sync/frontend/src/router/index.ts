import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ArtistsView from '../views/ArtistsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/library_manager',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/library_manager/artists',
      name: 'artists',
      component: ArtistsView,
    },
    {
      path: '/library_manager/albums',
      name: 'albums',
      component: HomeView,
    },
    {
      path: '/library_manager/download_history',
      name: 'download_history',
      component: HomeView,
    },
    {
      path: '/library_manager/tracked_playlists',
      name: 'tracked_playlists',
      component: HomeView,
    },
    // Non routed pages
    {
      path: '/library_manager/artist',
      name: 'artist',
      component: HomeView,
    },
    {
      path: '/library_manager/song',
      name: 'song',
      component: HomeView,
    },
  ],
})

export default router
