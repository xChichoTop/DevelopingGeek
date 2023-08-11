const router = require('express').Router()
const {GetPedidos} = require('../controllers/pedidos.contoller')

router.get('/' ,GetPedidos)


router.get('/:id' ,)

module.exports  = router
