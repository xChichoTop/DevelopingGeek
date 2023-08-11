const {PedidosModels} = require("../models/pedidos.models")

async function GetPedidos(req,res){
    const id = req.params.id
    try {
        
        const result = new PedidosModels.findOne({_id: new ObjectId(id) })
        const resultt = new PedidosModels.find({})
        console.log(result)
    } catch (error) {
        console.log("*** el error es: *** \n\n"+error);
    }

}

async function GetPedidosId(req,res){
    const id = req.params.id
    try {
        
        const result = new PedidosModels.findOne({_id: new ObjectId(id) })
        console.log(result)
    } catch (error) {
        console.log("*** el error es: *** \n\n"+error);
    }

}


module.exports = {
    GetPedidos
}