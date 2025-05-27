const canvas = document.getElementById('layer1');
const ctx = canvas.getContext('2d');

const BASE_WIDTH = 800;
const BASE_HEIGHT = 450;
let scaleFactor = 1;

// back (bottom) to front (top)
const layers = [
    { img: document.getElementById('layer-5'), speed: 0.01/2, y: 0 },
    { img: document.getElementById('layer-4'), speed: 0.05/2, y: 0 },
    { img: document.getElementById('layer-3'), speed: 0.1/2, y: 0 },
    { img: document.getElementById('layer-6'), speed: 1.0/2, y: 0 },
];

const positions = layers.map(() => ({ x1: 0, x2: BASE_WIDTH }));

const buttons = [
    { text: "Play", y: 140, path: "/play" },
    { text: "Login", y: 210, path: "/login" },
    { text: "Settings", y: 280, path: "/builder" }
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

    layers.forEach((_, index) => {
        positions[index] = { x1: 0, x2: BASE_WIDTH };
    });
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw parallax layers
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

    ctx.font = "bold 60px Arial";
    ctx.fillStyle = 'rgb(250, 183, 50)';
    ctx.textAlign = 'left';
    ctx.fillText("The Devo Trail", 45, 70);

    ctx.font = "bold 30px Arial";


    hoveredButton = null;
    buttons.forEach(button => {
        const textWidth = ctx.measureText(button.text).width;
        const buttonLeft = 45;
        const buttonRight = buttonLeft + textWidth;
        const buttonTop = button.y - 25;
        const buttonBottom = button.y;
        
        const isHovered = mouse.x >= buttonLeft && mouse.x <= buttonRight && 
                          mouse.y >= buttonTop && mouse.y <= buttonBottom;
        
        if (isHovered) {
            hoveredButton = button;
            ctx.fillStyle = 'rgb(255, 255, 255)'; // White for hover
        } else {
            ctx.fillStyle = 'rgb(250, 183, 50)'; // Original color
        }
        
        ctx.fillText(button.text, buttonLeft, button.y);
    });

    requestAnimationFrame(animate);
}

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = (e.clientX - rect.left) / scaleFactor;
    mouse.y = (e.clientY - rect.top) / scaleFactor;
});

canvas.addEventListener('click', () => {
    if (hoveredButton) {
        window.location.href = hoveredButton.path;
    }
});

window.addEventListener('resize', resizeCanvas);
resizeCanvas();
animate();