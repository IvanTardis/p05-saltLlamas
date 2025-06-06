const canvas = document.getElementById('layer1');
const ctx = canvas.getContext('2d');

// Set canvas to full window size
const BASE_WIDTH = 800;
const BASE_HEIGHT = 450;
let scaleFactor = 1;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    scaleFactor = Math.min(canvas.width / BASE_WIDTH, canvas.height / BASE_HEIGHT);
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Environment definitions
const environments = {
    desert: {
        bg: document.getElementById('DesertBg'),
        mg1: document.getElementById('DesertMg1'),
        mg2: document.getElementById('DesertMg2'),
        fg: document.getElementById('DesertFg'),
        duration: 30 // seconds in this environment
    },
    jungle: {
        bg: document.getElementById('JungleBg'),
        mg1: document.getElementById('JungleMg1'),
        mg2: document.getElementById('JungleMg2'),
        fg: document.getElementById('JungleFg'),
        duration: 30 // seconds in this environment
    },
    mountain: {
        bg: document.getElementById('MountainBg'),
        mg1: document.getElementById('MountainMg1'),
        mg2: document.getElementById('MountainMg2'),
        fg: document.getElementById('MountainFg'),
        duration: 30 // seconds in this environment
    }
};

// Game state
const environmentOrder = ['desert', 'jungle', 'mountain'];
let currentEnvironmentIndex = 0;
let currentEnvironment = environmentOrder[currentEnvironmentIndex];
let nextEnvironment = environmentOrder[(currentEnvironmentIndex + 1) % environmentOrder.length]; // Use modulo for cycling
let environmentStartTime = 0;
let transitionProgress = 0; // 0-1 value for blending between environments

// Parallax layers configuration
const layers = [
    { speed: 0.2, y: 0, x: 0, name: "Background" },
    { speed: 0.4, y: 0, x: 0, name: "Midground 1" },
    { speed: 0.6, y: 0, x: 0, name: "Midground 2" },
    { speed: 1.0, y: 0, x: 0, name: "Foreground" }
];

// Animation variables
let animationId;
let lastTimestamp = 0;
const scrollSpeed = 50; // pixels per second
let totalTime = 0;

function updateEnvironment(elapsedTime) {
    const env = environments[currentEnvironment];
    const timeInEnvironment = elapsedTime - environmentStartTime;
    
    // Check if we need to transition to next environment
    if (timeInEnvironment >= env.duration) {
        const transitionDuration = 5; // seconds for transition
        const transitionStart = env.duration - transitionDuration;
        
        if (timeInEnvironment >= env.duration) {
            // Complete transition to next environment
            currentEnvironmentIndex = (currentEnvironmentIndex + 1) % environmentOrder.length; // Cycle back to 0 when reaching end
            currentEnvironment = environmentOrder[currentEnvironmentIndex];
            nextEnvironment = environmentOrder[(currentEnvironmentIndex + 1) % environmentOrder.length];
            environmentStartTime = elapsedTime;
            transitionProgress = 0;
        } else if (timeInEnvironment >= transitionStart) {
            // During transition period
            transitionProgress = (timeInEnvironment - transitionStart) / transitionDuration;
        }
    } else {
        // Check if we're in the transition period
        const transitionDuration = 5;
        const transitionStart = env.duration - transitionDuration;
        if (timeInEnvironment >= transitionStart) {
            transitionProgress = (timeInEnvironment - transitionStart) / transitionDuration;
        }
    }
}

function drawLayer(layer, env, alpha = 1, offsetX = 0) {
    let img;
    switch (layer.name) {
        case "Background": img = env.bg; break;
        case "Midground 1": img = env.mg1; break;
        case "Midground 2": img = env.mg2; break;
        case "Foreground": img = env.fg; break;
    }
    
    if (!img) return;
    
    ctx.globalAlpha = alpha;
    
    // Draw image twice for seamless scrolling
    const layerWidth = img.width * (canvas.height / img.height);
    const x1 = (offsetX % layerWidth) - layerWidth;
    const x2 = (offsetX % layerWidth);
    
    ctx.drawImage(img, x1, 0, layerWidth, canvas.height);
    ctx.drawImage(img, x2, 0, layerWidth, canvas.height);
}

function draw(timestamp) {
    if (!lastTimestamp) {
        lastTimestamp = timestamp;
        environmentStartTime = totalTime;
    }
    
    const deltaTime = (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;
    totalTime += deltaTime;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Update environment based on time
    updateEnvironment(totalTime);
    
    // Draw each layer
    layers.forEach(layer => {
        layer.x += layer.speed * scrollSpeed * deltaTime;
        
        // Draw current environment
        drawLayer(layer, environments[currentEnvironment], 1 - transitionProgress, layer.x);
        
        // Draw next environment during transition
        if (transitionProgress > 0) {
            drawLayer(layer, environments[nextEnvironment], transitionProgress, layer.x);
        }
    });
    
    animationId = requestAnimationFrame(draw);
}

// Start animation
animationId = requestAnimationFrame(draw);

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    cancelAnimationFrame(animationId);
});