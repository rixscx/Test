<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';
import GLOBE from 'vanta/dist/vanta.globe.min'; // Import the GLOBE effect
import * as THREE from 'three';

const vantaContainer = ref(null);
let vantaEffect = null;

onMounted(() => {
  vantaEffect = GLOBE({
    el: vantaContainer.value,
    THREE: THREE,
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    scale: 1.00,
    scaleMobile: 1.00,
    color: 0xffffff,      // Dot color: white
    color2: 0xffffff,     // Not used in this effect
    backgroundColor: 0x0, // Background: pure black
    size: 0.7,
  });
});

onBeforeUnmount(() => {
  if (vantaEffect) vantaEffect.destroy();
});

// --- Script for the new heading effect ---
const titleRef = ref(null);
const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

const handleTitleMouseOver = (event) => {
    let iteration = 0;
    const interval = setInterval(() => {
        event.target.innerText = event.target.innerText.split("")
            .map((letter, index) => {
                if(index < iteration) {
                    return event.target.dataset.value[index];
                }
                return letters[Math.floor(Math.random() * 26)]
            })
            .join("");

        if(iteration >= event.target.dataset.value.length){
            clearInterval(interval);
        }
        iteration += 1 / 3;
    }, 30);
}
</script>

<template>
  <div class="home-container" ref="vantaContainer">
    <div class="content-overlay">
      <h1 
        class="page-title fade-in-up-1" 
        data-value="EDEN" 
        ref="titleRef"
        @mouseover="handleTitleMouseOver"
      >
        EDEN
      </h1>
      <p class="fade-in-up-2">Analyze nutrition. Discover recipes. Elevate your culinary journey.</p>
      <div class="feature-box fade-in-up-3">
        <router-link to="/analyzer" class="start-button">
          <span class="button-text">Start Analyzing</span>
          <div class="button-grid"></div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.content-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  box-sizing: border-box;
}

/* --- NEW HEADING STYLE --- */
.page-title {
  font-family: 'Space Mono', monospace; /* A more technical font */
  font-size: 5rem;
  font-weight: 600;
  letter-spacing: 0.5rem;
  color: var(--primary-text);
  cursor: default;
  transition: text-shadow 0.3s ease;
}
.page-title:hover {
    text-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
}

p {
  font-size: 1.2rem;
  color: var(--secondary-text);
  max-width: 500px;
  margin-top: -1rem;
}

/* --- ENHANCED BUTTON STYLE --- */
.start-button {
  margin-top: 3rem;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--primary-text);
  background-color: transparent;
  border: 1px solid var(--border-color);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 0 100%);
}

.button-text {
    position: relative;
    z-index: 2;
}

.button-grid {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    z-index: 0;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.start-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 1px solid var(--accent-glow);
    clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 0 100%);
    transform: translateX(-101%);
    transition: transform 0.4s ease;
    z-index: 1;
}

.start-button:hover {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: var(--primary-text);
}

.start-button:hover .button-grid {
    opacity: 1;
}

.start-button:hover::before {
    transform: translateX(0);
    animation: scan-line 2s linear infinite;
}

@keyframes scan-line {
    0% { transform: translateX(-101%); }
    50% { transform: translateX(101%); }
    51% { transform: translateX(-101%); }
    100% { transform: translateX(-101%); }
}


/* --- ANIMATIONS --- */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up-1 { animation: fadeInUp 0.8s ease-out forwards; }
.fade-in-up-2 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.3s forwards; }
.fade-in-up-3 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.6s forwards; }
</style>