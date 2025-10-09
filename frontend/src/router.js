import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './Views/HomeView.vue';
import AnalysisPage from './Views/AnalyzerView.vue';
import RecipesPage from './Views/RecipesView.vue';
import AboutPage from './Views/AboutView.vue'; // --- ADD THIS LINE ---

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/analyzer', name: 'Analysis', component: AnalysisPage },
  { path: '/recipes', name: 'RecipeSearch', component: RecipesPage },
  { path: '/about', name: 'About', component: AboutPage } // --- ADD THIS LINE ---
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;