<script setup>
import { ref, onMounted } from 'vue';
const props = defineProps({
  food: String
});

const recipes = ref([]);
const isLoading = ref(false);
const searchQuery = ref(props.food || ''); // Pre-fill search bar if coming from analyzer
const searchedTerm = ref(props.food || '');
const errorMessage = ref('');

async function fetchRecipes(ingredient) {
  if (!ingredient) {
    recipes.value = [];
    return;
  }
  isLoading.value = true;
  recipes.value = []; // Clear previous results
  errorMessage.value = '';
  searchedTerm.value = ingredient;
  
  await new Promise(res => setTimeout(res, 1000)); // Simulate load time for effect
  try {
    const response = await fetch(`https://www.themealdb.com/api/json/v1/1/filter.php?i=${ingredient}`);
    const data = await response.json();
    if (data.meals) {
      recipes.value = data.meals;
    } else {
      errorMessage.value = `No recipes found for "${ingredient}".`;
    }
  } catch (e) {
    errorMessage.value = "Failed to connect to the recipe database.";
  }
  finally {
    isLoading.value = false;
  }
}

function handleSearch() {
  fetchRecipes(searchQuery.value);
}

// If a food was passed from the analyzer, fetch its recipes when the page loads
onMounted(() => {
  if (props.food) {
    fetchRecipes(props.food);
  } else {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="page-wrapper">
    <div class="animated-gradient-bg"></div>
    <div class="content-overlay">
      <h1 class="page-title">Recipe Finder</h1>
      
      <form @submit.prevent="handleSearch" class="search-form">
        <input type="text" v-model="searchQuery" placeholder="Search for an ingredient (e.g., Chicken)" />
        <button type="submit">Search</button>
      </form>

      <div v-if="isLoading" class="recipe-grid">
        <div v-for="n in 8" :key="n" class="skeleton-card"></div>
      </div>
      <div v-else-if="recipes.length > 0" class="results-container">
        <h2>Showing results for: <span class="highlight">{{ searchedTerm }}</span></h2>
        <div class="recipe-grid">
          <div v-for="(recipe, index) in recipes" :key="recipe.idMeal" 
               class="recipe-card" 
               :style="{ '--delay': `${index * 100}ms` }">
            <img :src="recipe.strMealThumb" :alt="recipe.strMeal" />
            <div class="card-overlay">
              <h3>{{ recipe.strMeal }}</h3>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="welcome-message">
        <p v-if="errorMessage">{{ errorMessage }}</p>
        <p v-else-if="searchedTerm && !isLoading">No recipes found for "{{ searchedTerm }}".</p>
        <p v-else>Search for an ingredient to discover new recipes.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  position: relative;
  min-height: calc(100vh - 85px); /* Full height minus nav bar */
  overflow: hidden;
}
.animated-gradient-bg {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(-45deg, #000000, #0a0a1a, #000000, #1a0a0a);
  background-size: 400% 400%;
  animation: gradientBG 20s ease infinite;
  z-index: 0;
}
@keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

.content-overlay { position: relative; z-index: 1; max-width: 1200px; margin: 0 auto; padding: 2rem; }
.page-title { text-align: center; }

.search-form { display: flex; max-width: 600px; margin: 2rem auto 3rem; }
.search-form input {
  flex-grow: 1;
  padding: 1rem;
  border: 1px solid var(--border-color);
  background-color: var(--surface-color);
  color: var(--primary-text);
  border-radius: 8px 0 0 8px;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}
.search-form input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}
.search-form button { border-radius: 0 8px 8px 0; }

.results-container h2 { text-align: center; margin-bottom: 2rem; font-weight: 400; }
.highlight { text-transform: capitalize; color: #fff; font-weight: 700; }
.recipe-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }
.recipe-card {
  position: relative; border-radius: 12px; overflow: hidden;
  cursor: pointer; height: 250px; border: 1px solid var(--border-color);
  opacity: 0; transform: translateY(20px);
  animation: cardFadeIn 0.5s ease forwards; animation-delay: var(--delay);
}
@keyframes cardFadeIn { to { opacity: 1; transform: translateY(0); } }
.recipe-card:hover img { transform: scale(1.1); }
.recipe-card img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; }
.card-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); padding: 2rem 1rem 1rem; }
.recipe-card h3 { margin: 0; font-size: 1.2rem; color: #fff; }
.skeleton-card { background-color: var(--surface-color); border-radius: 12px; height: 250px; border: 1px solid var(--border-color); animation: pulse 1.5s infinite ease-in-out; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.welcome-message { text-align: center; margin-top: 3rem; font-size: 1.2rem; color: var(--secondary-text); }
</style>