# Plan de ejecucion: Voice Codex para Omarchy + CachyOS

## Estado

Plan validado e implementacion MVP iniciada. Ya se instalaron skills, se creo la app Python, se configuro Handy, se anadio el binding `Alt+Z` en Hyprland y se cambio el STT por defecto a PipeWire + `whisper.cpp` al detectar que Handy no entregaba transcripciones fiables.

## Objetivo

Crear una aplicacion local que convierta el PC en un asistente de voz con Codex:

1. `Alt+Z`: empieza a escuchar.
2. `Alt+Z`: deja de escuchar.
3. PipeWire graba el microfono y `whisper.cpp` transcribe la voz.
4. Una app Python recibe el texto.
5. La app lo manda a una sesion Codex.
6. Codex actua con permisos completos por defecto.
7. La app muestra la respuesta y la lee en voz alta.

La experiencia buscada es: `Alt+Z`, hablar, `Alt+Z`, y el ordenador responde o ejecuta la tarea.

## Decisiones validadas por el usuario

- Modelo Handy por defecto: `canary-180m-flash`.
- Idioma Handy por defecto: espanol.
- Modelo Codex por defecto: `gpt 5.4 Medium`, implementado como `model = "gpt-5.4"` y `model_reasoning_effort = "medium"`.
- Permisos Codex por defecto: acceso completo al ordenador.
- Captura de pantalla: bajo criterio de la IA.
- Handy no debe traducir al ingles si no es necesario: `translate_to_english = false`.
- TTS por defecto final: Piper TTS en espanol, con fallback configurable a `espeak-ng`.
- Omarchy: la IA debe usar por defecto la skill de Omarchy para entender y modificar correctamente el sistema.
- README: debe contener toda la configuracion de instalacion, uso, riesgos y desinstalacion.
- Git: no hacer commits.

## Hallazgos locales confirmados

- Repo actual: limpio, con `README.md` vacio antes de este plan.
- Handy instalado: `/usr/bin/handy`.
- Version Handy instalada por pacman: `handy 0.8.3-2`.
- Handy soporta:
  - `handy --start-hidden`
  - `handy --toggle-transcription`
  - `handy --toggle-post-process`
  - `handy --cancel`
- Config local Handy encontrada:
  - `/home/juanma/.local/share/com.pais.handy/settings_store.json`
  - `selected_model = "canary-180m-flash"`
  - `selected_language = "es"`
  - `translate_to_english = true`
- Decision: la app dejara `translate_to_english = false` si necesita gestionar esa preferencia, porque no hace falta traducir al ingles.
- Codex instalado: `/home/juanma/.local/bin/codex`.
- Codex permite:
  - `codex exec`
  - `codex exec resume`
  - `--json`
  - `-m, --model <MODEL>`
  - `-C, --cd <DIR>`
  - `-s danger-full-access`
  - `-a never`
  - `--dangerously-bypass-approvals-and-sandbox`
  - `-i, --image <FILE>` para adjuntar imagenes.
- Hyprland instalado: `0.55.2`.
- Config correcta para atajos personales:
  - `/home/juanma/.config/hypr/bindings.conf`
- Herramientas visuales ya disponibles:
  - `grim`
  - `slurp`
  - `tesseract`
  - `wl-paste`
- No estan en PATH ahora mismo:
  - `spd-say`
- Posteriormente se instalo `espeak-ng`, y se instalo Piper TTS real en espacio de usuario porque el paquete `piper` de Arch/CachyOS corresponde a la app de configuracion de ratones.
- Se compilo `whisper.cpp` en:
  - `/home/juanma/.local/share/voice-codex/whisper.cpp`
- Modelo STT local:
  - `/home/juanma/.local/share/voice-codex/whisper.cpp/models/ggml-base.bin`
- Binario STT local:
  - `/home/juanma/.local/share/voice-codex/whisper.cpp/build/bin/whisper-cli`

## Skills localizadas

Se uso `$find-skills` y `npx skills find ...` para buscar skills de README, Linux, Arch, CachyOS y debug.

### README

Skill recomendada:

```bash
npx skills add https://github.com/github/awesome-copilot --skill create-readme -g -y
```

Motivo:

- Encaja directamente con creacion de README.
- Origen: `github/awesome-copilot`.
- Buenas senales de adopcion: alrededor de 13.5K installs por CLI y repositorio con muchas estrellas.

Alternativa:

```bash
npx skills add https://github.com/softaworks/agent-toolkit --skill crafting-effective-readmes -g -y
```

### Omarchy

Skill obligatoria ya disponible localmente:

```text
/home/juanma/.local/share/omarchy/default/omarchy-skill/SKILL.md
```

Uso por defecto:

- El perfil del asistente debe instruir a Codex para cargar y respetar la skill de Omarchy cuando la tarea toque Hyprland, Waybar, temas, atajos, capturas, terminales, ventanas, audio, configuracion de usuario u otros componentes de Omarchy.
- La app debe incluir esta politica en el prompt base de Codex.
- Regla critica: no editar `~/.local/share/omarchy/`; solo leer. Editar usuario en `~/.config/`.

### Arch Linux

Skill recomendada:

```bash
npx skills add https://github.com/github/awesome-copilot --skill arch-linux-triage -g -y
```

Motivo:

- Encaja con diagnostico Arch/CachyOS: pacman, systemd y rolling release.
- Origen confiable: `github/awesome-copilot`.
- `npx skills find arch linux` reporto alrededor de 8.6K installs.

Que es:

- `arch-linux-triage` es una skill de diagnostico para sistemas Arch Linux y derivados.
- Sirve para guiar a Codex cuando tenga que analizar problemas de paquetes, servicios, logs, kernel, actualizaciones, errores de pacman, systemd o estado general del sistema.
- No sustituye la skill de Omarchy. Omarchy queda para escritorio, Hyprland, Waybar, atajos y configuracion de usuario; Arch triage queda para la base del sistema.

### CachyOS

Skill encontrada:

```bash
npx skills add https://github.com/purplem0n/linux-assistants --skill cachyos-linux-assistant -g -y
```

Motivo:

- Especifica para CachyOS y Arch-based Linux.
- Cubre pacman, kernel CachyOS, systemd, rendimiento y administracion Linux.

Riesgo:

- Baja adopcion: alrededor de 30 installs.
- Repositorio pequeno, por lo que no tiene la misma senal social que una skill de GitHub.

Decision propuesta:

- Instalar `arch-linux-triage` como skill base.
- `cachyos-linux-assistant` queda revisada y aprobada para uso controlado.
- Complementar CachyOS con documentacion oficial y comandos locales del sistema durante la implementacion.

Revision realizada:

- Repositorio fuente revisado: `https://github.com/purplem0n/linux-assistants`.
- Commit revisado: `fb53c8f5a752ee258216939a3ae79d84371f0b82`.
- Archivos encontrados: `LICENSE`, `README.md`, `cachyos-linux-assistant/SKILL.md`.
- Licencia: MIT.
- No contiene scripts ejecutables ni automatizaciones; solo instrucciones para el agente.
- Contenido razonable: pacman, yay/paru, kernels CachyOS, systemd, logs, red, discos, rendimiento, scripts e idempotencia.
- Veredicto: aprobada para instalar, manteniendo prioridad de seguridad y contrastando hechos cambiantes con comandos locales o documentacion oficial.

### Linux admin/debug

Skills encontradas:

```bash
npx skills add https://github.com/chaterm/terminal-skills --skill system-admin -g -y
npx skills add https://github.com/mohitmishra786/low-level-dev-skills --skill linux-perf -g -y
```

Evaluacion:

- `system-admin`: util para comandos basicos de administracion, pero adopcion y estrellas modestas.
- `linux-perf`: util para rendimiento bajo nivel, `perf`, flamegraphs y diagnostico avanzado, pero no es una skill generalista de escritorio.

Decision propuesta:

- No instalarlas automaticamente en la primera pasada.
- Documentarlas como skills opcionales de diagnostico.
- Priorizar `omarchy` + `arch-linux-triage` para el MVP.

## Arquitectura propuesta

### 1. App Python

Responsabilidades:

- Ventana receptora del texto que Handy escribe.
- Estado visible:
  - idle
  - listening
  - transcribing
  - thinking
  - acting
  - speaking
  - error
- Historial de conversacion.
- Panel de configuracion.
- Logs auditables.
- IPC local para recibir eventos de `voice-codex-toggle`.
- Envio de prompts a Codex.
- Lectura TTS de respuestas.
- Broker de capturas de pantalla cuando Codex las solicite.

Stack propuesto:

- Python 3.
- GUI ligera con GTK/PyGObject si ya encaja bien con el escritorio, o PySide6 si resulta mas rapido y robusto.
- Configuracion TOML en `~/.config/voice-codex/config.toml`.

### 2. Script `voice-codex-toggle`

Ejecutado por Hyprland en `Alt+Z`.

Primera pulsacion:

- Arranca la app si no existe.
- Enfoca la ventana receptora.
- Notifica estado `listening`.
- Ejecuta `handy --toggle-transcription`.

Segunda pulsacion:

- Ejecuta `handy --toggle-transcription`.
- Notifica a la app que espere el texto final.
- La app aplica debounce y envia el texto a Codex.

### 3. STT

Valores por defecto finales:

```toml
[stt]
engine = "whisper_cpp"
fallback_engine = "handy"
record_command = "pw-record"
source = "@DEFAULT_AUDIO_SOURCE@"
whisper_executable = "/home/juanma/.local/share/voice-codex/whisper.cpp/build/bin/whisper-cli"
whisper_model = "/home/juanma/.local/share/voice-codex/whisper.cpp/models/ggml-base.bin"
language = "es"
```

Motivo del cambio:

- Handy estaba instalado y configurado correctamente, pero durante la prueba real devolvia `sample count: 0` o no generaba transcripcion util.
- El microfono si funcionaba con PipeWire/ALSA.
- `pw-record` graba WAV mono a 16 kHz correctamente.
- `whisper.cpp` permite controlar el flujo completo sin depender de que Handy pegue texto en una ventana.

### 4. Handy fallback

Valores por defecto:

```toml
[handy]
model = "canary-180m-flash"
language = "es"
toggle_command = "handy --toggle-transcription"
start_hidden_command = "handy --start-hidden"
post_process = false
translate_to_english = false
```

Notas:

- El modelo `canary-180m-flash` ya esta descargado localmente.
- Debe verificarse si cambiar `settings_store.json` directamente es estable o si Handy ofrece una API/flujo de configuracion mas seguro.
- Handy queda como fallback, no como punto unico de fallo del MVP.

### 5. Codex

Valores por defecto:

```toml
[codex]
model_label = "gpt 5.4 Medium"
model = "gpt-5.4"
model_reasoning_effort = "medium"
workdir = "/home/juanma"
full_system_access = true
sandbox = "danger-full-access"
approval_policy = "never"
bypass_approvals_and_sandbox = true
resume_strategy = "last-in-workdir"
```

Comando base propuesto:

```bash
codex exec --json \
  -m "$MODEL" \
  -C "$WORKDIR" \
  -s danger-full-access \
  -a never \
  --dangerously-bypass-approvals-and-sandbox \
  -
```

Resultado tecnico:

- Codex CLI no acepta literalmente `gpt 5.4 Medium`.
- Codex CLI si acepta `gpt-5.4`.
- La parte `Medium` se configura con `model_reasoning_effort = "medium"`.

### 5. Prompt base del asistente

La app debe generar un prompt base editable por el usuario.

Contenido por defecto:

- Actua como asistente personal del sistema de Juanma en CachyOS + Omarchy.
- Tienes permiso para actuar en todo el ordenador por defecto.
- Si el usuario pide abrir aplicaciones, navegar, cambiar configuracion, depurar o arreglar cosas, hazlo.
- Para tareas Omarchy/Hyprland/Waybar/temas/atajos/capturas, usa la skill Omarchy y respeta sus reglas.
- Para tareas Arch/CachyOS/pacman/systemd/kernel, usa la skill Arch Linux triage y, si esta instalada y revisada, la skill CachyOS.
- Si necesitas ver la pantalla para responder bien, solicita una captura o ejecuta el flujo de captura.
- No pidas confirmacion para acciones normales si el usuario ha pedido la accion de forma clara.
- Para acciones destructivas o irreversibles, registra claramente lo que se va a hacer y conserva logs.

Ejemplo que debe funcionar:

> "Abreme YouTube y ponme videos del canal Skullcar"

Codex deberia poder:

- Abrir el navegador con `omarchy-launch-browser`, `xdg-open` o mecanismo equivalente.
- Navegar a YouTube o una busqueda concreta.
- Usar herramientas GUI si se anaden en fases posteriores.

### 6. Captura de pantalla bajo criterio de la IA

Modo por defecto:

```toml
[screen]
mode = "ai_decides"
allow_fullscreen_capture = true
allow_region_capture = true
attach_images_to_codex = true
ocr_enabled = true
```

Flujo propuesto:

1. La app envia la peticion a Codex.
2. El prompt base indica a Codex que, si necesita ver la pantalla, responda con una solicitud estructurada:

```text
[[VOICE_CODEX_REQUEST_SCREENSHOT:fullscreen]]
```

3. La app captura con `grim`.
4. La app reanuda Codex adjuntando imagen:

```bash
codex exec resume --last -i "$SCREENSHOT" "$FOLLOWUP_PROMPT"
```

5. Para OCR, la app puede usar `tesseract` y adjuntar tambien el texto extraido.

Atajo de criterio:

- Si el texto del usuario contiene señales visuales claras, la app puede capturar antes de llamar a Codex.
- Ejemplos:
  - "te gusta como queda este fondo?"
  - "que ves en pantalla?"
  - "por que se ve mal esta ventana?"
  - "arregla este error que tengo abierto"

### 7. TTS

Como ahora mismo no hay motor TTS comun en PATH, se proponen dos opciones:

Opcion MVP simple:

```bash
sudo pacman -S espeak-ng
```

Opcion con mejor voz local:

```bash
sudo pacman -S piper
```

Config:

```toml
[tts]
engine = "espeak-ng"
fallback_engine = "espeak-ng"
voice = "es_ES"
rate = 165
read_codex_response = true
read_action_summary = true
```

Decision propuesta:

- Implementar interfaz TTS con backend intercambiable.
- Usar `espeak-ng` por defecto por simplicidad.
- Permitir cambiar a `piper` en cualquier momento desde config.

## Personalizacion del comportamiento

La app debe permitir modificar como actua el asistente.

Archivo:

```text
~/.config/voice-codex/config.toml
```

Opciones propuestas:

```toml
[behavior]
name = "Voice Codex"
language = "es"
tone = "directo"
autonomy = "high"
ask_before_destructive_actions = true
prefer_doing_over_explaining = true
explain_actions_after_execution = true
max_spoken_response_seconds = 90
use_omarchy_skill_by_default = true
use_arch_skill_by_default = true
use_cachyos_skill_if_installed = true

[permissions]
default = "full"
allow_shell = true
allow_gui = true
allow_file_edits = true
allow_system_config = true
allow_package_install = true
allow_browser_control = true
allow_screen_capture = "ai_decides"

[audit]
enabled = true
log_dir = "~/.local/state/voice-codex/logs"
log_prompts = true
log_codex_output = true
log_commands = true
```

## Configuracion Hyprland propuesta

Editar solo:

```text
~/.config/hypr/bindings.conf
```

Agregar:

```text
bindd = ALT, Z, Voice Codex, exec, /home/juanma/AIComputerbyAmccgil/scripts/voice-codex-toggle
```

Validar:

```bash
hyprctl reload
hyprctl configerrors
```

## Estructura de archivos propuesta

```text
.
├── README.md
├── PLAN_AI_VOICE_CODEX.md
├── pyproject.toml
├── src/
│   └── voice_codex/
│       ├── __init__.py
│       ├── app.py
│       ├── behavior.py
│       ├── codex_client.py
│       ├── config.py
│       ├── gui_control.py
│       ├── handy_bridge.py
│       ├── ipc.py
│       ├── screen_context.py
│       ├── skills.py
│       └── tts.py
├── scripts/
│   ├── voice-codex
│   ├── voice-codex-toggle
│   ├── install-hypr-binding
│   └── install-skills
├── config/
│   └── voice-codex.example.toml
├── systemd/
│   └── voice-codex.service
└── tests/
    ├── test_config.py
    ├── test_codex_client.py
    ├── test_screen_context.py
    └── test_toggle_state.py
```

## Fases de ejecucion

### Fase 1: Validacion tecnica

- Probar que Handy inserta texto en la ventana enfocada.
- Verificar que `canary-180m-flash` sigue seleccionado.
- Cambiar o documentar `translate_to_english = false` si procede.
- Probar llamada Codex con el modelo configurado.
- Resolver el id exacto de `gpt 5.4 Medium` para CLI.
- Probar captura con `grim` y adjunto con `codex exec -i`.
- Instalar o validar `espeak-ng` como motor TTS por defecto.

Criterio de aceptacion:

- Desde terminal se puede ejecutar: texto -> Codex -> respuesta hablada.

### Fase 2: Proyecto Python

- Crear `pyproject.toml`.
- Implementar config TOML.
- Implementar ventana.
- Implementar IPC.
- Implementar cliente Codex.
- Implementar prompt base con Omarchy/Arch/CachyOS.
- Implementar broker de capturas.
- Implementar TTS.

Criterio de aceptacion:

- La app recibe una frase escrita y responde por Codex con voz.

### Fase 3: Integracion Handy + `Alt+Z`

- Crear `scripts/voice-codex-toggle`.
- Crear estado runtime en `$XDG_RUNTIME_DIR/voice-codex`.
- Enfocar ventana antes de activar Handy.
- Activar/parar Handy.
- Detectar fin de transcripcion.
- Enviar texto a Codex.
- Agregar binding Hyprland.
- Validar Hyprland.

Criterio de aceptacion:

- `Alt+Z`, hablar, `Alt+Z` ejecuta el flujo completo.

### Fase 4: Acceso completo y acciones GUI

- Configurar Codex por defecto con permisos completos.
- Anadir herramientas/prompt para abrir apps, navegador y comandos de escritorio.
- Verificar ejemplo YouTube:
  - "Abreme YouTube y pon videos del canal Skullcar".
- Registrar acciones en logs.

Criterio de aceptacion:

- Codex puede ejecutar tareas reales del escritorio cuando se le piden.

### Fase 5: Captura inteligente

- Implementar solicitud estructurada de captura.
- Implementar `grim` fullscreen.
- Implementar captura de region con `slurp`.
- Adjuntar imagen a Codex con `-i`.
- Implementar OCR opcional con `tesseract`.
- Probar pregunta visual:
  - "Te gusta como queda este fondo de pantalla?"

Criterio de aceptacion:

- Si la tarea requiere vision, Codex puede pedir/capturar pantalla y responder con contexto visual.

### Fase 6: Skills y README

- Instalar skill README validada:

```bash
npx skills add https://github.com/github/awesome-copilot --skill create-readme -g -y
```

- Instalar skill Arch validada:

```bash
npx skills add https://github.com/github/awesome-copilot --skill arch-linux-triage -g -y
```

- Revisar antes de instalar:
- Instalar, tras la revision ya realizada:

```bash
npx skills add https://github.com/purplem0n/linux-assistants --skill cachyos-linux-assistant -g -y
```

- Crear README con:
  - Requisitos CachyOS/Omarchy.
  - Instalacion de Python.
  - Instalacion de TTS.
  - Configuracion Handy.
  - Configuracion Codex.
  - Permisos completos.
  - Uso con `Alt+Z`.
  - Captura de pantalla bajo criterio IA.
  - Personalizacion.
  - Logs.
  - Troubleshooting.
  - Desinstalacion.

Criterio de aceptacion:

- Una persona puede instalar y activar la app siguiendo solo el README.

### Fase 7: Verificacion final

- Ejecutar tests.
- Ejecutar formato/lint si se configura.
- Validar `hyprctl configerrors`.
- Probar flujo real.
- Revisar `git diff`.
- No hacer commit.

## Riesgos

- `gpt 5.4 Medium` puede no ser el id exacto aceptado por Codex CLI. Hay que verificarlo antes de fijarlo.
- El modo de permisos completos permite cambios amplios en el sistema. Se documenta como comportamiento por defecto porque asi lo ha pedido el usuario.
- Handy puede no escribir de forma fiable en todos los widgets. Fallback: portapapeles o lectura de su historial local.
- La skill CachyOS encontrada tiene baja adopcion. Debe revisarse antes de confiar en ella.
- Capturas de pantalla pueden incluir informacion sensible. Por defecto se permiten bajo criterio de la IA, con logs.
- Control GUI avanzado puede requerir herramientas adicionales en Wayland.

## Preguntas abiertas

1. Confirmar si autorizas instalar `arch-linux-triage` directamente en la implementacion.
2. Confirmar si autorizas instalar `cachyos-linux-assistant`, ya revisada y aprobada para uso controlado.
3. El id exacto de CLI quedo resuelto: `gpt-5.4` con `model_reasoning_effort = "medium"`.

## No se hara hasta validacion

- La validacion fue concedida por el usuario y estas tareas ya se ejecutaron parcialmente.
- No se pudo instalar software del sistema que requiere `sudo` interactivo, como `espeak-ng`.
- No se haran commits.

## Estado de implementacion MVP

- Skills instaladas:
  - `create-readme`
  - `arch-linux-triage`
  - `cachyos-linux-assistant`
  - `system-admin`
  - `linux-perf`
- App Python creada en `src/voice_codex`.
- Scripts creados en `scripts/`.
- Config ejemplo creada en `config/voice-codex.example.toml`.
- Servicio systemd de usuario preparado en `systemd/voice-codex.service`.
- README creado.
- Handy ajustado:
  - `selected_model = "canary-180m-flash"`
  - `selected_language = "es"`
  - `translate_to_english = false`
- Binding Hyprland instalado:
  - `bindd = ALT, Z, Voice Codex, exec, /home/juanma/AIComputerbyAmccgil/scripts/voice-codex-toggle`
- Validacion Hyprland:
  - `hyprctl reload`
  - `hyprctl configerrors` sin errores reportados.
- Tests unitarios:
  - `PYTHONPATH=src python -m unittest discover -s tests -v`
  - 6 tests OK.
- Modelo Codex:
  - `gpt 5.4 Medium` literal fue rechazado por Codex CLI.
  - `gpt-5.4` funciona.
  - `model_reasoning_effort = "medium"` queda aplicado por config.
- Siguiente incremento:
  - `voice-codex-doctor` para diagnostico local.
  - `voice-codex-ask` para probar Codex+TTS desde terminal.
  - Deteccion de que el paquete Arch `piper` instalado es la app de ratones, no Piper TTS.
  - Piper TTS real instalado en `~/.local/share/voice-codex/piper-tts`.
  - Voz espanola `es_ES-davefx-medium` configurada por defecto.
  - `espeak-ng` queda como fallback.
