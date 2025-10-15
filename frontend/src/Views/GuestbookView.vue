<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

// --- HELPER FUNCTION to get the CSRF token from cookies ---
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// --- COMPONENT LOGIC ---
const entries = ref([]);
const newEntry = ref('');
const newName = ref('');
const isLoading = ref(true);
const errorMessage = ref('');
const currentUser = ref(null);

// --- API FUNCTIONS ---

// Fetches the current logged-in user from your Django backend
async function fetchCurrentUser() {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/guestbook/user/', {
      credentials: 'include', // Crucial: Sends session cookies with the request
      headers: { 'Accept': 'application/json' },
    });
    if (response.ok) {
      currentUser.value = await response.json();
    } else {
      currentUser.value = null; // User is not logged in
    }
  } catch (error) {
    currentUser.value = null;
    errorMessage.value = 'Cannot connect to authentication service.';
    console.error('API error while fetching user:', error);
  }
}

// Fetches all guestbook entries
async function fetchEntries() {
  try {
    isLoading.value = true;
    errorMessage.value = ''; // Reset error on new fetch
    const response = await fetch('http://127.0.0.1:8000/api/guestbook/');
    if (!response.ok) throw new Error('Failed to fetch entries.');
    const data = await response.json();
    entries.value = data;
  } catch (error) {
    errorMessage.value = 'Could not connect to the guestbook archives.';
    console.error(error);
  } finally {
    isLoading.value = false;
  }
}

// Submits a new entry (only if logged in)
async function submitEntry() {
  if (!newEntry.value.trim() || !currentUser.value) return;

  try {
    errorMessage.value = ''; // Reset previous errors
    const csrftoken = getCookie('csrftoken');
    const response = await fetch('http://127.0.0.1:8000/api/guestbook/create/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({
        message: newEntry.value,
      }),
    });

    if (!response.ok) {
      if (response.status === 403) {
        errorMessage.value = 'Authentication failed. Please log in again.';
        currentUser.value = null; // CORRECTED: Force UI to logged-out state on auth failure
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit entry.');
      }
    } else {
      // IMPROVED: Instead of re-fetching all entries, add the new one to the list
      const createdEntry = await response.json();
      entries.value.unshift(createdEntry); // Adds the new entry to the top of the list
      newEntry.value = '';
    }
  } catch (error) {
    errorMessage.value = 'Your message could not be transmitted.';
    console.error(error);
  }
}

// --- BACKGROUND ANIMATION SCRIPT (Unchanged) ---
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
// --- LIFECYCLE HOOKS ---
onMounted(async () => {
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

  // --- Fetch initial data ---
  await fetchCurrentUser(); // First, check if user is logged in
  await fetchEntries();   // Then, fetch the entries
});

onBeforeUnmount(() => {
    // --- Cleanup Background Animation ---
    cancelAnimationFrame(animationFrameId);
    // IMPROVED: Correctly reference the functions for removal
    window.removeEventListener('resize', handleResize);
    window.removeEventListener('mousemove', handleMouseMove);
});
</script>

<template>
  <div class="guestbook-view" ref="canvasContainer">
    <div class="scanline"></div>
    <div class="content-grid">
      <div class="header-section">
        <h1 class="page-title">Guestbook</h1>
        <p class="page-subtitle">Leave your transmission in the project archives</p>
      </div>

      <div class="form-panel">
        <div v-if="currentUser" class="user-profile-container">
          <img v-if="currentUser.avatar_url" :src="currentUser.avatar_url" alt="User Avatar" class="user-avatar"/>
          <div class="user-details">
            <input type="text" :value="currentUser.username" id="nameInput" required class="input-field" disabled />
            <label for="nameInput" class="input-label" style="top: -1rem; font-size: 0.8rem;">Callsign (Name)</label>
          </div>
        </div>

        <div v-else class="input-group">
          <input type="text" v-model="newName" id="nameInput" required class="input-field" disabled />
          <label for="nameInput" class="input-label">Login to use your Callsign</label>
        </div>

        <div class="input-group">
          <textarea 
            v-model="newEntry" 
            id="messageInput" 
            required 
            class="input-field" 
            rows="4" 
            :disabled="!currentUser" 
            :placeholder="currentUser ? 'Enter your message...' : 'Please log in to leave a message.'"
          ></textarea>
          <label for="messageInput" class="input-label">Message</label>
        </div>
        
        <button v-if="currentUser" @click="submitEntry" class="submit-button">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          <span>Transmit</span>
        </button>
        <a v-else href="http://127.0.0.1:8000/accounts/github/login/" class="submit-button">
            <svg viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.91 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
            <span>Authenticate with GitHub</span>
        </a>
      </div>

      <div class="entries-panel">
        <h2 class="panel-title">Transmission Log</h2>
        <div v-if="isLoading" class="loading-state">
            <div class="signal-loader">
                <div class="signal-bar"></div><div class="signal-bar"></div><div class="signal-bar"></div>
            </div>
            <p>Accessing archives...</p>
        </div>
        <div v-if="errorMessage" class="error-state">
            <p>{{ errorMessage }}</p>
        </div>
        <div v-if="!isLoading && entries.length" class="entries-list">
            <div v-for="(entry, index) in entries" :key="entry.id" class="entry-card" :style="{ '--delay': `${index * 75}ms` }">
                <p class="entry-message">{{ entry.message }}</p>
                <div class="entry-footer">
                    <span class="entry-name">from: {{ entry.user }}</span>
                    <span class="entry-date">timestamp: {{ new Date(entry.created_at).toISOString() }}</span>
                </div>
            </div>
        </div>
        <div v-if="!isLoading && !entries.length" class="empty-state">
            <p>No transmissions logged. Be the first.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.guestbook-view {
  width: 100%;
  min-height: 100vh;
  padding: 4rem 2rem;
  box-sizing: border-box;
  background-color: var(--bg-color);
  position: relative;
  overflow: hidden;
}

:deep(#stardust-canvas) {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.scanline {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: linear-gradient(
    0deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.03) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  background-size: 100% 4px;
  animation: scanlines 10s linear infinite;
  z-index: 2;
}

@keyframes scanlines {
  from { background-position: 0 0; }
  to { background-position: 0 100px; }
}

.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  grid-template-rows: auto 1fr;
  gap: 2.5rem;
  grid-template-areas:
    "header header"
    "form entries";
}

.header-section { grid-area: header; }
.form-panel { grid-area: form; }
.entries-panel { grid-area: entries; }

.page-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 500;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  text-align: center;
  font-size: 1.1rem;
  color: var(--secondary-text);
  margin-bottom: 1rem;
}

.form-panel {
  background: rgba(13, 13, 13, 0.7);
  -webkit-backdrop-filter: blur(15px);
  backdrop-filter: blur(15px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  height: fit-content;
}

.input-group {
  position: relative;
}

.input-field {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border-color);
  padding: 0.8rem 0;
  color: var(--primary-text);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
  resize: vertical;
}

.input-label {
  position: absolute;
  top: 0.8rem;
  left: 0;
  color: var(--secondary-text);
  pointer-events: none;
  transition: all 0.3s ease;
}

.input-field:focus + .input-label,
.input-field:valid + .input-label,
.input-field:disabled + .input-label {
  top: -1rem;
  font-size: 0.8rem;
  color: var(--primary-text);
}

.input-field:focus {
  border-bottom-color: var(--accent-glow);
}

.submit-button {
  align-self: flex-start;
  padding: 0.8rem 1.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: transparent;
  color: var(--secondary-text);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.submit-button svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
  transition: transform 0.3s ease;
}

.submit-button:hover {
  background-color: var(--accent-glow);
  color: var(--bg-color);
  border-color: var(--accent-glow);
  box-shadow: 0 0 15px var(--accent-glow);
}

.submit-button:hover svg {
  transform: translateX(5px);
}

.entries-panel {
  background: rgba(13, 13, 13, 0.7);
  -webkit-backdrop-filter: blur(15px);
  backdrop-filter: blur(15px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  height: 70vh;
}

.panel-title {
  font-size: 1.2rem;
  font-weight: 500;
  margin: 0 0 1.5rem 0;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--secondary-text);
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--secondary-text);
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.signal-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px;
  gap: 8px;
  margin: 0 auto 1.5rem;
}

.signal-bar {
  width: 6px;
  height: 100%;
  background-color: var(--accent-glow);
  animation: signal 1.2s infinite ease-in-out;
}

.signal-bar:nth-child(2) { animation-delay: 0.2s; }
.signal-bar:nth-child(3) { animation-delay: 0.4s; }

@keyframes signal {
  0%, 100% { transform: scaleY(0.2); }
  50% { transform: scaleY(1); }
}

.entries-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
  flex-grow: 1;
  padding-right: 1rem;
}

.entries-list::-webkit-scrollbar { width: 4px; }
.entries-list::-webkit-scrollbar-track { background: transparent; }
.entries-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}
.entries-list {
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.entry-card {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1.5rem;
  opacity: 0;
  animation: card-fade-in 0.6s ease forwards;
  animation-delay: var(--delay);
}

.entry-message {
  font-family: 'Space Mono', monospace;
  font-size: 1rem;
  line-height: 1.7;
  margin: 0 0 1rem 0;
  color: var(--primary-text);
}

.entry-footer {
  font-family: 'Space Mono', monospace;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--secondary-text);
}

@keyframes card-fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-profile-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  flex-shrink: 0;
}

.user-details {
  position: relative;
  flex-grow: 1;
}

</style>