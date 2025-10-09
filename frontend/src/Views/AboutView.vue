<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';

const canvasContainer = ref(null);
let canvas, ctx, particles, animationFrameId;

// --- Perlin Noise Generator (for organic flow) ---
const Perlin = {
    // ... (A self-contained Perlin Noise implementation)
    // This creates the smooth, flowing effect.
    rand_vect: function(){
        let theta = Math.random() * 2 * Math.PI;
        return {x: Math.cos(theta), y: Math.sin(theta)};
    },
    dot_prod_grid: function(x, y, vx, vy){
        let g_vect;
        let d_vect = {x: x - vx, y: y - vy};
        if (this.gradients[[vx,vy]]){
            g_vect = this.gradients[[vx,vy]];
        } else {
            g_vect = this.rand_vect();
            this.gradients[[vx,vy]] = g_vect;
        }
        return d_vect.x * g_vect.x + d_vect.y * g_vect.y;
    },
    smootherstep: function(x){
        return 6*x**5 - 15*x**4 + 10*x**3;
    },
    interp: function(x, a, b){
        return a + this.smootherstep(x) * (b-a);
    },
    seed: function(){
        this.gradients = {};
        this.memory = {};
    },
    get: function(x, y) {
        if (this.memory.hasOwnProperty([x,y]))
            return this.memory[[x,y]];
        let xf = Math.floor(x);
        let yf = Math.floor(y);
        //interpolate
        let tl = this.dot_prod_grid(x, y, xf,   yf);
        let tr = this.dot_prod_grid(x, y, xf+1, yf);
        let bl = this.dot_prod_grid(x, y, xf,   yf+1);
        let br = this.dot_prod_grid(x, y, xf+1, yf+1);
        let xt = this.interp(x-xf, tl, tr);
        let xb = this.interp(x-xf, bl, br);
        let v = this.interp(y-yf, xt, xb);
        this.memory[[x,y]] = v;
        return v;
    }
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

        // Reset particle if it goes off-screen
        if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
        }

        // Mouse interaction
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
function init() {
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
    canvasContainer.value.appendChild(canvas);
    ctx = canvas.getContext('2d');

    const mouse = { x: undefined, y: undefined, radius: 150 };
    const handleMouseMove = (event) => { mouse.x = event.x; mouse.y = event.y; };
    window.addEventListener('mousemove', handleMouseMove);

    const handleResize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        init();
    };
    window.addEventListener('resize', handleResize);
    
    handleResize();
    animate(mouse);
});

onBeforeUnmount(() => {
    cancelAnimationFrame(animationFrameId);
    window.removeEventListener('resize', () => {});
    window.removeEventListener('mousemove', () => {});
});
</script>

<template>
  <div class="about-view" ref="canvasContainer">
    <div class="content-overlay">
      <div class="info-panel card-fade-in" style="--delay: 100ms;">
        <h1 class="panel-title">About Eden</h1>
        <p>
          Welcome to <strong>Eden</strong>, a forward-thinking culinary platform designed to blend nutritional science with artificial intelligence. Our core mission is to empower users to make smarter, healthier, and more delicious food choices.
        </p>
        <p>
          At the heart of Eden is <strong>Pipo</strong>, our advanced AI assistant. Pipo drives our powerful nutrient analysis engine, helps you discover new recipes, and provides a seamless, intelligent interface for your culinary journey.
        </p>
      </div>

      <div class="info-panel card-fade-in" style="--delay: 300ms;">
        <h2 class="panel-title">Contact & Collaboration</h2>
        <p>This project is actively developed and maintained. For inquiries, feature requests, or collaboration opportunities, please use the following channels:</p>
        <ul class="contact-list">
          <li><strong>Lead Developer:</strong> rixscx</li>
          <li><strong>Email:</strong> contact@edensystems.dev</li>
          <li><strong>GitHub Organization:</strong> /Eden</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about-view {
  width: 100%;
  min-height: 100%;
  padding: 4rem 2rem;
  box-sizing: border-box;
  background-color: #000;
  position: relative;
  overflow: hidden;
}

:deep(#stardust-canvas) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.content-overlay {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  position: relative;
  z-index: 1;
}

.info-panel {
  background: rgba(13, 13, 13, 0.7);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.panel-title {
  font-size: 1.8rem;
  font-weight: 500;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
  text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}

p, li {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--secondary-text);
}

p strong, li strong {
    color: var(--primary-text);
    font-weight: 500;
}

.contact-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-fade-in {
  opacity: 0;
  transform: translateY(20px);
  animation: card-fade-in 0.6s ease forwards;
  animation-delay: var(--delay);
}

@keyframes card-fade-in {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
