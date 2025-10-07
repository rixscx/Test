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
</script>

<template>
  <div class="home-container" ref="vantaContainer">
    <div class="content-overlay">
      <h1 class="fade-in-up-1">PANTS AI</h1>
      <p class="fade-in-up-2">Analyze nutrition. Discover recipes. Elevate your culinary journey.</p>
      <div class="feature-box fade-in-up-3">
        <router-link to="/analyzer" class="start-button">Start Analyzing</router-link>
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

h1 {
  font-size: 3.5rem;
  color: var(--primary-text);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

p {
  font-size: 1.2rem;
  color: var(--secondary-text);
  max-width: 500px;
}

.start-button {
  margin-top: 2rem;
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  color: var(--primary-text);
  background-color: transparent;
  border: 2px solid var(--primary-text);
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.start-button:hover {
  background-color: var(--primary-text);
  color: var(--bg-color);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up-1 { animation: fadeInUp 0.8s ease-out forwards; }
.fade-in-up-2 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.3s forwards; }
.fade-in-up-3 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.6s forwards; }
</style>
