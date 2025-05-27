const canvas = document.getElementById('layer1');
const ctx = canvas.getContext('2d');

//ordered from back (bottom) to front (top)
const layers = [
    { img: document.getElementById('layer-5'), speed: 0.01/2, y: 0 },
    { img: document.getElementById('layer-4'), speed: 0.05/2, y: 0 },
    { img: document.getElementById('layer-3'), speed: 0.1/2, y: 0 },
    { img: document.getElementById('layer-6'), speed: 1.0/2, y: 0 }
];

const positions = layers.map(() => ({ x1: 0, x2: canvas.width }));

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    layers.forEach((layer, index) => {
        const pos = positions[index];
        
        ctx.drawImage(layer.img, pos.x1, layer.y);
        ctx.drawImage(layer.img, pos.x2, layer.y);
        
        pos.x1 -= layer.speed;
        pos.x2 -= layer.speed;
        
        if (pos.x1 + canvas.width <= 0) {
            pos.x1 = canvas.width;
        }
        if (pos.x2 + canvas.width <= 0) {
            pos.x2 = canvas.width;
        }
    });
    
    requestAnimationFrame(animate);
}

function resizeCanvas() {
    canvas.width = 200;
    canvas.height = 300;

    layers.forEach((_, index) => {
        positions[index] = { x1: 0, x2: canvas.width };
    });
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();
animate();