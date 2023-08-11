import  express  from "express";
import morgan from "morgan";
import usuariosRoutes from "./src/routes/usuarios.routes.js";

const app=express()

app.use(morgan('dev'))
app.use(express.json())
app.use('/api',usuariosRoutes)
export default app