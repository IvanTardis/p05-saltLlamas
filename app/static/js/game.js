const canvas = document.getElementById('layer1');
const ctx = canvas.getContext('2d');

const BASE_WIDTH = 800;
const BASE_HEIGHT = 450;
let scaleFactor = 1;

canvas.width = BASE_WIDTH;
canvas.height = BASE_HEIGHT;

const layers = [
    { img: document.getElementById('layer-5'), speed: 0.01/2, y: 0, name: "Background" },
    { img: document.getElementById('layer-4'), speed: 0.05/2, y: 0, name: "Midground 1" },
    { img: document.getElementById('layer-3'), speed: 0.1/2, y: 0, name: "Midground 2" },
    { img: document.getElementById('layer-6'), speed: 1.0/2, y: 0, name: "Foreground" },
]

//status message
ctx.fillRect(25, 25, 100, 100);
ctx.clearRect(45, 45, 60, 60);
ctx.strokeRect(50, 50, 50, 50);