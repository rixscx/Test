import { createRouter, createWebHistory } from 'vue-router';
// --- CORRECTED PATHS AND NAMES ---
import HomePage from './Views/HomeView.vue';
import AnalysisPage from './Views/AnalyzerView.vue';
import RecipesPage from './Views/RecipesView.vue';

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/analyzer', name: 'Analysis', component: AnalysisPage },
  { path: '/recipes', name: 'RecipeSearch', component: RecipesPage },
  { path: '/recipes/:food', name: 'Recipes', component: RecipesPage, props: true }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;