const homebg = document.getElementByID('layer1')

const ctx = homebg.getContext('2d')
const img = document.getElementByID('hbg')
ctx.drawImage(img, 10, 10)