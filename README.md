# Voice Codex

Voice Codex convierte un escritorio CachyOS + Omarchy en un asistente local de voz para Codex, controlado por atajo global, transcripcion local y respuesta hablada.

El flujo principal es:

```text
Alt+Z -> hablar -> Alt+Z -> Codex actua -> respuesta en voz alta
```

La aplicacion graba el microfono con PipeWire, transcribe localmente con `whisper.cpp`, envia la peticion a Codex CLI y lee la respuesta con un motor TTS configurable. Al usar `Alt+Z`, funciona en segundo plano con un indicador de notificacion para no robar foco ni cambiar de escritorio. Handy queda configurado como fallback y referencia de modelo, pero el flujo por defecto ya no depende de que Handy pegue texto en la ventana.

> [!WARNING]
> La configuracion por defecto da a Codex permisos completos sobre el ordenador (`danger-full-access`, aprobaciones desactivadas y bypass de sandbox). Es deliberado para este proyecto, pero debe usarse solo en una maquina personal donde entiendas el riesgo.

## Demo

<video src="https://raw.githubusercontent.com/amcgiluma/AIComputer/master/docs/demo/voice-codex-demo.mp4" controls width="100%" title="Voice Codex demo"></video>

[Abrir demo en GitHub](docs/demo/voice-codex-demo.mp4)

La demo muestra el flujo principal: `Alt+Z`, escucha en segundo plano, transcripcion local con `whisper.cpp`, ejecucion mediante Codex CLI, memoria persistente y respuesta hablada con Piper TTS.

## Caracteristicas

- Atajo global `Alt+Z` integrado con Hyprland/Omarchy.
- Transcripcion local con `whisper.cpp` por defecto.
- Handy preparado como fallback con modelo `canary-180m-flash`.
- Idioma por defecto: espanol.
- Sin traduccion automatica al ingles (`translate_to_english = false`).
- Codex configurable por modelo, esfuerzo de razonamiento, directorio de trabajo y permisos.
- Indicador minimalista por notificacion para `Alt+Z`.
- Memoria persistente en archivos Markdown/texto.
- Capturas de pantalla bajo criterio de la IA.
- OCR opcional con `tesseract`.
- Respuesta hablada con Piper TTS en espanol por defecto.
- Fallback a `espeak-ng` si Piper falla.
- Logs auditables en `~/.local/state/voice-codex/logs`.
- Skills instaladas para README, Omarchy, Arch Linux, CachyOS y diagnostico Linux.

## Requisitos

Sistema objetivo:

- CachyOS / Arch Linux.
- Omarchy con Hyprland.
- Python 3.11 o superior.
- Codex CLI autenticado.
- Handy instalado.

Comandos esperados en PATH:

```bash
codex
hyprctl
grim
slurp
tesseract
pw-record
```

TTS fallback:

```bash
sudo pacman -S espeak-ng
```

Piper TTS real se instala en espacio de usuario:

```text
~/.local/share/voice-codex/piper-tts
```

Whisper local se instala en espacio de usuario:

```text
~/.local/share/voice-codex/whisper.cpp
```

## Instalacion

Desde el repo:

```bash
git clone https://github.com/amcgiluma/AIComputer.git
cd AIComputer
chmod +x scripts/voice-codex scripts/voice-codex-toggle scripts/voice-codex-doctor scripts/voice-codex-ask scripts/install-hypr-binding scripts/install-skills
```

Instala las skills usadas por el asistente:

```bash
./scripts/install-skills
```

Configura el atajo de Hyprland:

```bash
./scripts/install-hypr-binding
```

Ese script agrega esta linea a `~/.config/hypr/bindings.conf` si no existe:

```text
bindd = ALT, Z, Voice Codex, exec, <repo>/scripts/voice-codex-toggle
```

Tambien ejecuta:

```bash
hyprctl reload
hyprctl configerrors
```

## Uso

Arranca el asistente en segundo plano:

```bash
./scripts/voice-codex
```

Por defecto no muestra ventana. Para usar la ventana GTK de depuracion/escritura, cambia temporalmente `ui.show_window_on_start = true` en `~/.config/voice-codex/config.toml` y reinicia el proceso.

Comprueba el entorno:

```bash
./scripts/voice-codex-doctor
```

Prueba Codex + TTS sin Handy ni ventana:

```bash
./scripts/voice-codex-ask "Di una frase corta confirmando que funcionas"
```

Uso normal:

1. Pulsa `Alt+Z`.
2. Habla.
3. Pulsa `Alt+Z` de nuevo.
4. Voice Codex transcribe la grabacion con `whisper.cpp`.
5. Codex recibe la peticion, actua y responde.
6. La app lee la respuesta con Piper TTS en espanol.

Si activas la ventana GTK de depuracion, tambien puedes escribir directamente y pulsar `Enviar a Codex`.

`Alt+Z` no abre la ventana grande. Si la app no estaba viva, el atajo la arranca oculta y muestra una notificacion breve.

## Configuracion

La primera ejecucion crea:

```text
~/.config/voice-codex/config.toml
```

Ejemplo base:

```toml
[codex]
model_label = "gpt 5.4 Medium"
model = "gpt-5.4"
model_reasoning_effort = "medium"
workdir = "~"
sandbox = "danger-full-access"
approval_policy = "never"
bypass_approvals_and_sandbox = true

[handy]
model = "canary-180m-flash"
language = "es"
translate_to_english = false
transcription_settle_ms = 1800

[stt]
engine = "whisper_cpp"
fallback_engine = "handy"
record_command = "pw-record"
source = "@DEFAULT_AUDIO_SOURCE@"
whisper_executable = "~/.local/share/voice-codex/whisper.cpp/build/bin/whisper-cli"
whisper_model = "~/.local/share/voice-codex/whisper.cpp/models/ggml-base.bin"
language = "es"
normalize_audio = true
ffmpeg_executable = "ffmpeg"
audio_filter = "highpass=f=90,lowpass=f=7600,afftdn=nf=-25,dynaudnorm=f=150:g=15:p=0.95"
suppress_non_speech_tokens = true
initial_prompt = "Transcribe solamente voz hablada en espanol."
vad_enabled = true
vad_model = "~/.local/share/voice-codex/whisper.cpp/models/ggml-silero-v6.2.0.bin"
vad_threshold = 0.35

[tts]
engine = "piper"
fallback_engine = "espeak-ng"
voice = "es"
rate = 165
piper_executable = "~/.local/share/voice-codex/piper-tts/bin/piper/piper"
piper_model = "~/.local/share/voice-codex/piper-tts/voices/es_ES-davefx-medium.onnx"
piper_length_scale = 1.0

[screen]
mode = "ai_decides"
ocr_enabled = true

[memory]
enabled = true
dir = "~/.codex/memories/voice-codex"
max_bytes = 20000

[ui]
auto_focus_on_record = false
show_window_on_start = false
indicator = "notification"
notification_icon = "assistant"
notification_timeout_ms = 1800
```

> [!IMPORTANT]
> `gpt 5.4 Medium` queda representado como `model = "gpt-5.4"` y `model_reasoning_effort = "medium"`, que es el formato aceptado por Codex CLI en este sistema.

### Donde tocar modelos, voz y UI

- Modelo Codex: seccion `[codex]`, claves `model` y `model_reasoning_effort`.
- Transcriptor principal: seccion `[stt]`, claves `engine`, `whisper_executable`, `whisper_model`, `language`, `vad_enabled` y `vad_threshold`.
- Handy fallback: seccion `[handy]`, clave `model`.
- Voz hablada: seccion `[tts]`, claves `engine`, `piper_executable`, `piper_model`, `voice`, `rate` y `piper_length_scale`.
- Comportamiento de `Alt+Z`: seccion `[ui]`, especialmente `auto_focus_on_record`, `indicator` y `notification_icon`.

### Memoria persistente

Voice Codex lee memoria desde:

```text
~/.codex/memories/voice-codex
```

Estructura creada:

```text
preferences/
projects/
system/
voice/
notes/
```

Guarda ahi archivos `.md` o `.txt`. Se cargan en cada peticion hasta `memory.max_bytes`. El `README.md` de esa carpeta es solo guia y no entra en el prompt.

## Capturas de pantalla

Voice Codex no captura pantalla de forma continua.

La captura se dispara en dos casos:

- La peticion contiene pistas visuales, por ejemplo: "te gusta este fondo?", "que ves en pantalla?", "por que se ve mal esta ventana?".
- Codex solicita una captura con el marcador interno:

```text
[[VOICE_CODEX_REQUEST_SCREENSHOT:fullscreen]]
```

Las capturas se guardan en:

```text
~/.local/state/voice-codex/screenshots
```

## Skills

Instaladas por `scripts/install-skills`:

- `create-readme`: estructura y calidad del README.
- `arch-linux-triage`: diagnostico Arch Linux, `pacman`, `systemd`, logs y kernel.
- `cachyos-linux-assistant`: contexto CachyOS, kernels y repos.
- `system-admin`: administracion Linux general.
- `linux-perf`: diagnostico avanzado de rendimiento.

Omarchy esta disponible localmente y se usa como criterio base para escritorio, Hyprland, Waybar, atajos, capturas y configuracion de usuario.

## Logs

Los logs quedan en:

```text
~/.local/state/voice-codex/logs/voice-codex.log
```

Incluyen estados, prompts enviados, comandos Codex y respuestas finales.

## Desarrollo

Ejecutar pruebas:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Compilar modulos:

```bash
python -m compileall src
```

## Licencia

Este proyecto se distribuye bajo la licencia [Apache License 2.0](LICENSE).

## Solucion de problemas

### No se oye la respuesta

Instala `espeak-ng`:

```bash
sudo pacman -S espeak-ng
```

Prueba directa:

```bash
espeak-ng -v es "Voice Codex listo"
```

### Piper TTS

Voice Codex usa por defecto el binario oficial de Rhasspy/Piper y la voz espanola `es_ES-davefx-medium`:

```toml
[tts]
engine = "piper"
piper_executable = "~/.local/share/voice-codex/piper-tts/bin/piper/piper"
piper_model = "~/.local/share/voice-codex/piper-tts/voices/es_ES-davefx-medium.onnx"
```

> [!NOTE]
> En Arch/CachyOS, el paquete `piper` de repos es la app GTK para configurar ratones gaming, no Piper TTS. `voice-codex-doctor` detecta el Piper TTS real configurado por ruta.

### `Alt+Z` no hace nada

Comprueba que el binding existe:

```bash
rg "Voice Codex|ALT, Z" ~/.config/hypr/bindings.conf
```

Valida Hyprland:

```bash
hyprctl reload
hyprctl configerrors
```

### Handy escribe en otra ventana

El flujo por defecto ya no depende de que Handy escriba en la ventana. Si quieres volver a Handy como backend principal, cambia:

```toml
[stt]
engine = "handy"
```

Despues arranca Voice Codex y pulsa dentro del cuadro de texto antes de usar `Alt+Z`. Si necesitas que el atajo enfoque la ventana como antes, cambia `ui.auto_focus_on_record = true`.

### No hay transcripcion

Comprueba que PipeWire puede grabar:

```bash
timeout 2s pw-record --target @DEFAULT_AUDIO_SOURCE@ --rate 16000 --channels 1 --format s16 /tmp/voice-codex-test.wav
file /tmp/voice-codex-test.wav
```

Comprueba Whisper:

```bash
~/.local/share/voice-codex/whisper.cpp/build/bin/whisper-cli \
  -m ~/.local/share/voice-codex/whisper.cpp/models/ggml-base.bin \
  -f /tmp/voice-codex-test.wav \
  -l es -nt -np
```

### Codex falla por modelo

Edita:

```text
~/.config/voice-codex/config.toml
```

y ajusta:

```toml
[codex]
model = "gpt-5.5"
model_reasoning_effort = "high"
```

Tambien puedes borrar la linea `model` para dejar que Codex use su modelo por defecto local.

## Desinstalacion

Quita el binding de `~/.config/hypr/bindings.conf`:

```text
bindd = ALT, Z, Voice Codex, exec, <repo>/scripts/voice-codex-toggle
```

Recarga Hyprland:

```bash
hyprctl reload
hyprctl configerrors
```

Opcionalmente borra configuracion y estado:

```bash
rm -rf ~/.config/voice-codex ~/.local/state/voice-codex
```
