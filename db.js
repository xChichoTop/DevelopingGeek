import mongoose from 'mongoose'

export const connectDB = async ()=>{
    try {
        await mongoose.connect("mongodb+srv://DevelopingGeek:DevelopingGeek@developinggeek.sr4xlq6.mongodb.net/DevelopingGeek")
        console.log(">>> Base De datos esta Conectada...")
    } catch (error) {
        console.log(error)
    }
}