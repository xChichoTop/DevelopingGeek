$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-Location -LiteralPath $PSScriptRoot
$utf8 = New-Object System.Text.UTF8Encoding($false)
$runId = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,6)
$ev = Join-Path $PSScriptRoot ('evidencias\docker-' + $runId)
New-Item -ItemType Directory -Path $ev -Force | Out-Null

function Invoke-DockerChecked {
    param([string[]]$Arguments, [string]$FileName)
    Write-Host ('docker ' + ($Arguments -join ' ')) -ForegroundColor Cyan
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $lines = & docker @Arguments 2>&1
        $resultCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previous
    }
    $resultText = ($lines | ForEach-Object { $_.ToString() }) -join "`n"
    [System.IO.File]::WriteAllText((Join-Path $ev $FileName), $resultText, $utf8)
    if ($resultCode -ne 0) { throw ('Fallo en docker ' + ($Arguments -join ' ') + '. Consulta ' + $FileName) }
    return $resultText
}

try {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw 'Docker no esta instalado. Instala Docker Desktop, abrelo y vuelve a ejecutar este archivo.'
    }
    $null = Invoke-DockerChecked -Arguments @('info') -FileName 'docker_info.txt'
    $null = Invoke-DockerChecked -Arguments @('compose','version') -FileName 'compose_version.txt'
    $null = Invoke-DockerChecked -Arguments @('compose','config','--quiet') -FileName 'configuracion.txt'
    $null = Invoke-DockerChecked -Arguments @('compose','up','--build','-d','--wait','--wait-timeout','180') -FileName 'construccion.txt'
    $beforeText = Invoke-DockerChecked -Arguments @('compose','ps','-q') -FileName 'ids_antes.txt'
    $beforeIds = @($beforeText -split '\r?\n' | Where-Object { $_ -match '^[0-9a-f]{64}$' })
    if ($beforeIds.Count -ne 2) { throw 'Se esperaban exactamente dos contenedores del proyecto.' }
    $inspectText = Invoke-DockerChecked -Arguments (@('inspect') + $beforeIds) -FileName 'contenedores_antes.json'
    $containers = @($inspectText | ConvertFrom-Json)
    $web = @($containers | Where-Object { $_.Config.Labels.'com.docker.compose.service' -eq 'web' })
    $datos = @($containers | Where-Object { $_.Config.Labels.'com.docker.compose.service' -eq 'datos' })
    if ($web.Count -ne 1 -or $datos.Count -ne 1) { throw 'Los servicios deben ser web y datos.' }
    if ($web[0].State.Health.Status -ne 'healthy' -or $datos[0].State.Health.Status -ne 'healthy') {
        throw 'Los dos contenedores deben estar saludables.'
    }
    $webNetworks = @($web[0].NetworkSettings.Networks.PSObject.Properties.Name)
    $dataNetworks = @($datos[0].NetworkSettings.Networks.PSObject.Properties.Name)
    $commonNetworks = @($webNetworks | Where-Object { $dataNetworks -contains $_ })
    if ($commonNetworks.Count -lt 1) { throw 'Los contenedores no comparten una red.' }
    $volume = @($datos[0].Mounts | Where-Object { $_.Type -eq 'volume' -and $_.Destination -eq '/data' })
    if ($volume.Count -ne 1) { throw 'No se encontro el volumen de datos de Redis.' }
    $null = Invoke-DockerChecked -Arguments @('compose','ps') -FileName 'estado_antes.txt'
    $testsText = Invoke-DockerChecked -Arguments @('compose','exec','-T','web','python','comprobar.py') -FileName 'pruebas.json'
    $tests = $testsText | ConvertFrom-Json
    if ($tests.total -ne 9 -or @($tests.pruebas).Count -ne 9 -or @($tests.pruebas | Where-Object { $_.resultado -ne 'APROBADA' }).Count -ne 0) {
        throw 'Las nueve pruebas de comunicacion y funcionamiento deben aprobarse.'
    }
    $seed = "from app import db; db.hset('tareas', 'verificacion_entrega', 'Entrega 1 Johan Alvarez Parra'); print(db.hget('tareas', 'verificacion_entrega'))"
    $null = Invoke-DockerChecked -Arguments @('compose','exec','-T','web','python','-c',$seed) -FileName 'tarea_creada_desde_web.txt'
    $direct = Invoke-DockerChecked -Arguments @('compose','exec','-T','datos','redis-cli','HGET','tareas','verificacion_entrega') -FileName 'lectura_directa_redis_antes.txt'
    if ($direct.Trim() -ne 'Entrega 1 Johan Alvarez Parra') { throw 'La lectura directa en Redis no coincide con la escritura desde web.' }
    $null = Invoke-DockerChecked -Arguments @('compose','down') -FileName 'detencion.txt'
    $null = Invoke-DockerChecked -Arguments @('compose','up','-d','--wait','--wait-timeout','180') -FileName 'recreacion.txt'
    $afterText = Invoke-DockerChecked -Arguments @('compose','ps','-q') -FileName 'ids_despues.txt'
    $afterIds = @($afterText -split '\r?\n' | Where-Object { $_ -match '^[0-9a-f]{64}$' })
    if ($afterIds.Count -ne 2) { throw 'No se recrearon los dos contenedores.' }
    if (@($afterIds | Where-Object { $beforeIds -contains $_ }).Count -ne 0) { throw 'Los contenedores no fueron recreados.' }
    $afterInspect = Invoke-DockerChecked -Arguments (@('inspect') + $afterIds) -FileName 'contenedores_despues.json'
    $afterContainers = @($afterInspect | ConvertFrom-Json)
    if (@($afterContainers | Where-Object { $_.State.Health.Status -ne 'healthy' }).Count -ne 0) { throw 'Los contenedores recreados no estan saludables.' }
    $directAfter = Invoke-DockerChecked -Arguments @('compose','exec','-T','datos','redis-cli','HGET','tareas','verificacion_entrega') -FileName 'lectura_directa_redis_despues.txt'
    if ($directAfter.Trim() -ne 'Entrega 1 Johan Alvarez Parra') { throw 'No se conservo el registro en el volumen.' }
    $finalCheck = "from app import db; assert db.hget('tareas', 'verificacion_entrega') == 'Entrega 1 Johan Alvarez Parra'; print('APROBADA: persistencia y comunicacion despues de recrear contenedores')"
    $null = Invoke-DockerChecked -Arguments @('compose','exec','-T','web','python','-c',$finalCheck) -FileName 'persistencia.txt'
    $null = Invoke-DockerChecked -Arguments @('compose','ps') -FileName 'estado_final.txt'
    $null = Invoke-DockerChecked -Arguments @('compose','logs','--no-color') -FileName 'registros.txt'
    $proof = [ordered]@{
        estado = 'APROBADA'; fecha = (Get-Date).ToString('o'); autor = 'Johan Alvarez Parra'; docente = 'Edwar Reyes'
        entorno = 'Docker real en el equipo de ejecucion'; numero_contenedores = 2
        servicios = @('web','datos'); red_compartida = $commonNetworks; volumen = $volume[0].Name
        pruebas_aprobadas = 9; lectura_directa_redis_coincide = $true; contenedores_recreados = $true; persistencia_aprobada = $true
        ids_antes = $beforeIds; ids_despues = $afterIds
        repositorio = 'https://github.com/xChichoTop/DevelopingGeek/tree/entrega-1-semana-3/entrega-1-semana-3'
        archivos_sha256 = @('app.py','Dockerfile','compose.yaml','requirements.txt','comprobar.py') | ForEach-Object {
            [ordered]@{ archivo = $_; sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_).Hash }
        }
    }
    [System.IO.File]::WriteAllText((Join-Path $ev 'resultado_docker.json'), ($proof | ConvertTo-Json -Depth 8), $utf8)
    $destination = Join-Path $PSScriptRoot ('entrega_para_subir\' + $runId)
    $package = Join-Path $destination 'contenido'
    $code = Join-Path $package 'codigo'
    New-Item -ItemType Directory -Path $code -Force | Out-Null
    foreach ($item in Get-ChildItem -LiteralPath $PSScriptRoot -Force) {
        if ($item.Name -in @('.git','__pycache__','entrega_para_subir','informe','evidencias','EMPIEZA_AQUI.txt','PASO_A_PASO_ENTREGA.txt')) { continue }
        if ($item.Extension -eq '.zip') { continue }
        Copy-Item -LiteralPath $item.FullName -Destination $code -Recurse -Force
    }
    $localEvidence = Join-Path $code 'evidencias'
    New-Item -ItemType Directory -Path $localEvidence -Force | Out-Null
    foreach ($name in @('LEEME.md','interfaz_ejecucion_local.png','salud_ejecucion_local.png','pruebas_http_redis_real.json','datos_redis_real.json','persistencia_redis_real.json')) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('evidencias\' + $name)) -Destination $localEvidence
    }
    Copy-Item -LiteralPath $ev -Destination (Join-Path $package 'evidencias_docker') -Recurse
    foreach ($name in @('Informe_Entrega_1_Semana_3.pdf','Informe_Entrega_1_Semana_3.docx')) {
        $reportSource = Join-Path $PSScriptRoot ('informe\' + $name)
        if (-not (Test-Path -LiteralPath $reportSource)) { $reportSource = Join-Path (Split-Path $PSScriptRoot -Parent) $name }
        Copy-Item -LiteralPath $reportSource -Destination $package
    }
    $note = "ENTREGA 1 - SEMANA 3`r`nJohan Alvarez Parra`r`nProfesor: Edwar Reyes`r`n`r`nContiene el informe, el codigo y evidencias reales de Docker aprobadas.`r`nEl informe separa las pruebas locales de este anexo de contenedores.`r`nRepositorio: " + $proof.repositorio
    [System.IO.File]::WriteAllText((Join-Path $package 'LEEME_ENTREGA.txt'), $note, $utf8)
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = Join-Path $destination 'Entrega_1_Semana_3_Johan_Alvarez_Parra.zip'
    [System.IO.Compression.ZipFile]::CreateFromDirectory($package, $archive)
    Write-Host ''
    Write-Host 'VALIDACION DOCKER APROBADA' -ForegroundColor Green
    Write-Host 'El ZIP para subir al aula esta en:' -ForegroundColor Green
    Write-Host $archive
    Write-Host 'Comprueba el contenido del archivo ZIP antes de entregarlo.'
    Start-Process explorer.exe -ArgumentList ('"' + $destination + '"')
    exit 0
} catch {
    [System.IO.File]::WriteAllText((Join-Path $ev 'ERROR.txt'), $_.ToString(), $utf8)
    Write-Host ('NO SE GENERO UNA ENTREGA APROBADA: ' + $_.ToString()) -ForegroundColor Red
    Write-Host ('Revisa: ' + $ev)
    Write-Host 'Consulta el registro ERROR.txt antes de repetir la comprobacion.'
    exit 1
}
