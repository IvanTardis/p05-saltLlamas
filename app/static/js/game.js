const canvas = document.getElementById('layer1');
const ctx = canvas.getContext('2d');

const BASE_WIDTH = 800;
const BASE_HEIGHT = 450;
let scaleFactor = 1;

const fileInput = document.getElementById('file-input');
const wagon = document.getElementById('Wagon');
const customWagon = document.getElementById('CustomWagon');

let currentState = 'PLAY';
let selectedLayerIndex = 0;
let selectedEnvironmentIndex = 0; // 0=desert, 1=jungle, 2=mountain
let customizingWagon = false;

const customizeButtons = [
    { text: "Select Image", y: 350, action: "selectImage" },
    { text: "Close", y: 400, action: "closeCustomize" }
];

const environmentOptions = [
    { name: "Desert", key: "desert" },
    { name: "Jungle", key: "jungle" },
    { name: "Mountain", key: "mountain" }
];

const layerOptions = [
    { name: "Background", key: "bg" },
    { name: "Midground 1", key: "mg1" },
    { name: "Midground 2", key: "mg2" },
    { name: "Foreground", key: "fg" },
    { name: "Wagon", key: "wagon" }
];

const mouse = { x: 0, y: 0 };
let hoveredButton = null;

const environments = {
    desert: {
        bg: document.getElementById('DesertBg'),
        mg1: document.getElementById('DesertMg1'),
        mg2: document.getElementById('DesertMg2'),
        fg: document.getElementById('DesertFg'),
        duration: 30
    },
    jungle: {
        bg: document.getElementById('JungleBg'),
        mg1: document.getElementById('JungleMg1'),
        mg2: document.getElementById('JungleMg2'),
        fg: document.getElementById('JungleFg'),
        duration: 30
    },
    mountain: {
        bg: document.getElementById('MountainBg'),
        mg1: document.getElementById('MountainMg1'),
        mg2: document.getElementById('MountainMg2'),
        fg: document.getElementById('MountainFg'),
        duration: 30
    }
};

const environmentOrder = ['desert', 'jungle', 'mountain'];
let currentEnvironmentIndex = 0;
let currentEnvironment = environmentOrder[currentEnvironmentIndex];
let nextEnvironment = environmentOrder[(currentEnvironmentIndex + 1) % environmentOrder.length];
let environmentStartTime = 0;
let transitionProgress = 0;

const layers = [
    { speed: 0.2, y: 0, x: 0, name: "Background" },
    { speed: 0.4, y: 0, x: 0, name: "Midground 1" },
    { speed: 0.6, y: 0, x: 0, name: "Midground 2" },
    { speed: 1.0, y: 0, x: 0, name: "Foreground" }
];

const wagonConfig = {
    width: 200,
    height: 150,
    yOffset: .1,
    scale: 1,
    x: 0.6
};

let animationId;
let lastTimestamp = 0;
const scrollSpeed = 50;
let totalTime = 0;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    scaleFactor = Math.min(canvas.width / BASE_WIDTH, canvas.height / BASE_HEIGHT);
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

function drawLayer(layer, env, alpha = 1, offsetX = 0) {
    let img = env[layerOptions.find(l => l.name === layer.name).key];
    if (!img) return;

    ctx.globalAlpha = alpha;
    const layerWidth = img.width * (canvas.height / img.height);
    const x1 = (offsetX % layerWidth) - layerWidth;
    const x2 = (offsetX % layerWidth);

    ctx.drawImage(img, x1, 0, layerWidth, canvas.height);
    ctx.drawImage(img, x2, 0, layerWidth, canvas.height);
}

function drawWagon() {
    const imgToUse = customWagon.src ? customWagon : wagon;
    if (!imgToUse) return;

    const wagonScale = scaleFactor * wagonConfig.scale;
    const wagonWidth = wagonConfig.width * wagonScale;
    const wagonHeight = wagonConfig.height * wagonScale;
    const wagonX = canvas.width * wagonConfig.x - wagonWidth / 2;
    const wagonY = canvas.height * (1 - wagonConfig.yOffset) - wagonHeight;

    ctx.globalAlpha = 1;
    ctx.drawImage(imgToUse, wagonX, wagonY, wagonWidth, wagonHeight);
}

function updateEnvironment(elapsedTime) {
    const env = environments[currentEnvironment];
    const timeInEnvironment = elapsedTime - environmentStartTime;

    const transitionDuration = 5;
    const transitionStart = env.duration - transitionDuration;

    if (timeInEnvironment >= env.duration) {
        currentEnvironmentIndex = (currentEnvironmentIndex + 1) % environmentOrder.length;
        currentEnvironment = environmentOrder[currentEnvironmentIndex];
        nextEnvironment = environmentOrder[(currentEnvironmentIndex + 1) % environmentOrder.length];
        environmentStartTime = elapsedTime;
        transitionProgress = 0;
    } else if (timeInEnvironment >= transitionStart) {
        transitionProgress = (timeInEnvironment - transitionStart) / transitionDuration;
    }
}

function drawCustomizePopup() {
    const popupWidth = 500;
    const popupHeight = 400;
    const popupX = (canvas.width - popupWidth) / 2;
    const popupY = (canvas.height - popupHeight) / 2;

    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.strokeStyle = '#fadb32';
    ctx.lineWidth = 3;
    ctx.fillRect(popupX, popupY, popupWidth, popupHeight);
    ctx.strokeRect(popupX, popupY, popupWidth, popupHeight);

    ctx.font = "25px Arial";
    ctx.fillStyle = '#fadb32';
    ctx.textAlign = 'center';
    ctx.fillText("Customize Game Graphics", canvas.width / 2, popupY + 40);

    // Draw environment selection
    ctx.font = "20px Arial";
    ctx.fillStyle = '#fadb32';
    ctx.textAlign = 'left';
    ctx.fillText("Environment:", popupX + 20, popupY + 80);

    environmentOptions.forEach((env, index) => {
        const yPos = popupY + 110 + index * 30;
        const isSelected = index === selectedEnvironmentIndex;
        ctx.fillStyle = isSelected ? '#ffffff' : '#fadb32';
        if (isSelected) ctx.fillText(">", popupX + 20, yPos);
        ctx.fillText(env.name, popupX + 50, yPos);
    });

    // Draw layer selection (only if not customizing wagon)
    if (!customizingWagon) {
        ctx.fillText("Layer:", popupX + 20, popupY + 200);
        layerOptions.slice(0, 4).forEach((layer, index) => {
            const yPos = popupY + 230 + index * 30;
            const isSelected = index === selectedLayerIndex;
            ctx.fillStyle = isSelected ? '#ffffff' : '#fadb32';
            if (isSelected) ctx.fillText(">", popupX + 20, yPos);
            ctx.fillText(layer.name, popupX + 50, yPos);
        });
    } else {
        ctx.fillStyle = '#ffffff';
        ctx.fillText("Customizing Wagon", popupX + 50, popupY + 230);
    }

    // Draw wagon customization option
    const wagonYPos = popupY + 350;
    const isWagonSelected = customizingWagon;
    ctx.fillStyle = isWagonSelected ? '#ffffff' : '#fadb32';
    if (isWagonSelected) ctx.fillText(">", popupX + 20, wagonYPos);
    ctx.fillText("Wagon", popupX + 50, wagonYPos);

    // Draw action buttons
    hoveredButton = null;
    ctx.font = "18px Arial";
    ctx.textAlign = 'left';

    customizeButtons.forEach(button => {
        const textWidth = ctx.measureText(button.text).width;
        const buttonLeft = (canvas.width - textWidth) / 2;
        const buttonRight = buttonLeft + textWidth;
        const buttonTop = button.y - 20;
        const buttonBottom = button.y;

        const isHovered = mouse.x >= buttonLeft && mouse.x <= buttonRight &&
                          mouse.y >= buttonTop && mouse.y <= buttonBottom;

        if (isHovered) {
            hoveredButton = button;
            ctx.fillStyle = '#ffffff';
        } else {
            ctx.fillStyle = '#fadb32';
        }

        ctx.fillText(button.text, buttonLeft, button.y);
    });
}

function handleCanvasClick() {
    if (currentState === 'CUSTOMIZE') {
        const popupX = (canvas.width - 500) / 2;
        const popupY = (canvas.height - 400) / 2;

        // Check environment selection
        environmentOptions.forEach((env, index) => {
            const yPos = popupY + 110 + index * 30;
            const textWidth = ctx.measureText(env.name).width;

            if (mouse.x >= popupX + 50 && mouse.x <= popupX + 50 + textWidth &&
                mouse.y >= yPos - 20 && mouse.y <= yPos) {
                selectedEnvironmentIndex = index;
                customizingWagon = false;
            }
        });

        // Check layer selection (only if not customizing wagon)
        if (!customizingWagon) {
            layerOptions.slice(0, 4).forEach((layer, index) => {
                const yPos = popupY + 230 + index * 30;
                const textWidth = ctx.measureText(layer.name).width;

                if (mouse.x >= popupX + 50 && mouse.x <= popupX + 50 + textWidth &&
                    mouse.y >= yPos - 20 && mouse.y <= yPos) {
                    selectedLayerIndex = index;
                    customizingWagon = false;
                }
            });
        }

        // Check wagon selection - updated y position to 350
        const wagonYPos = popupY + 350;
        const wagonTextWidth = ctx.measureText("Wagon").width;
        if (mouse.x >= popupX + 50 && mouse.x <= popupX + 50 + wagonTextWidth &&
            mouse.y >= wagonYPos - 20 && mouse.y <= wagonYPos) {
            customizingWagon = true;
            selectedLayerIndex = 4;
        }

        if (hoveredButton?.action === "selectImage") {
            fileInput.click();
        } else if (hoveredButton?.action === "closeCustomize") {
            currentState = 'PLAY';
            customizingWagon = false;
        }
    } else {
        currentState = 'CUSTOMIZE';
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            if (customizingWagon) {
                customWagon.src = e.target.result;
                wagon.src = e.target.result;
                sendImageToDatabase(file, 'wagon');
            } else {
                const envKey = environmentOptions[selectedEnvironmentIndex].key;
                const layerKey = layerOptions[selectedLayerIndex].key;
                environments[envKey][layerKey] = img;
                sendImageToDatabase(file, `${envKey}_${layerKey}`);
            }
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function sendImageToDatabase(file, imageType) {
    const formData = new FormData();
    formData.append("image", file);
    formData.append("type", imageType);

    fetch("/upload-image", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => console.log("Uploaded:", data))
    .catch(err => console.error("Upload error:", err));
}

function draw(timestamp) {
    if (!lastTimestamp) {
        lastTimestamp = timestamp;
        environmentStartTime = totalTime;
    }

    const deltaTime = (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;
    totalTime += deltaTime;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    updateEnvironment(totalTime);

    layers.forEach(layer => {
        layer.x += layer.speed * scrollSpeed * deltaTime;

        drawLayer(layer, environments[currentEnvironment], 1 - transitionProgress, layer.x);

        if (transitionProgress > 0) {
            drawLayer(layer, environments[nextEnvironment], transitionProgress, layer.x);
        }
    });

    drawWagon();

    if (currentState === 'CUSTOMIZE') {
        drawCustomizePopup();
    }

    animationId = requestAnimationFrame(draw);
}

canvas.addEventListener('click', handleCanvasClick);
canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = (e.clientX - rect.left);
    mouse.y = (e.clientY - rect.top);
});
fileInput.addEventListener('change', handleFileUpload);
animationId = requestAnimationFrame(draw);

window.addEventListener('beforeunload', () => cancelAnimationFrame(animationId));