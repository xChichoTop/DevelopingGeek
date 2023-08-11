import usuarioModels from "../models/usuario.models.js"

export const register = async (req, res) => {
    const { nombre, apellidos, email, edad, cargo, password } = req.body
    console.log(nombre, apellidos, email, edad, cargo, password)

    try {
        const newUsuario = new usuarioModels({
            nombre,
            apellidos,
            email,
            edad,
            cargo,
            password
        })
        await newUsuario.save()
        res.status(200).send(newUsuario)
    } catch (error) {
        console.log(error)
    }
   
}

export const login = (req, res) => {
    res.send("login")
}