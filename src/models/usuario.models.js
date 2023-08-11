import mongoose from "mongoose";

const UsuarioSchema=new mongoose.Schema({
    nombre:{
        type:String,
        required:true,
        trim:true,
        minlenght:4
    },
    apellidos:{
        type:String,
        required:true,
        trim:true,
        minlenght:6
    },
    edad:{
        type:Number,
        required:true
    },
    email:{
        type:String,
        required:true,
        unique:true,
        unique:true
    },
    cargo:
    {
        type:String,
        required:true
    },
    password:{
        type:String,
        required:true,
        trim:true,
        minlenght:6
    }
},{
    timestamps:true

})

const UsuarioModels = mongoose.model('Usuarios',UsuarioSchema)

module.exports = {
    UsuarioModels
} 

