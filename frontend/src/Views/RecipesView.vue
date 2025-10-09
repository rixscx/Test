<template>
  <div class="recipes-view" ref="canvasContainer">
    <div class="header-content">
        <h1 class="page-title">Eden Database</h1>
        <p class="page-subtitle">Querying culinary constructs from the network</p>
    </div>

    <div class="command-bar">
      <div class="search-bar">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="search-icon"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"></path></svg>
        <input type="text" v-model="searchQuery" placeholder="Initiate search query..." @keyup.enter="searchRecipes">
      </div>
      <div class="category-selector">
        <button
          v-for="category in categories"
          :key="category"
          @click="selectCategory(category)"
          :class="{ active: selectedCategory === category }"
        >
          {{ category }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="signal-loader">
        <div class="signal-bar"></div><div class="signal-bar"></div><div class="signal-bar"></div>
      </div>
      <p>Acquiring data stream...</p>
    </div>

    <div v-if="error" class="error-state">
      <p>Connection to culinary archive failed. Data stream unresponsive.</p>
    </div>

    <div v-if="!loading && !error" class="recipes-grid">
      <div v-for="(recipe, i) in recipes" :key="recipe.id" class="recipe-card" :style="{ '--delay': `${i * 75}ms` }">
        <div class="card-border-glow"></div>
        <div class="image-container">
          <div class="image-overlay"></div>
          <img :src="recipe.image" :alt="recipe.title" class="recipe-image">
        </div>
        <div class="recipe-content">
          <h3 class="recipe-title">{{ recipe.title }}</h3>
          <p class="recipe-description">{{ recipe.description }}</p>
          <button class="details-button">Analyze Construct</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';

const canvasContainer = ref(null);
let canvas, ctx, particles, animationFrameId;

// --- Perlin Noise Generator (for organic flow) ---
const Perlin = {
    rand_vect: function(){ let theta = Math.random() * 2 * Math.PI; return {x: Math.cos(theta), y: Math.sin(theta)}; },
    dot_prod_grid: function(x, y, vx, vy){ let g_vect; let d_vect = {x: x - vx, y: y - vy}; if (this.gradients[[vx,vy]]){ g_vect = this.gradients[[vx,vy]]; } else { g_vect = this.rand_vect(); this.gradients[[vx,vy]] = g_vect; } return d_vect.x * g_vect.x + d_vect.y * g_vect.y; },
    smootherstep: function(x){ return 6*x**5 - 15*x**4 + 10*x**3; },
    interp: function(x, a, b){ return a + this.smootherstep(x) * (b-a); },
    seed: function(){ this.gradients = {}; this.memory = {}; },
    get: function(x, y) { if (this.memory.hasOwnProperty([x,y])) return this.memory[[x,y]]; let xf = Math.floor(x); let yf = Math.floor(y); let tl = this.dot_prod_grid(x, y, xf,   yf); let tr = this.dot_prod_grid(x, y, xf+1, yf); let bl = this.dot_prod_grid(x, y, xf,   yf+1); let br = this.dot_prod_grid(x, y, xf+1, yf+1); let xt = this.interp(x-xf, tl, tr); let xb = this.interp(x-xf, bl, br); let v = this.interp(y-yf, xt, xb); this.memory[[x,y]] = v; return v; }
};
Perlin.seed();

// --- Particle Class ---
class Particle {
    constructor() {
        this.x = Math.random() * window.innerWidth;
        this.y = Math.random() * window.innerHeight;
        this.size = Math.random() * 1.5 + 0.5;
        this.speed = Math.random() * 0.5 + 0.2;
        this.angle = 0;
        this.alpha = 0;
    }

    update(noiseZ, mouse) {
        const noiseValue = Perlin.get(this.x * 0.001, this.y * 0.001 + noiseZ);
        this.angle = noiseValue * Math.PI * 2;
        
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;

        if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
        }

        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let distance = Math.sqrt(dx * dx + dy * dy);
        let maxDistance = mouse.radius;
        
        if (distance < maxDistance) {
            this.alpha = 1 - (distance / maxDistance);
            this.x += dx * 0.02 * this.alpha;
            this.y += dy * 0.02 * this.alpha;
        } else {
            this.alpha = 0;
        }
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${0.5 + this.alpha * 0.5})`;
        ctx.shadowColor = 'white';
        ctx.shadowBlur = 5 + this.alpha * 10;
        ctx.fill();
        ctx.shadowBlur = 0; // Reset shadow blur
    }
}

// --- Animation Setup ---
let noiseZ = 0;
function init(mouse) {
    particles = [];
    let numberOfParticles = (window.innerWidth * window.innerHeight) / 10000;
    for (let i = 0; i < numberOfParticles; i++) {
        particles.push(new Particle());
    }
}

function animate(mouse) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    noiseZ += 0.0005; // This makes the field evolve over time
    for (let i = 0; i < particles.length; i++) {
        particles[i].update(noiseZ, mouse);
        particles[i].draw();
    }
    animationFrameId = requestAnimationFrame(() => animate(mouse));
}


// --- Vue Lifecycle Hooks ---
onMounted(() => {
    canvas = document.createElement('canvas');
    canvas.id = 'stardust-canvas';
    canvasContainer.value.insertBefore(canvas, canvasContainer.value.firstChild);
    ctx = canvas.getContext('2d');

    const mouse = { x: undefined, y: undefined, radius: 150 };
    const handleMouseMove = (event) => { mouse.x = event.x; mouse.y = event.y; };
    window.addEventListener('mousemove', handleMouseMove);

    const handleResize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        init(mouse);
    };
    window.addEventListener('resize', handleResize);
    
    handleResize();
    animate(mouse);
    
    fetchRecipes('popular global dishes'); // Initial fetch
});

onBeforeUnmount(() => {
    cancelAnimationFrame(animationFrameId);
    window.removeEventListener('resize', () => {});
    window.removeEventListener('mousemove', () => {});
});


// --- Component Logic ---
const recipes = ref([]);
const loading = ref(true);
const error = ref(null);
const categories = ['Popular', 'Italian', 'Mexican', 'Indian', 'Japanese', 'Vegan'];
const selectedCategory = ref('Popular');
const searchQuery = ref('');

const fetchRecipes = async (query) => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/recipes/?category=${query}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    recipes.value = data;
  } catch (e) {
    error.value = e;
    console.error("Failed to fetch recipes:", e);
  } finally {
    loading.value = false;
  }
};

const selectCategory = (category) => {
  selectedCategory.value = category;
  searchQuery.value = '';
  let apiCategory = category.toLowerCase();
  if (apiCategory === 'popular') {
    apiCategory = 'popular global dishes';
  }
  fetchRecipes(apiCategory);
};

const searchRecipes = () => {
    if (!searchQuery.value.trim()) return;
    selectedCategory.value = '';
    fetchRecipes(searchQuery.value);
}

</script>

<style scoped>
/* Hide scrollbar for a cleaner look */
.recipes-view::-webkit-scrollbar { display: none; }
.recipes-view { -ms-overflow-style: none; scrollbar-width: none; }

.recipes-view {
  padding: 3rem 5rem;
  background-color: var(--bg-color);
  color: var(--primary-text);
  min-height: 100vh;
  font-family: 'Poppins', sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* Canvas for Stardust Field */
:deep(#stardust-canvas) {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

/* Header & Content is layered above the background */
.header-content, .command-bar, .recipes-grid, .loading-state, .error-state {
    position: relative;
    z-index: 1;
}

.page-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  letter-spacing: 1px;
}
.page-subtitle {
  text-align: center;
  font-size: 1.1rem;
  color: var(--secondary-text);
  margin-bottom: 4rem;
}

/* Command Bar */
.command-bar {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    padding: 1.5rem;
    margin: 0 auto 4rem auto;
    width: 80%;
    max-width: 1000px;
    background: rgba(13,13,13,0.7);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    backdrop-filter: blur(10px);
}

.search-bar {
    position: relative;
    width: 100%;
    max-width: 500px;
}
.search-icon {
    position: absolute; left: 1rem; top: 50%;
    transform: translateY(-50%);
    width: 20px; height: 20px;
    fill: var(--secondary-text);
    transition: fill 0.3s ease;
}
.search-bar input {
    width: 100%;
    padding: 0.8rem 1rem 0.8rem 3rem;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background-color: var(--surface-color);
    color: var(--primary-text);
    font-size: 1rem;
    transition: all 0.3s ease;
    outline: none;
}
.search-bar input:focus {
    border-color: var(--accent-glow);
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
}
.search-bar input:focus + .search-icon {
    fill: var(--primary-text);
}

/* Category Buttons */
.category-selector {
  display: flex; justify-content: center;
  gap: 0.75rem; flex-wrap: wrap;
}
.category-selector button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background-color: transparent;
  color: var(--secondary-text);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}
.category-selector button:hover {
  background-color: var(--border-color);
  color: var(--primary-text);
}
.category-selector button.active {
  background-color: var(--accent-glow);
  color: var(--bg-color);
  border-color: var(--accent-glow);
}

/* Loading and Error States */
.loading-state, .error-state {
  text-align: center; padding: 4rem; color: var(--secondary-text);
}
.signal-loader {
    display: flex; justify-content: center; align-items: center;
    height: 40px; gap: 8px; margin: 0 auto 1.5rem;
}
.signal-bar {
    width: 6px; height: 100%;
    background-color: var(--accent-glow);
    animation: signal 1.2s infinite ease-in-out;
}
.signal-bar:nth-child(2) { animation-delay: 0.2s; }
.signal-bar:nth-child(3) { animation-delay: 0.4s; }
@keyframes signal { 0%, 100% { transform: scaleY(0.2); } 50% { transform: scaleY(1); } }

/* Recipe Grid & Cards */
.recipes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 3rem;
}

.recipe-card {
  background-color: var(--surface-color);
  border-radius: 16px;
  overflow: hidden;
  display: flex; flex-direction: column;
  position: relative;
  border: 1px solid var(--border-color);
  animation: card-materialize 0.6s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
  transform: translateY(20px);
}
@keyframes card-materialize { to { opacity: 1; transform: translateY(0); } }

.card-border-glow {
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%;
    border-radius: 16px;
    box-shadow: 0 0 0px var(--accent-glow);
    pointer-events: none;
    transition: all 0.4s ease;
    opacity: 0;
}
.recipe-card:hover {
    transform: translateY(-5px);
}
.recipe-card:hover .card-border-glow {
    opacity: 1;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

.image-container {
  width: 100%; height: 220px;
  overflow: hidden;
  position: relative;
}
.image-overlay {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: 
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 20px 20px;
    opacity: 0;
    transition: opacity 0.4s ease;
}
.recipe-card:hover .image-overlay { opacity: 1; }

.recipe-image {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.recipe-card:hover .recipe-image { transform: scale(1.03); }

.recipe-content {
  padding: 1.5rem;
  display: flex; flex-direction: column;
  flex-grow: 1;
}
.recipe-title {
  margin: 0 0 0.75rem 0;
  font-size: 1.4rem;
  font-weight: 500;
  color: var(--primary-text);
}
.recipe-description {
  color: var(--secondary-text);
  font-size: 0.95rem;
  line-height: 1.6;
  flex-grow: 1;
}
.details-button {
  padding: 0.7rem 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: transparent;
  color: var(--secondary-text);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 0.9rem;
  align-self: flex-start;
  margin-top: 1.5rem;
}
.details-button:hover {
  background-color: var(--accent-glow);
  color: var(--bg-color);
  border-color: var(--accent-glow);
}
</style>