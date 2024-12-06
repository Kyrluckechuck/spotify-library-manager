<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import LibraryOverview from './components/LibraryOverview.vue'

</script>

<template>
  <header>
    <h2 class="importer_header">
      <img
        alt="Vue logo"
        class="logo"
        :src="'/static/library_manager/images/spotify_icon_128.png'"
        width="128"
        height="128"
      />
      <div class="title">Spotify AAC Downloader</div>
    </h2>

    <div class="wrapper">
      <LibraryOverview/>

      <nav>
        <RouterLink to="/library_manager">Home</RouterLink>
        <!-- <RouterLink to="/library_manager/about">About</RouterLink> -->
        <RouterLink to="/library_manager/artists">Artists</RouterLink>
        <RouterLink to="/library_manager/albums">Albums</RouterLink>
        <RouterLink to="/library_manager/download_history">Download History</RouterLink>
        <RouterLink to="/library_manager/tracked_playlists">Tracked Playlists</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
