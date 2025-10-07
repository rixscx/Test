<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import FOG from 'vanta/dist/vanta.fog.min';
import * as THREE from 'three';

// --- Vanta.js Background Setup ---
const vantaContainer = ref(null);
let vantaEffect = null;
onMounted(() => {
  vantaEffect = FOG({
    el: vantaContainer.value, THREE: THREE,
    mouseControls: true, touchControls: true, gyroControls: false,
    minHeight: 200.00, minWidth: 200.00,
    highlightColor: 0x525252,
    midtoneColor: 0x313131,
    lowlightColor: 0x0,
    baseColor: 0x0,
    blurFactor: 0.90,
    speed: 1.50,
    zoom: 0.4
  });
});
onBeforeUnmount(() => { if (vantaEffect) vantaEffect.destroy(); });


// --- Component Logic (Restored from your reference code) ---
const router = useRouter();
const selectedFile = ref(null);
const imagePreviewUrl = ref('');
const analysisResult = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');
const isDragOver = ref(false);

async function analyzeImage() {
  if (!selectedFile.value) {
    errorMessage.value = 'Please select an image first.';
    return;
  }
  isLoading.value = true;
  errorMessage.value = '';
  analysisResult.value = null;

  // This is a mock response. Replace with your actual fetch() call.
  await new Promise(res => setTimeout(res, 2500));
  analysisResult.value = {
    Total_profile: "{'calories': 530, 'proteins': 45, 'fats': 35, 'carbs': 8}",
    Ingredient_breakdown: "[{'ingredient': {'name': 'Grilled Chicken'}, 'nutrients': {'calories': 350}, 'cost': 150}, {'ingredient': {'name': 'Leafy Greens'}, 'nutrients': {'calories': 180}, 'cost': 60}]",
    Metadata: "{'detected_items': ['chicken', 'salad'], 'dish_name': 'Grilled Chicken Salad', 'disclaimer': 'Estimates only.', 'sources': ['USDA API']}"
  };
  isLoading.value = false;
}

function findRecipes() {
  const dishName = formattedResult.value?.metadata?.dish_name;
  if (dishName) router.push({ name: 'Recipes', params: { food: dishName } });
}

function parseApiString(str) {
  if (!str) return null;
  if (typeof str === 'object') return str;
  if (typeof str === 'string') {
    try { return JSON.parse(str.replace(/'/g, '"')); } 
    catch (e) { console.warn('Failed to parse API string:', str); return null; }
  }
  return null;
}

const formattedResult = computed(() => {
  if (!analysisResult.value) return null;
  return {
    total_profile: parseApiString(analysisResult.value.Total_profile) || {},
    ingredient_breakdown: parseApiString(analysisResult.value.Ingredient_breakdown) || [],
    metadata: parseApiString(analysisResult.value.Metadata) || {}
  };
});

function setFile(file) {
  if (file && file.type.startsWith('image/')) {
    if (imagePreviewUrl.value) URL.revokeObjectURL(imagePreviewUrl.value);
    selectedFile.value = file;
    errorMessage.value = '';
    imagePreviewUrl.value = URL.createObjectURL(file);
  }
}
function handleFileChange(event) { if (event.target.files.length > 0) setFile(event.target.files[0]); }
function handleDrop(event) {
  event.preventDefault();
  isDragOver.value = false;
  if (event.dataTransfer.files.length > 0) setFile(event.dataTransfer.files[0]);
}
</script>

<template>
  <div class="page-wrapper" ref="vantaContainer">
    <div class="content-overlay">
      <h1 class="page-title">Nutrient Analyzer</h1>
      <p class="page-subtitle">A modern tool for culinary insights.</p>
      
      <div class="analyzer-core">
        <div 
          class="drop-zone"
          :class="{ 'drag-over': isDragOver }"
          @dragover.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @drop="handleDrop"
          @click="$refs.fileInput.click()"
        >
          <img v-if="imagePreviewUrl" :src="imagePreviewUrl" class="image-preview" alt="Selected food"/>
          <div v-else class="placeholder-text">
            <span>+</span>
            <p>Place Food Image Here</p>
          </div>
          <input ref="fileInput" type="file" @change="handleFileChange" accept="image/*" class="file-input"/>
        </div>

        <button @click="analyzeImage" :disabled="isLoading || !selectedFile">
          <div v-if="isLoading" class="spinner"></div>
          <span>{{ isLoading ? 'Analyzing...' : 'Analyze' }}</span>
        </button>
      </div>
      
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <div v-if="formattedResult" class="result-container">
        <div class="result-card" :style="{'--delay': '100ms'}">
          <h2>Dish Name</h2>
          <div class="meta-item"><span class="tag">{{ formattedResult.metadata.dish_name }}</span></div>
        </div>
        <div class="result-card" :style="{'--delay': '200ms'}">
          <h2>Total Profile</h2>
          <div class="profile-grid">
              <div class="stat-item">
                <span class="stat-value">{{ formattedResult.total_profile.calories?.toFixed(0) || 'N/A' }}</span>
                <span class="stat-label">Calories</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ formattedResult.total_profile.proteins?.toFixed(1) || 'N/A' }}g</span>
                <span class="stat-label">Protein</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ formattedResult.total_profile.fats?.toFixed(1) || 'N/A' }}g</span>
                <span class="stat-label">Fats</span>
              </div>
               <div class="stat-item">
                <span class="stat-value">{{ formattedResult.total_profile.carbs?.toFixed(1) || 'N/A' }}g</span>
                <span class="stat-label">Carbs</span>
              </div>
            </div>
        </div>
        <div class="result-card" :style="{'--delay': '300ms'}">
            <h2>Ingredient Breakdown</h2>
             <table class="ingredients-table">
               <thead><tr><th>Ingredient</th><th>Calories</th><th>Cost (est.)</th></tr></thead>
               <tbody>
                 <tr v-for="(item, index) in formattedResult.ingredient_breakdown" :key="index">
                   <td>{{ item?.ingredient?.name || 'Unknown' }}</td>
                   <td>{{ item?.nutrients?.calories ? Number(item.nutrients.calories).toFixed(1) : 'N/A' }}</td>
                   <td>{{ item?.cost !== undefined && item?.cost !== null ? '₹' + Number(item.cost).toFixed(2) : 'N/A' }}</td>
                 </tr>
               </tbody>
             </table>
        </div>
         <div class="result-card" :style="{'--delay': '400ms'}">
            <h2>Metadata</h2>
            <div class="meta-item">
              <strong>Detected Items:</strong>
              <div class="tags-container">
                <span v-for="item in (formattedResult.metadata.detected_items || [])" :key="item" class="tag">{{ item }}</span>
              </div>
            </div>
        </div>
        <div class="result-card" :style="{'--delay': '500ms'}">
          <button @click="findRecipes" class="recipe-button">Find Recipes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  width: 100%;
  min-height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}
.content-overlay {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
  position: relative;
  z-index: 2;
}
.page-title {
  font-size: 2.5rem;
  letter-spacing: 1px;
  font-weight: 300;
}
.page-subtitle {
  color: var(--secondary-text);
  margin-top: -1.5rem;
  margin-bottom: 2rem;
}

/* --- FIX START HERE --- */
.analyzer-core {
  /* This container now has a max-width to match the drop-zone */
  max-width: 450px;
  margin-left: auto;
  margin-right: auto;
  
  background: rgba(18, 18, 18, 0.6);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
}

.drop-zone {
  /* Proportions are now a taller, less wide rectangle */
  max-width: 450px; /* This is now redundant as parent controls width */
  height: 350px;
  width: 100%;
  
  /* Added padding to create space around the image */
  padding: 1rem;
  box-sizing: border-box;

  border: 2px dashed var(--border-color);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  cursor: pointer; transition: all 0.3s ease;
  margin-bottom: 2rem;
}
/* --- FIX END HERE --- */

.drop-zone:hover, .drop-zone.drag-over {
  border-color: var(--accent-color);
  background-color: rgba(255, 255, 255, 0.05);
}
.image-preview {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
}
.placeholder-text span {
  font-size: 3rem;
  font-weight: 200;
  color: var(--secondary-text);
}
.file-input {
  display: none;
}
button {
  width: 100%;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  color: var(--primary-text);
  background-color: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
button:hover:not(:disabled) {
  background-color: var(--primary-text);
  color: var(--bg-color);
}
button:disabled {
  border-color: var(--border-color);
  color: var(--secondary-text);
  cursor: not-allowed;
}
.spinner {
  border: 3px solid rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  border-top-color: #000;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}
button:hover .spinner {
  border-top-color: #fff;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.result-container {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.result-card {
  background: rgba(18, 18, 18, 0.7);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  text-align: left;
  opacity: 0;
  transform: translateY(20px);
  animation: cardFadeIn 0.5s ease forwards;
  animation-delay: var(--delay);
}
@keyframes cardFadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.result-card h2 {
  margin-top: 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}
.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
  text-align: center;
}
.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
}
.stat-label {
  font-size: 0.8rem;
  color: var(--secondary-text);
}
.tag {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 5px 12px;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.ingredients-table {
  width: 100%;
  border-collapse: collapse;
}
.ingredients-table th,
.ingredients-table td {
  padding: 10px;
  border-bottom: 1px solid var(--border-color);
}
.meta-item {
  margin-bottom: 1rem;
}
.meta-item strong {
  display: block;
  margin-bottom: 0.5rem;
}
</style>