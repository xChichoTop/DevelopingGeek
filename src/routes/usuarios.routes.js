import { Router } from "express";
const { login, register } = require("../controllers/usuarios.controller.js");

const express = require('express') // <- forma que se hace en nodejs 🚩

const router =express.Router()

router.post('/register',register)
router.post('/login',login)

export default router