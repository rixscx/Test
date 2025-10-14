<script setup>
import { ref, watch, nextTick } from 'vue';

const isChatOpen = ref(false);
const chatContainerRef = ref(null);
const neuralNodeRef = ref(null);

const initialMessage = { id: 1, text: "I am Pipo. Systems online.", sender: 'bot' };
const messages = ref([]);
const userInput = ref('');
const isBotTyping = ref(false);
const showConstruction = ref(false);
const isClosing = ref(false); // State to track closing animation

// Updated function for symmetrical open/close animations
const toggleChat = () => {
  if (isChatOpen.value) {
    // --- Start Closing Sequence ---
    isClosing.value = true;
    isChatOpen.value = false; // Triggers chat window fade out
    showConstruction.value = true; // Show wireframe for "un-draw" animation
    
    setTimeout(() => {
      showConstruction.value = false;
      isClosing.value = false; // Reset state after animation
    }, 800); // Matches animation duration
  } else {
    // --- Start Opening Sequence ---
    isClosing.value = false;
    showConstruction.value = true;
    setTimeout(() => {
      isChatOpen.value = true;
      if (messages.value.length === 0) {
        setTimeout(() => typeBotMessage(initialMessage.text), 500);
      }
    }, 800); // Wait for construction animation
    
    setTimeout(() => {
      // Hide the wireframe only if we are not in the middle of closing
      if (!isClosing.value) {
        showConstruction.value = false;
      }
    }, 1600);
  }
};

const typeBotMessage = (responseText) => {
  isBotTyping.value = true;
  let partialText = '';
  const newMessage = {
    id: Date.now(),
    text: '',
    sender: 'bot'
  };
  messages.value.push(newMessage);
  
  const messageIndex = messages.value.length - 1;
  let charIndex = 0;

  const typingInterval = setInterval(() => {
    if (charIndex < responseText.length) {
      partialText += responseText[charIndex];
      messages.value[messageIndex].text = partialText;
      charIndex++;
    } else {
      clearInterval(typingInterval);
      isBotTyping.value = false;
    }
  }, 30);
};

const sendMessage = () => {
  const text = userInput.value.trim();
  if (text === '' || isBotTyping.value) return;

  messages.value.push({
    id: Date.now(),
    text: text,
    sender: 'user'
  });
  userInput.value = '';

  setTimeout(() => {
    const cannedResponse = "Your query has been processed. I am capable of analyzing a wide spectrum of data. Please proceed with your next inquiry.";
    typeBotMessage(cannedResponse);
  }, 1000);
};

const handleClickOutside = (event) => {
  if (isChatOpen.value &&
      chatContainerRef.value &&
      !chatContainerRef.value.contains(event.target) &&
      neuralNodeRef.value &&
      !neuralNodeRef.value.contains(event.target)) {
    toggleChat();
  }
};

watch(isChatOpen, (isOpen) => {
  if (isOpen) {
    nextTick(() => {
      document.addEventListener('mousedown', handleClickOutside);
    });
  } else {
    document.removeEventListener('mousedown', handleClickOutside);
  }
});

watch(messages, () => {
  nextTick(() => {
    const chatArea = document.querySelector('.chat-messages');
    if (chatArea) {
      chatArea.scrollTop = chatArea.scrollHeight;
    }
  });
}, { deep: true });

</script>

<template>
  <div id="app">
    <nav class="main-nav">
      <router-link to="/">Home</router-link>
      <router-link to="/analyzer">Analyzer</router-link>
      <router-link to="/recipes">Recipes</router-link>
      <router-link to="/guestbook">Guestbook</router-link>
      <router-link to="/about">About</router-link>
    </nav>
    
    <main class="content-area">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <div class="chatbot-container">
        <transition name="construct-fade">
            <svg v-if="showConstruction" class="construction-svg" viewBox="0 0 400 600">
                <rect :class="['construct-wireframe', { 'closing': isClosing }]" x="1" y="1" width="398" height="598" rx="24"/>
            </svg>
        </transition>

        <transition name="construct-materialize">
            <div v-if="isChatOpen" class="neural-construct" ref="chatContainerRef">
                <div class="neural-bg layer1"></div>
                <div class="neural-bg layer2"></div>
                <div class="neural-bg layer3"></div>

                <header class="chat-header">
                    <div class="header-title"><h3>Pipo</h3></div>
                    <button @click="toggleChat" class="close-btn" aria-label="Close Chat">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                    </button>
                </header>
        
                <main class="chat-messages">
                    <div v-for="(message, index) in messages" 
                         :key="message.id" 
                         :class="['message-wrapper', message.sender]"
                         :style="{ '--index': index }">
                        <div class="message">
                            {{ message.text }}
                            <span v-if="message.sender === 'bot' && isBotTyping && messages[messages.length - 1].id === message.id" class="typing-cursor"></span>
                        </div>
                    </div>
                    <div v-if="isBotTyping && messages[messages.length-1]?.sender !== 'bot'" class="message-wrapper bot">
                        <div class="message typing-node">
                            <div class="particle"></div><div class="particle"></div><div class="particle"></div>
                        </div>
                    </div>
                </main>
        
                <footer class="chat-input-area">
                    <input type="text" placeholder="Initiate query..." v-model="userInput" @keyup.enter="sendMessage"/>
                    <button class="send-btn" @click="sendMessage" aria-label="Send Message">
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </footer>
            </div>
      </transition>

      <button class="neural-node" @click="toggleChat" :class="{ 'open': isChatOpen }" aria-label="Open Pipo" ref="neuralNodeRef">
        <svg class="node-svg" viewBox="0 0 100 100">
            <path class="node-path" d="M50 10 L90 50 L50 90 L10 50 Z" />
            <path class="node-path" d="M20 20 L80 80 M80 20 L20 80" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style>
/* --- Global Styles --- */
:root {
  --bg-color: #000000;
  --surface-color: #0d0d0d;
  --primary-text: #e5e5e5;
  --secondary-text: #888888;
  --border-color: #222;
  --accent-glow: #ffffff;
}
body { font-family: 'Poppins', sans-serif; background-color: var(--bg-color); color: var(--primary-text); margin: 0; }
#app { display: flex; flex-direction: column; height: 100vh; }
.main-nav { flex-shrink: 0; display: flex; justify-content: center; padding: 1.5rem; background-color: var(--bg-color); border-bottom: 1px solid var(--border-color); position: relative; z-index: 100; }
.main-nav a { color: var(--secondary-text); margin: 0 20px; text-decoration: none; font-size: 1.1rem; font-weight: 500; transition: color 0.3s; }
.main-nav a.router-link-exact-active, .main-nav a:hover { color: var(--primary-text); }
.content-area { flex-grow: 1; position: relative; overflow-y: auto; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* --- NEURAL CONSTRUCT STYLES --- */
.chatbot-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 400px;
    height: 600px;
    pointer-events: none;
    z-index: 1001;
}

/* Neural Node Trigger */
.neural-node {
  position: absolute; bottom: 0; right: 0;
  width: 64px; height: 64px;
  background: transparent; border: none;
  cursor: pointer; pointer-events: all;
  transition: all 0.5s ease;
  z-index: 2;
}
.neural-node.open { transform: scale(0); opacity: 0; }
.neural-node .node-svg { width: 100%; height: 100%; overflow: visible; }
.neural-node .node-path {
  fill: none; stroke: var(--accent-glow); stroke-width: 2;
  stroke-linecap: round;
  filter: drop-shadow(0 0 2px var(--accent-glow));
  animation: morph-node 8s infinite ease-in-out, rotate-node 12s infinite linear;
  transform-origin: center;
}
@keyframes morph-node { 50% { transform: scale(0.8) rotate(180deg); } }
@keyframes rotate-node { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Construction Animation */
.construction-svg {
    position: absolute; bottom: 0; right: 0;
    width: 400px; height: 600px;
    pointer-events: none;
    z-index: 1;
    overflow: visible;
}
.construct-wireframe {
    fill: none; stroke: var(--accent-glow); stroke-width: 2px;
    stroke-dasharray: 2000;
    stroke-dashoffset: 2000;
    animation: draw-wireframe 0.8s ease-out forwards;
}
.construct-wireframe.closing {
    stroke-dashoffset: 0;
    animation: undraw-wireframe 0.8s ease-in forwards;
}
@keyframes draw-wireframe { to { stroke-dashoffset: 0; } }
@keyframes undraw-wireframe { from { stroke-dashoffset: 0; } to { stroke-dashoffset: 2000; } }

.construct-fade-leave-active { transition: opacity 0.5s ease 0.3s; }
.construct-fade-leave-to { opacity: 0; }

/* Chat Window */
.neural-construct {
  position: absolute; bottom: 0; right: 0;
  width: 400px; height: 600px;
  max-height: calc(100vh - 120px);
  display: flex; flex-direction: column;
  background-color: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  pointer-events: all;
}
.construct-materialize-enter-active { transition: all 0.5s ease 0.3s; }
.construct-materialize-leave-active { transition: all 0.3s ease; }
.construct-materialize-enter-from, .construct-materialize-leave-to { opacity: 0; transform: scale(0.95); }

/* Neural BG */
.neural-bg {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><defs><pattern id="p" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="%23fff"/></pattern></defs><rect width="100%" height="100%" fill="url(%23p)"/></svg>');
    opacity: 0.05;
}
.layer1 { animation: drift 30s linear infinite; }
.layer2 { animation: drift 40s linear infinite reverse; transform: scale(1.5); }
.layer3 { animation: drift 50s linear infinite; transform: scale(0.8); }
@keyframes drift { from { transform: translate(0,0); } to { transform: translate(100px, 50px); } }

/* Header & Input */
.chat-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; flex-shrink: 0; border-bottom: 1px solid var(--border-color); background: var(--surface-color); }
.header-title h3 { margin: 0; font-weight: 500; letter-spacing: 1px; }
.close-btn { background: none; border: none; cursor: pointer; color: var(--secondary-text); fill: var(--secondary-text); transition: all 0.2s; }
.close-btn:hover { color: var(--primary-text); fill: var(--primary-text); transform: scale(1.1); }
.chat-input-area { display: flex; padding: 1rem; border-top: 1px solid var(--border-color); align-items: center; background: var(--surface-color); }
.chat-input-area input { flex-grow: 1; border: none; background: transparent; color: var(--primary-text); padding: 0.5rem 0; font-size: 1rem; line-height: 1.5; outline: none; }
.send-btn { background: none; border: none; cursor: pointer; color: var(--primary-text); fill: var(--primary-text); width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.send-btn:hover { transform: scale(1.2); }

/* Messages Area */
.chat-messages { flex-grow: 1; padding: 1rem; overflow-y: auto; display: flex; flex-direction: column; position: relative; }
.message-wrapper { display: flex; flex-direction: column; animation: new-message-pop 0.5s forwards; animation-delay: calc(var(--index) * 50ms); opacity: 0; position: relative; }
.message-wrapper.user { align-items: flex-end; }
.message-wrapper.bot { align-items: flex-start; }
.message-wrapper + .message-wrapper::before { content: ''; position: absolute; top: -0.5rem; left: 1.5rem; width: 1px; height: 1rem; background-color: var(--border-color); }
.message-wrapper.user + .message-wrapper.bot::before, .message-wrapper.bot + .message-wrapper.user::before { left: 50%; }
.message-wrapper.user + .message-wrapper.user::before { left: auto; right: 1.5rem; }
.message { padding: 0.8rem 1.2rem; border-radius: 12px; max-width: 85%; line-height: 1.5; word-wrap: break-word; border: 1px solid var(--border-color); margin-bottom: 1rem; }
.message-wrapper.bot .message { background: var(--surface-color); }
.message-wrapper.user .message { background: var(--primary-text); color: #1c1c1e; }
@keyframes new-message-pop { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.typing-cursor { display: inline-block; width: 3px; height: 1em; background-color: var(--primary-text); margin-left: 5px; animation: blink 1s infinite; vertical-align: text-bottom; }
@keyframes blink { 50% { opacity: 0; } }

/* Bot Typing Node */
.typing-node { border: 1px dashed var(--border-color); display: flex; justify-content: center; align-items: center; gap: 5px; height: 40px; }
.particle { width: 6px; height: 6px; background: var(--accent-glow); border-radius: 50%; animation: particle-flow 1.2s infinite ease-in-out; }
.particle:nth-child(2) { animation-delay: 0.2s; }
.particle:nth-child(3) { animation-delay: 0.4s; }
@keyframes particle-flow { 0%, 100% { transform: scale(0.5); opacity: 0.5; } 50% { transform: scale(1); opacity: 1; } }
</style>