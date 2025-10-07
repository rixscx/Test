<template>
  <div id="app">
    <nav class="main-nav">
      <router-link to="/">Home</router-link>
      <router-link to="/analyzer">Analyzer</router-link>
      <router-link to="/recipes">Recipes</router-link>
    </nav>
    
    <main class="content-area">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style>
/* Global styles for a pure black theme */
:root {
  --bg-color: #000000;
  --surface-color: #121212;
  --primary-text: #ffffff;
  --secondary-text: #aaaaaa;
  --accent-color: #ffffff; /* Using white as the primary accent */
  --border-color: #222;
}

body {
  font-family: 'Poppins', sans-serif;
  background-color: var(--bg-color);
  color: var(--primary-text);
  margin: 0;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.main-nav {
  flex-shrink: 0; /* Prevents the nav from shrinking */
  display: flex;
  justify-content: center;
  padding: 1.5rem;
  background-color: var(--bg-color);
  border-bottom: 1px solid var(--border-color);
  position: relative; /* Establishes a stacking context */
  z-index: 100;       /* A high z-index to keep it on top of everything */
}

.main-nav a {
  color: var(--secondary-text);
  margin: 0 20px;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 500;
  transition: color 0.3s;
}

.main-nav a.router-link-exact-active,
.main-nav a:hover {
  color: var(--primary-text);
}

.content-area {
  flex-grow: 1; /* Makes the content area fill the remaining space */
  position: relative; /* Container for pages and their backgrounds */
  overflow-y: auto; /* Allows content to scroll if it's too long */
}

/* Page transition styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>