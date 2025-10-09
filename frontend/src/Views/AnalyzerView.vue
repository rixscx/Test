<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';

// --- BACKGROUND ANIMATION SCRIPT ---
const canvasContainer = ref(null);
let canvas, ctx, particles, animationFrameId;

const Perlin = {
    rand_vect: function(){ let theta = Math.random() * 2 * Math.PI; return {x: Math.cos(theta), y: Math.sin(theta)}; },
    dot_prod_grid: function(x, y, vx, vy){ let g_vect; let d_vect = {x: x - vx, y: y - vy}; if (this.gradients[[vx,vy]]){ g_vect = this.gradients[[vx,vy]]; } else { g_vect = this.rand_vect(); this.gradients[[vx,vy]] = g_vect; } return d_vect.x * g_vect.x + d_vect.y * g_vect.y; },
    smootherstep: function(x){ return 6*x**5 - 15*x**4 + 10*x**3; },
    interp: function(x, a, b){ return a + this.smootherstep(x) * (b-a); },
    seed: function(){ this.gradients = {}; this.memory = {}; },
    get: function(x, y) { if (this.memory.hasOwnProperty([x,y])) return this.memory[[x,y]]; let xf = Math.floor(x); let yf = Math.floor(y); let tl = this.dot_prod_grid(x, y, xf,   yf); let tr = this.dot_prod_grid(x, y, xf+1, yf); let bl = this.dot_prod_grid(x, y, xf,   yf+1); let br = this.dot_prod_grid(x, y, xf+1, yf+1); let xt = this.interp(x-xf, tl, tr); let xb = this.interp(x-xf, bl, br); let v = this.interp(y-yf, xt, xb); this.memory[[x,y]] = v; return v; }
};
Perlin.seed();

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
        ctx.shadowBlur = 0;
    }
}

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
    noiseZ += 0.0005;
    for (let i = 0; i < particles.length; i++) {
        particles[i].update(noiseZ, mouse);
        particles[i].draw();
    }
    animationFrameId = requestAnimationFrame(() => animate(mouse));
}
// --- END BACKGROUND ANIMATION SCRIPT ---


onMounted(() => {
  // --- Initialize Background Animation ---
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
});

onBeforeUnmount(() => {
    // --- Cleanup Background Animation ---
    cancelAnimationFrame(animationFrameId);
    window.removeEventListener('resize', () => {});
    window.removeEventListener('mousemove', () => {});
});

const router = useRouter();
const selectedFile = ref(null);
const imagePreviewUrl = ref('');
const analysisResult = ref(null);
const isLoading = ref(false);
const errorMessage = ref('');
const isDragOver = ref(false);

async function analyzeImage() {
  if (!selectedFile.value) return;
  isLoading.value = true;
  errorMessage.value = '';
  analysisResult.value = null;
  const formData = new FormData();
  formData.append('image', selectedFile.value);
  try {
    const response = await fetch('http://127.0.0.1:8000/api/analyze/', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed');
    analysisResult.value = data.analysis;
  } catch (error) {
    errorMessage.value = `Analysis failed. Check if the backend is running. Details: ${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

function findRecipes() {
  const dishName = analysisResult.value?.metadata?.dish_name;
  if (dishName) router.push({ name: 'Recipes', params: { food: dishName } });
}

function saveAnalysis() {
  if (!analysisResult.value) return;
  const dishName = analysisResult.value?.metadata?.dish_name.replace(/\s+/g, '_') || 'analysis';
  const filename = `${dishName}_analysis.json`;
  const dataStr = JSON.stringify(analysisResult.value, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function setFile(file) {
  if (file && file.type.startsWith('image/')) {
    if (imagePreviewUrl.value) URL.revokeObjectURL(imagePreviewUrl.value);
    selectedFile.value = file;
    imagePreviewUrl.value = URL.createObjectURL(file);
  }
}

function clearImage() {
  if (imagePreviewUrl.value) URL.revokeObjectURL(imagePreviewUrl.value);
  selectedFile.value = null;
  imagePreviewUrl.value = '';
}

function handleFileChange(event) {
  if (event.target.files.length > 0) setFile(event.target.files[0]);
}

function handleDrop(event) {
  event.preventDefault();
  isDragOver.value = false;
  if (event.dataTransfer.files.length > 0) setFile(event.dataTransfer.files[0]);
}
</script>

<template>
  <div class="page-wrapper" ref="canvasContainer">
    <div class="content-overlay">
      <div class="header">
        <h1 class="page-title" data-text="Eden">Eden</h1>
        <p class="page-subtitle">A modern tool for culinary insights.</p>
      </div>

      <div class="analyzer-layout">
        <div class="analyzer-core">
          <div
            class="drop-zone"
            :class="{ 'drag-over': isDragOver, 'has-image': imagePreviewUrl }"
            @dragover.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @drop="handleDrop"
            @click="!imagePreviewUrl ? $refs.fileInput.click() : null"
          >
            <div v-if="imagePreviewUrl" class="image-preview-container">
              <img :src="imagePreviewUrl" class="image-preview" alt="Selected food" />
              <button @click.stop="clearImage" class="clear-btn">×</button>
            </div>
            <div v-else class="placeholder-text">
              <svg class="placeholder-icon" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15v-4H7v-2h4V7h2v4h4v2h-4v4h-2z" />
              </svg>
              <p>Place Food Image Here</p>
            </div>
            <input ref="fileInput" type="file" @change="handleFileChange" accept="image/*" class="file-input" />
          </div>

          <button @click="analyzeImage" :disabled="isLoading || !selectedFile" class="analyze-button">
            <span class="button-text">{{ isLoading ? 'Analyzing...' : 'Analyze' }}</span>
            <div v-if="isLoading" class="spinner"></div>
            <div v-if="isLoading" class="typing-node">
              <div class="particle"></div>
              <div class="particle"></div>
              <div class="particle"></div>
            </div>
          </button>
        </div>

        <div class="right-panel">
          <transition name="error-fade">
            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
          </transition>

          <transition name="results-slide-fade" mode="out-in">
            <div v-if="analysisResult" class="result-container">
              <div class="result-card" :style="{'--delay': '100ms'}">
                <h2>Dish Name</h2>
                <div class="meta-item">
                  <span class="tag">{{ analysisResult.metadata.dish_name }}</span>
                </div>
              </div>
              <div class="result-card" :style="{'--delay': '200ms'}">
                <h2>Total Profile</h2>
                <div class="profile-grid">
                  <div class="stat-item">
                    <span class="stat-value">{{ analysisResult.Total_profile.calories?.toFixed(0) || 'N/A' }}</span>
                    <span class="stat-label">Calories</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ analysisResult.Total_profile.proteins?.toFixed(1) || 'N/A' }}g</span>
                    <span class="stat-label">Protein</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ analysisResult.Total_profile.fats?.toFixed(1) || 'N/A' }}g</span>
                    <span class="stat-label">Fats</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">{{ analysisResult.Total_profile.carbs?.toFixed(1) || 'N/A' }}g</span>
                    <span class="stat-label">Carbs</span>
                  </div>
                </div>
              </div>
              <div class="result-card" :style="{'--delay': '300ms'}">
                <h2>Ingredient Breakdown</h2>
                <table class="ingredients-table">
                  <thead>
                    <tr>
                      <th>Ingredient</th>
                      <th>Calories</th>
                      <th>Cost (est.)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in analysisResult.Ingredient_breakdown" :key="index">
                      <td>{{ item?.ingredient?.name || 'Unknown' }}</td>
                      <td>{{ item?.nutrients?.calories ? Number(item.nutrients.calories).toFixed(1) : 'N/A' }}</td>
                      <td>{{ item?.cost !== undefined && item?.cost !== null ? '₹' + Number(item.cost).toFixed(2) : 'N/A' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="action-buttons-container" :style="{'--delay': '400ms'}">
                <button @click="findRecipes" class="action-button">
                  <span>Find Recipes</span>
                </button>
                <button @click="saveAnalysis" class="action-button">
                  <span>Save Analysis</span>
                </button>
              </div>
            </div>
            <div v-else-if="!errorMessage" class="result-placeholder">
              <svg class="placeholder-icon-large" viewBox="0 0 24 24">
                <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12H17A5,5 0 0,0 12,7V4Z" />
              </svg>
              <p>Awaiting analysis...</p>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- UNCHANGED STYLES --- */
:root {
  --primary-text: #e5e5e5;
  --secondary-text: #888888;
  --border-color: #2a2a2a;
  --bg-color: #000000;
  --surface-color: #0d0d0d;
  --accent-glow: #ffffff;
}
.page-wrapper {
  width: 100%;
  height: 100vh;
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: var(--bg-color); /* Ensure background is black */
}
.content-overlay {
  width: 95%;
  max-width: 1400px;
  height: 90vh;
  margin: 0 auto;
  text-align: center;
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
}
.header {
  flex-shrink: 0;
  margin-bottom: 1.5rem;
  animation: fadeInUp 1.2s cubic-bezier(0.25, 1, 0.5, 1);
}
.analyzer-layout {
  flex-grow: 1;
  display: flex;
  gap: 2rem;
  height: 100%;
  min-height: 0;
}
.right-panel {
  flex: 1.2;
  display: flex;
  flex-direction: column;
}
.page-subtitle { 
  color: var(--secondary-text); 
  margin-top: 0.2rem;
  font-size: 1.1rem;
  letter-spacing: 0.5px;
  opacity: 0.8;
  animation: fadeIn 2s ease-in;
}
.analyzer-core {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(18, 18, 18, 0.4);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
  transition: all 0.5s ease;
}
.drop-zone {
  flex-grow: 1;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  margin-bottom: 2rem;
  background: rgba(0,0,0,0.2);
  background: linear-gradient(var(--bg-color), var(--bg-color)) padding-box,
              linear-gradient(90deg, transparent, var(--accent-glow), transparent) border-box;
  border: 2px solid transparent;
  animation: glowLine 3s ease-in-out infinite;
}
.drop-zone.has-image { border-style: solid; cursor: default; }
.drop-zone.drag-over {
  background-color: rgba(0,0,0,0.3);
  border-color: var(--secondary-text);
}
.drop-zone:hover:not(.has-image) {
  background-color: rgba(0,0,0,0.3);
  border-color: var(--secondary-text);
}
.image-preview-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-preview { 
  max-width: 100%; 
  max-height: 100%; 
  object-fit: contain; 
  border-radius: 10px; 
}
.clear-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0,0,0,0.7);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  color: var(--primary-text);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 3;
}
.clear-btn:hover {
  background: var(--primary-text);
  color: var(--bg-color);
  transform: scale(1.1);
}
.placeholder-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--secondary-text);
  transition: color 0.4s ease;
  position: relative;
  z-index: 2;
}
.drop-zone:hover .placeholder-text { color: var(--primary-text); }
.placeholder-icon {
  width: 48px;
  height: 48px;
  fill: currentColor;
  margin-bottom: 1rem;
  transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}
.drop-zone:hover .placeholder-icon { transform: scale(1.1); }
.file-input { display: none; }
.analyze-button, .action-button {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: transparent;
  color: var(--primary-text);
}
.analyze-button {
  width: 100%;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.analyze-button .button-text { z-index: 2; position: relative; }
.action-button {
  flex-grow: 1;
  padding: 0.8rem 1rem;
  font-size: 1rem;
  color: var(--secondary-text);
}
.action-button span, .analyze-button .button-text {
    z-index: 2;
    position: relative;
    transition: color 0.4s ease;
}
.analyze-button::before, .action-button::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: var(--primary-text);
    transform: translateX(-101%);
    transition: transform 0.4s cubic-bezier(0.7, 0, 0.2, 1);
    z-index: 1;
}
.analyze-button:hover::before, .action-button:hover::before {
    transform: translateX(0);
}
.analyze-button:hover .button-text, .action-button:hover span {
    color: var(--bg-color);
}
.analyze-button:disabled {
  color: var(--secondary-text);
  cursor: not-allowed;
  background-color: rgba(0,0,0,0.2);
}
.analyze-button:disabled:hover::before { transform: translateX(-101%); }
.analyze-button:disabled:hover .button-text { color: var(--secondary-text); }
.typing-node {
  border: 1px dashed var(--border-color);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  height: 20px;
  margin-left: 10px;
}
.particle {
  width: 4px;
  height: 4px;
  background: var(--accent-glow);
  border-radius: 50%;
  animation: particle-flow 1.2s infinite ease-in-out;
}
.particle:nth-child(2) { animation-delay: 0.2s; }
.particle:nth-child(3) { animation-delay: 0.4s; }
@keyframes particle-flow { 0%, 100% { transform: scale(0.5); opacity: 0.5; } 50% { transform: scale(1); opacity: 1; } }
.result-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
  padding-right: 1rem;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.result-container::-webkit-scrollbar {
    display: none;
}
.result-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--secondary-text);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  background: rgba(18, 18, 18, 0.4);
}
.placeholder-icon-large {
    width: 64px;
    height: 64px;
    fill: var(--secondary-text);
    opacity: 0.5;
    margin-bottom: 1rem;
    animation: pulse-rotate 4s infinite ease-in-out;
}
@keyframes pulse-rotate {
    0% { transform: scale(0.9) rotate(0deg); opacity: 0.4; }
    50% { transform: scale(1.1) rotate(180deg); opacity: 0.8; }
    100% { transform: scale(0.9) rotate(360deg); opacity: 0.4; }
}
.result-card {
  background: rgba(18, 18, 18, 0.6);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  text-align: left;
  opacity: 0;
  transform: translateY(20px);
  animation: cardFadeIn 0.6s cubic-bezier(0.23, 1, 0.32, 1) forwards;
  animation-delay: var(--delay);
  transition: border-color 0.3s ease;
  position: relative;
}
.result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-glow), transparent);
  animation: glowLine 3s ease-in-out infinite;
}
.result-card:hover {
    border-color: var(--secondary-text);
}
.result-card h2 { 
    margin-top: 0; 
    margin-bottom: 1rem;
    padding-bottom: 0.5rem; 
    font-weight: 400; 
    color: var(--primary-text);
    position: relative;
    display: inline-block;
}
.result-card h2::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0;
    width: 0%;
    height: 1px;
    background: var(--primary-text);
    transition: width 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}
.result-card:hover h2::after {
    width: 100%;
}
.profile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 1rem; text-align: center; }
.stat-value { font-size: 1.8rem; font-weight: 500; color: var(--primary-text); }
.stat-label { font-size: 0.8rem; color: var(--secondary-text); text-transform: uppercase; letter-spacing: 0.5px; }
.tag { 
    background-color: rgba(255, 255, 255, 0.05); 
    color: var(--primary-text); 
    padding: 5px 12px; 
    border-radius: 20px; 
    border: 1px solid var(--border-color); 
    display: inline-block;
    transition: all 0.3s ease;
}
.tag:hover {
    transform: translateY(-2px);
    border-color: var(--primary-text);
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}
.ingredients-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.ingredients-table th, .ingredients-table td { padding: 12px; border-bottom: 1px solid var(--border-color); transition: all 0.3s ease; }
.ingredients-table th { 
    font-weight: 500; 
    color: var(--secondary-text); 
    text-transform: uppercase;
}
.ingredients-table tbody tr { position: relative; }
.ingredients-table tbody tr::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: var(--primary-text);
    transform: scaleY(0);
    transform-origin: center;
    transition: transform 0.3s ease;
}
.ingredients-table tbody tr:hover::before {
    transform: scaleY(1);
}
.ingredients-table tbody tr:hover td { 
    background-color: rgba(255,255,255,0.03); 
    transform: translateX(4px);
}
.meta-item { margin-bottom: 1rem; }
.action-buttons-container {
  display: flex;
  gap: 1rem;
  opacity: 0;
  transform: translateY(20px);
  animation: cardFadeIn 0.5s ease forwards;
  animation-delay: var(--delay);
}
.action-button:hover {
    border-color: var(--border-color);
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}
.spinner {
  border: 3px solid rgba(255,255,255,0.2);
  border-radius: 50%;
  border-top-color: var(--primary-text);
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
  margin-left: 10px;
}
.analyze-button:hover .spinner { border-top-color: var(--bg-color); }
@keyframes spin { to { transform: rotate(360deg); } }
.error-message {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ff8a80;
  border: 1px solid #ff8a80;
  border-radius: 16px;
  background: rgba(255, 138, 128, 0.1);
  padding: 2rem;
}
.error-fade-enter-active, .error-fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.error-fade-enter-from, .error-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
.results-slide-fade-enter-active, .results-slide-fade-leave-active {
  transition: opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1), transform 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}
.results-slide-fade-enter-from { opacity: 0; transform: translateY(30px); }
.results-slide-fade-leave-to { opacity: 0; transform: translateY(-30px); }
@keyframes glowLine {
  0%, 100% { opacity: 0.5; box-shadow: 0 0 5px #666; }
  50% { opacity: 1; box-shadow: 0 0 20px #aaa; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@media (max-width: 900px) {
  .analyzer-layout { flex-direction: column; }
  .result-container { padding-right: 0.5rem; }
}
:global(::-webkit-scrollbar) { display: none; }
:global(html), :global(body) {
  scrollbar-width: none;
  -ms-overflow-style: none;
  overflow: hidden;
}

/* --- NEW STYLES & OVERRIDES --- */

/* Canvas for Stardust Field */
:deep(#stardust-canvas) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* Positioned behind .content-overlay */
}

/* Page wrapper adjustments */
.page-wrapper {
  z-index: 1;
}

/* NEW EDEN HEADING STYLE */
.page-title {
  font-size: 3.5rem; 
  font-weight: 500; 
  letter-spacing: 2px;
  color: var(--primary-text);
  text-shadow: none;
  background: none;
  -webkit-background-clip: unset;
  background-clip: unset;
  animation: none;
  position: relative;
  display: inline-block;
  cursor: default; /* Make it feel static until hovered */
  padding: 0 10px;
}

/* REMOVE old shimmer/glow effects */
.page-title::after {
  display: none;
}

/* ADD Data-corruption effect */
.page-title::before, .page-title::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 10px;
  width: 100%;
  height: 100%;
  background: var(--bg-color);
  overflow: hidden;
  color: var(--primary-text);
  clip: rect(0, 0, 0, 0);
}

.page-title::before {
  left: 8px;
  text-shadow: -2px 0 white;
  animation: glitch-anim-1 2s infinite linear alternate-reverse;
}

.page-title::after {
  left: -8px;
  text-shadow: -2px 0 white, 2px 2px white;
  animation: glitch-anim-2 3s infinite linear alternate-reverse;
}

@keyframes glitch-anim-1 {
  0% { clip: rect(42px, 9999px, 44px, 0); }
  5% { clip: rect(17px, 9999px, 96px, 0); }
  10% { clip: rect(40px, 9999px, 66px, 0); }
  15% { clip: rect(87px, 9999px, 82px, 0); }
  20% { clip: rect(12px, 9999px, 74px, 0); }
  25% { clip: rect(54px, 9999px, 57px, 0); }
  30% { clip: rect(42px, 9999px, 95px, 0); }
  35% { clip: rect(62px, 9999px, 73px, 0); }
  40% { clip: rect(31px, 9999px, 94px, 0); }
  45% { clip: rect(85px, 9999px, 49px, 0); }
  50% { clip: rect(47px, 9999px, 82px, 0); }
  55% { clip: rect(67px, 9999px, 75px, 0); }
  60% { clip: rect(82px, 9999px, 60px, 0); }
  65% { clip: rect(41px, 9999px, 70px, 0); }
  70% { clip: rect(88px, 9999px, 83px, 0); }
  75% { clip: rect(43px, 9999px, 63px, 0); }
  80% { clip: rect(25px, 9999px, 75px, 0); }
  85% { clip: rect(53px, 9999px, 50px, 0); }
  90% { clip: rect(10px, 9999px, 93px, 0); }
  95% { clip: rect(69px, 9999px, 96px, 0); }
  100% { clip: rect(1px, 9999px, 50px, 0); }
}

@keyframes glitch-anim-2 {
  0% { clip: rect(7px, 9999px, 95px, 0); }
  5% { clip: rect(89px, 9999px, 74px, 0); }
  10% { clip: rect(23px, 9999px, 67px, 0); }
  15% { clip: rect(79px, 9999px, 73px, 0); }
  20% { clip: rect(3px, 9999px, 64px, 0); }
  25% { clip: rect(25px, 9999px, 86px, 0); }
  30% { clip: rect(96px, 9999px, 69px, 0); }
  35% { clip: rect(53px, 9999px, 79px, 0); }
  40% { clip: rect(8px, 9999px, 98px, 0); }
  45% { clip: rect(93px, 9999px, 58px, 0); }
  50% { clip: rect(59px, 9999px, 94px, 0); }
  55% { clip: rect(1px, 9999px, 68px, 0); }
  60% { clip: rect(80px, 9999px, 76px, 0); }
  65% { clip: rect(80px, 9999px, 92px, 0); }
  70% { clip: rect(54px, 9999px, 60px, 0); }
  75% { clip: rect(21px, 9999px, 54px, 0); }
  80% { clip: rect(4px, 9999px, 70px, 0); }
  85% { clip: rect(90px, 9999px, 88px, 0); }
  90% { clip: rect(48px, 9999px, 69px, 0); }
  95% { clip: rect(8px, 9999px, 52px, 0); }
  100% { clip: rect(13px, 9999px, 94px, 0); }
}

</style>