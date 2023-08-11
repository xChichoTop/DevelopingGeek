const mongoose = require('mongoose')
const Schema = mongoose.Schema()

const PedidosSchema = Schema({
    name: String
})

const PedidosModels = mongoose.model("Pedidos",PedidosSchema)

module.exports = {
    PedidosModels
}

