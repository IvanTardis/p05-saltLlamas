const homebg = document.getElementById('layer1')

const ctx = homebg.getContext('2d')
// const img = document.getElementById('hbg')
// ctx.drawImage(img, 10, 10)

let speed = 2

const bgl1 = document.getElementById('layer-1')

const bgl2 = document.getElementById('layer-2')

const bgl3 = document.getElementById('layer-3')

const bgl4 = document.getElementById('layer-4')

const bgl5 = document.getElementById('layer-5')

const bgl6 = document.getElementById('layer-6')

let x = 0
let xS = 2400

function animate(){
    ctx.clearRect(0,0, 800, 700)
    ctx.drawImage(bgl1, x, 0)
    ctx.drawImage(bgl2, xS, 0)
    if (x < -2400) x = 2400 + xS - speed;
    else x -= speed;
    if (xS < -2400) xS = 2400 + x - speed;
    else xS -= speed;
    requestAnimationFrame(animate)

}

animate()