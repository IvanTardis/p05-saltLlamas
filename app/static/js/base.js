const homebg = document.getElementById('layer1')

const ctx = homebg.getContext('2d')
// const img = document.getElementByID('hbg')
// ctx.drawImage(img, 10, 10)

let speed = 2

const bgl1 = new Image()
bgl1.src = '../images/later-1.png'

const bgl2 = new Image()
bgl2.src = '../images/layer-2.png'

const bgl3 = new Image()
bgl3.src = './images/layer-3.png'

const bgl4 = new Image()
bgl4.src = './images/layer-4.png'

const bgl5 = new Image()
bgl5.src = './images/layer-5.png'

const bgl6 = new Image()
bgl6.src = './images/layer-6.png'

function animate(){
    ctx.drawImage(bgl1, 0, 0)
    requestAnimationFrame(animate)
}

animate()