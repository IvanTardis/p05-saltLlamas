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

function animate(){
    console.log(bgl1.src)
    ctx.drawImage(bgl1, 0, 0)
    requestAnimationFrame(animate)

}

animate()