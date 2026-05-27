# Publicacion LinkedIn: convertir mi PC en un asistente de voz con Codex

## Contexto personal

Estoy construyendo una aplicacion para mi propio ordenador: un PC con CachyOS y Omarchy.

La idea es simple de explicar, pero potente:

> Pulsar `Alt+Z`, hablarle al ordenador, volver a pulsar `Alt+Z`, y que Codex entienda la tarea, actue en el sistema y me responda en voz alta.

No quiero un chatbot separado de mi maquina. Quiero un asistente integrado en el escritorio, capaz de ver el contexto cuando lo necesita, usar herramientas del sistema y ayudarme a resolver tareas reales.

## Lo que hicimos hasta ahora

### 1. Definimos la experiencia de usuario

El flujo base sera:

1. Pulso `Alt+Z`.
2. Hablo.
3. Pulso `Alt+Z` otra vez.
4. Handy transcribe mi voz.
5. Una app Python recibe el texto.
6. Codex procesa la peticion.
7. El ordenador responde en voz alta.

Ejemplo de uso esperado:

> "Abreme YouTube y pon videos del canal Skullcar."

El objetivo no es que la IA diga como hacerlo, sino que lo haga.

### 2. Revisamos el sistema real

Antes de escribir codigo, comprobamos el entorno:

- El repo Git estaba limpio.
- Handy estaba instalado en `/usr/bin/handy`.
- Codex estaba instalado en `/home/juanma/.local/bin/codex`.
- Hyprland estaba instalado en version `0.55.2`.
- Omarchy usa `~/.config/hypr/bindings.conf` para atajos personalizados.
- Ya estaban disponibles herramientas utiles:
  - `grim` para capturas.
  - `slurp` para seleccionar regiones.
  - `tesseract` para OCR.
  - `wl-paste` para Wayland.

Tambien vimos que no estaban instalados todavia motores TTS comunes como `espeak-ng`, `spd-say` o `piper`.

### 3. Elegimos Handy como motor de voz

Handy ya estaba configurado con:

- Modelo: `canary-180m-flash`.
- Idioma: espanol.

Este modelo es rapido, local y admite espanol, asi que sera el valor por defecto.

Tambien detectamos que Handy tenia `translate_to_english = true`. Como no hace falta traducir si vamos a trabajar naturalmente en espanol, decidimos que la app no usara traduccion al ingles por defecto.

### 4. Definimos Codex como cerebro del sistema

La app hablara con Codex usando la CLI.

Configuracion deseada:

- Modelo por defecto: `gpt 5.4 Medium`, implementado en CLI como `gpt-5.4` con razonamiento `medium`.
- Directorio de trabajo: `/home/juanma`.
- Permisos por defecto: acceso completo al ordenador.
- Sandbox: `danger-full-access`.
- Politica de aprobacion: `never`.

Esto es deliberadamente potente. El asistente no esta pensado como demo limitada, sino como una herramienta personal con capacidad real de operar sobre mi sistema.

### 5. Decidimos que la IA pueda usar capturas bajo criterio propio

La IA no deberia capturar pantalla todo el tiempo.

Pero si la tarea lo necesita, debe poder hacerlo.

Ejemplo:

> "Te gusta como queda este fondo de pantalla?"

En ese caso, la IA necesita ver la pantalla. El plan es que pueda pedir o lanzar una captura con `grim`, adjuntarla a Codex y responder con contexto visual.

### 6. Priorizamos Omarchy

Como el sistema usa Omarchy, el asistente debe entender sus reglas:

- No editar `~/.local/share/omarchy/`.
- Leer esa ruta si hace falta para entender defaults.
- Editar configuracion de usuario en `~/.config/`.
- Validar Hyprland con:

```bash
hyprctl reload
hyprctl configerrors
```

La skill de Omarchy sera parte del criterio base del asistente cuando toque escritorio, Hyprland, Waybar, temas, atajos, capturas o configuracion visual.

### 7. Buscamos skills para README, Arch, CachyOS y Linux

Use la skill `$find-skills` para localizar skills utiles.

Para README, la mejor candidata fue:

```bash
npx skills add https://github.com/github/awesome-copilot --skill create-readme -g -y
```

Para Arch Linux, encontramos:

```bash
npx skills add https://github.com/github/awesome-copilot --skill arch-linux-triage -g -y
```

Esta skill sirve para guiar diagnosticos de Arch y derivados: pacman, systemd, logs, kernels, errores de actualizacion y problemas de base del sistema.

Para CachyOS encontramos:

```bash
npx skills add https://github.com/purplem0n/linux-assistants --skill cachyos-linux-assistant -g -y
```

La revisamos antes de aprobarla porque tenia baja adopcion. El repositorio era pequeno y limpio:

- `LICENSE`
- `README.md`
- `cachyos-linux-assistant/SKILL.md`

No contiene scripts ejecutables ni automatizaciones ocultas. Es una guia de criterio para tareas de CachyOS/Arch: pacman, yay/paru, kernels CachyOS, systemd, logs, red, discos, rendimiento y scripting seguro.

Veredicto: aprobada para uso controlado.

### 8. Elegimos TTS

Por defecto usaremos:

```bash
espeak-ng
```

Motivo: simple, rapido y suficiente para el MVP.

Pero la app quedara preparada para cambiar a:

```bash
piper
```

cuando quiera una voz local de mas calidad.

## Arquitectura que vamos a construir

La app tendra estos componentes:

- Una ventana Python que recibe el texto de Handy.
- Un script `voice-codex-toggle` conectado a `Alt+Z`.
- Un cliente para Codex CLI.
- Un modulo TTS.
- Un modulo de capturas/OCR.
- Un archivo de configuracion en `~/.config/voice-codex/config.toml`.
- Logs auditables en `~/.local/state/voice-codex/logs`.

El atajo de Hyprland sera:

```text
bindd = ALT, Z, Voice Codex, exec, /home/juanma/AIComputerbyAmccgil/scripts/voice-codex-toggle
```

## Por que me parece interesante

Porque cambia la relacion con el ordenador.

No es "abrir una app de IA".

Es hablar con tu propio sistema operativo:

- Que pueda entender donde esta.
- Que conozca Omarchy.
- Que sepa que esta en CachyOS.
- Que pueda mirar la pantalla si lo necesita.
- Que pueda abrir aplicaciones.
- Que pueda depurar problemas.
- Que pueda modificar archivos.
- Que pueda responder en voz alta.

Es mas cercano a tener un operador local de tu ordenador que a tener un chatbot.

## Riesgos asumidos

Hay riesgos reales:

- Dar permisos completos a una IA no es trivial.
- Las capturas de pantalla pueden contener informacion sensible.
- Las acciones sobre el sistema pueden romper cosas si se hacen mal.
- Hay que auditar lo que se ejecuta.

Por eso el plan incluye:

- Logs.
- Configuracion explicita.
- Separacion entre tareas Omarchy, Arch y CachyOS.
- Validacion de Hyprland.
- README completo.
- Sin commits automaticos.

## Borrador de post para LinkedIn

Estoy construyendo algo bastante personal: un asistente de voz para mi propio PC con CachyOS + Omarchy.

La idea es que el ordenador funcione asi:

`Alt+Z` -> hablo -> `Alt+Z` -> Codex entiende, actua y responde en voz alta.

No quiero un chatbot aislado. Quiero una IA integrada en el escritorio, con contexto real del sistema, capaz de abrir aplicaciones, revisar configuraciones, depurar problemas, mirar la pantalla cuando haga falta y ayudarme a operar el ordenador de verdad.

El flujo que estoy disenando usa:

- Handy para transcribir voz localmente.
- `canary-180m-flash` como modelo de voz por defecto en espanol.
- Codex como motor de razonamiento y ejecucion.
- Omarchy/Hyprland para el atajo `Alt+Z`.
- `grim`, `slurp` y `tesseract` para contexto visual y OCR.
- `espeak-ng` como TTS inicial, con opcion de pasar a `piper`.

Una parte importante del proceso ha sido no empezar escribiendo codigo a ciegas. Primero revise el sistema real:

- donde vive Handy,
- como esta configurado,
- que acepta Codex por CLI,
- donde se deben tocar los bindings de Hyprland,
- que herramientas ya tiene el sistema,
- que skills pueden ayudar a Codex a entender Arch, CachyOS y Omarchy.

Tambien revise una skill especifica de CachyOS antes de aprobarla. Tenia poca adopcion, asi que mire el repositorio: solo contiene README, licencia MIT y un `SKILL.md`. No trae scripts ni automatizaciones ocultas. Es una guia de criterio para pacman, kernels CachyOS, systemd, logs y diagnostico. Con esa revision, me parece razonable usarla de forma controlada.

Lo potente de esto es que no estoy creando "otra interfaz de chat". Estoy intentando que la IA sea una capa operativa encima de mi propio ordenador.

Ejemplo:

> "Abreme YouTube y pon videos del canal Skullcar."

O:

> "Te gusta como queda este fondo de pantalla?"

En el segundo caso, la IA deberia entender que necesita ver la pantalla, hacer una captura y responder con criterio visual.

Obviamente esto tiene riesgos. Dar permisos completos a una IA no se puede tratar como una demo inocente. Por eso la app tendra configuracion explicita, logs, README completo, reglas especificas para Omarchy y una separacion clara entre acciones de escritorio, sistema y diagnostico.

Me interesa mucho esta direccion: IA no como una pagina web mas, sino como una herramienta local que entiende tu maquina y trabaja contigo sobre ella.

Siguiente paso: probar el flujo real con voz y ajustar los puntos finos.

## Actualizacion: MVP implementado

Despues del plan inicial, ya deje construida la primera version funcional:

- App Python con ventana GTK.
- Socket Unix local para comunicar el atajo con la app.
- Script `voice-codex-toggle` para `Alt+Z`.
- Integracion inicial con Handy y fallback de lectura de su historial local.
- Cambio posterior a PipeWire + `whisper.cpp` como STT por defecto, porque Handy no estaba entregando transcripciones fiables en esta maquina.
- Cliente Codex por CLI.
- Captura de pantalla automatica cuando la peticion parece visual.
- TTS con Piper en espanol por defecto y fallback a `espeak-ng`.
- Logs auditables.
- README completo.
- Binding Hyprland instalado y validado.
- Handy configurado para no traducir al ingles.
- Tests unitarios pasando.
- Script de diagnostico (`voice-codex-doctor`).
- Prueba por terminal (`voice-codex-ask`) para validar Codex + voz sin depender aun de Handy.
- Deteccion de un detalle tipico de Linux: el paquete `piper` instalado en Arch/CachyOS puede ser la app para ratones gaming, no Piper TTS.
- Instalacion local de Piper TTS real con voz espanola `es_ES-davefx-medium`.
- Compilacion local de `whisper.cpp` y descarga del modelo `ggml-base.bin` en espacio de usuario, sin `sudo`.
- Diagnostico de microfono con PipeWire/ALSA: el micro funcionaba; el bloqueo estaba en el flujo de Handy.
- Filtro para evitar que Whisper mande a Codex falsos positivos como `[Musica]` cuando solo hay ruido ambiente.

Lo interesante del proceso es que no fue solo "hacer una app". Fue ir conectando capas del sistema:

- voz,
- ventana,
- atajo global,
- compositor Wayland,
- modelo de IA,
- permisos del sistema,
- capturas,
- skills,
- documentacion.

Ese es justo el punto que me interesa: IA integrada en el ordenador real, no aislada en una caja de texto.

Tambien me gusta que el proyecto haya tenido una decision muy de sistema real: el plan inicial era Handy, pero al probarlo vimos que se quedaba en "sin transcripcion". En vez de forzar una idea que no funcionaba, comprobamos microfono, PipeWire, ALSA y CPAL, y cambiamos el backend a una ruta mas controlable:

```text
Alt+Z -> pw-record -> whisper.cpp -> Codex -> Piper TTS
```

Handy no desaparece: queda configurado con `canary-180m-flash`, espanol y sin traduccion al ingles, pero ya no es el punto unico de fallo.

## Version corta

Estoy construyendo un asistente de voz local para mi PC con CachyOS + Omarchy.

La experiencia sera:

`Alt+Z` -> hablar -> `Alt+Z` -> Codex actua en el sistema y responde en voz alta.

Usa PipeWire + `whisper.cpp` para transcripcion local, Codex para razonar y ejecutar, Omarchy/Hyprland para integrarse con el escritorio, capturas bajo criterio de la IA cuando necesite ver la pantalla, y Piper TTS en espanol para contestar.

No quiero otro chatbot. Quiero una capa operativa sobre mi propio ordenador.

Ahora toca probar el flujo real con voz, escuchar los fallos y pulirlo sobre uso diario.
