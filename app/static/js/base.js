const canvas = document.getElementById('layer1');
const ctx = canvas.getContext('2d');
const fileInput = document.getElementById('file-input');

const BASE_WIDTH = 800;
const BASE_HEIGHT = 450;
let scaleFactor = 1;

const STATE = {
    MENU: 0,
    CUSTOMIZE: 1
};
let currentState = STATE.MENU;
let selectedLayerIndex = 0;

const layers = [
    { img: document.getElementById('layer-5'), speed: 0.01/2, y: 0, name: "Background" },
    { img: document.getElementById('layer-4'), speed: 0.05/2, y: 0, name: "Midground 1" },
    { img: document.getElementById('layer-3'), speed: 0.1/2, y: 0, name: "Midground 2" },
    { img: document.getElementById('layer-6'), speed: 1.0/2, y: 0, name: "Foreground" },
];
const positions = layers.map(() => ({ x1: 0, x2: BASE_WIDTH }));

const menuButtons = [
    { text: "Play", y: 140, path: "/play" },
    { text: "Login", y: 210, path: "/login" },
    { text: "Settings", y: 280, path: "/builder" },
    { text: "Customize Background", y: 350, action: "openCustomize" }
];

const customizeButtons = [
    { text: "Select Image", y: 300, action: "selectImage" },
    { text: "Close", y: 350, action: "closeCustomize" }
];

const mouse = { x: 0, y: 0 };
let hoveredButton = null;

function resizeCanvas() {
    const container = document.getElementById('game-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    scaleFactor = Math.min(width / BASE_WIDTH, height / BASE_HEIGHT);
    
    canvas.width = BASE_WIDTH;
    canvas.height = BASE_HEIGHT;
    
    canvas.style.width = `${BASE_WIDTH * scaleFactor}px`;
    canvas.style.height = `${BASE_HEIGHT * scaleFactor}px`;
    
    canvas.style.position = 'absolute';
    canvas.style.left = '50%';
    canvas.style.top = '50%';
    canvas.style.transform = 'translate(-50%, -50%)';

    positions.forEach((_, index) => {
        positions[index] = { x1: 0, x2: BASE_WIDTH };
    });
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            layers[selectedLayerIndex].img = img;
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function drawMenu() {
    ctx.font = "bold 60px Arial";
    ctx.fillStyle = 'rgb(250, 183, 50)';
    ctx.textAlign = 'left';
    ctx.fillText("The Devo Trail", 45, 70);
    ctx.font = "bold 30px Arial";

    hoveredButton = null;
    menuButtons.forEach(button => {
        const textWidth = ctx.measureText(button.text).width;
        const buttonLeft = 45;
        const buttonRight = buttonLeft + textWidth;
        const buttonTop = button.y - 25;
        const buttonBottom = button.y;
        
        const isHovered = mouse.x >= buttonLeft && mouse.x <= buttonRight && 
                          mouse.y >= buttonTop && mouse.y <= buttonBottom;
        
        if (isHovered) {
            hoveredButton = button;
            ctx.fillStyle = 'rgb(255, 255, 255)';
        } else {
            ctx.fillStyle = 'rgb(250, 183, 50)';
        }
        
        ctx.fillText(button.text, buttonLeft, button.y);
    });
}

function drawCustomizePopup() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.strokeStyle = 'rgb(250, 183, 50)';
    ctx.lineWidth = 3;
    const popupWidth = 400;
    const popupHeight = 300;
    const popupX = (BASE_WIDTH - popupWidth) / 2;
    const popupY = (BASE_HEIGHT - popupHeight) / 2;
    
    ctx.fillRect(popupX, popupY, popupWidth, popupHeight);
    ctx.strokeRect(popupX, popupY, popupWidth, popupHeight);
    
    ctx.font = "bold 25px Arial";
    ctx.fillStyle = 'rgb(250, 183, 50)';
    ctx.textAlign = 'center';
    ctx.fillText("Customize Background", BASE_WIDTH / 2, popupY + 40);
    
    ctx.font = "18px Arial";
    ctx.textAlign = 'left';
    layers.forEach((layer, index) => {
        const yPos = popupY + 80 + index * 30;
        const isSelected = index === selectedLayerIndex;
        
        ctx.fillStyle = isSelected ? 'rgb(255, 255, 255)' : 'rgb(250, 183, 50)';
        
        if (isSelected) {
            ctx.fillText(">", popupX + 20, yPos);
        }
        
        ctx.fillText(layer.name, popupX + 50, yPos);
        
        const textWidth = ctx.measureText(layer.name).width;
        if (mouse.x >= popupX + 50 && mouse.x <= popupX + 50 + textWidth &&
            mouse.y >= yPos - 20 && mouse.y <= yPos) {
            ctx.fillStyle = 'rgb(255, 255, 255)';
            ctx.fillText(layer.name, popupX + 50, yPos);
        }
    });
    
    hoveredButton = null;
    customizeButtons.forEach(button => {
        ctx.font = "bold 18px Arial";
        const textWidth = ctx.measureText(button.text).width;
        const buttonLeft = (BASE_WIDTH - textWidth) / 2;
        const buttonRight = buttonLeft + textWidth;
        const buttonTop = button.y - 20;
        const buttonBottom = button.y;
        
        const isHovered = mouse.x >= buttonLeft && mouse.x <= buttonRight && 
                          mouse.y >= buttonTop && mouse.y <= buttonBottom;
        
        if (isHovered) {
            hoveredButton = button;
            ctx.fillStyle = 'rgb(255, 255, 255)';
        } else {
            ctx.fillStyle = 'rgb(250, 183, 50)';
        }
        
        ctx.fillText(button.text, buttonLeft, button.y);
    });
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (currentState === STATE.MENU) {
        layers.forEach((layer, index) => {
            const pos = positions[index];
            
            ctx.drawImage(layer.img, pos.x1, layer.y, canvas.width, canvas.height);
            ctx.drawImage(layer.img, pos.x2, layer.y, canvas.width, canvas.height);
            
            pos.x1 -= layer.speed;
            pos.x2 -= layer.speed;
            
            if (pos.x1 + canvas.width <= 0) {
                pos.x1 = canvas.width;
            }
            if (pos.x2 + canvas.width <= 0) {
                pos.x2 = canvas.width;
            }
        });
    }
    
    if (currentState === STATE.MENU) {
        drawMenu();
    } else if (currentState === STATE.CUSTOMIZE) {
        drawCustomizePopup();
    }

    requestAnimationFrame(animate);
}

function handleCanvasClick() {
    if (hoveredButton) {
        if (hoveredButton.path) {
            window.location.href = hoveredButton.path;
        } else if (hoveredButton.action === "openCustomize") {
            currentState = STATE.CUSTOMIZE;
        } else if (hoveredButton.action === "closeCustomize") {
            currentState = STATE.MENU;
        } else if (hoveredButton.action === "selectImage") {
            fileInput.click();
        }
    }
    
    if (currentState === STATE.CUSTOMIZE) {
        const popupWidth = 400;
        const popupHeight = 300;
        const popupX = (BASE_WIDTH - popupWidth) / 2;
        const popupY = (BASE_HEIGHT - popupHeight) / 2;
        
        layers.forEach((layer, index) => {
            const yPos = popupY + 80 + index * 30;
            const textWidth = ctx.measureText(layer.name).width;
            
            if (mouse.x >= popupX + 50 && mouse.x <= popupX + 50 + textWidth &&
                mouse.y >= yPos - 20 && mouse.y <= yPos) {
                selectedLayerIndex = index;
            }
        });
    }
}

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = (e.clientX - rect.left) / scaleFactor;
    mouse.y = (e.clientY - rect.top) / scaleFactor;
});

canvas.addEventListener('click', handleCanvasClick);
fileInput.addEventListener('change', handleFileUpload);

window.addEventListener('resize', resizeCanvas);
resizeCanvas();
animate();