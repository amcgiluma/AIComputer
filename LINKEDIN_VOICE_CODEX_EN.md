# LinkedIn Post: Building a Local Voice Assistant for My Linux PC

## Post Draft

I have been building a personal project that feels much closer to the future I want from AI on desktop systems: a local voice assistant for my own Linux laptop.

The idea is simple:

`Alt+Z` -> I speak -> `Alt+Z` -> the computer understands the task, acts on the system, and answers back out loud.

This is not a chatbot living in a browser tab. It is an assistant integrated into the operating system itself.

The stack behind it is:

- `whisper.cpp` for local speech-to-text
- Codex CLI for reasoning and system actions
- Piper TTS for spoken replies
- CachyOS + Omarchy/Hyprland for desktop integration

What I find most interesting is not just the voice interface, but the idea of AI as an operational layer on top of a real machine:

- opening apps
- navigating the system
- checking configuration
- helping my family use the laptop more easily
- helping me explore Linux while I keep learning it

Coming from a long Windows background, Linux changed the way I think about computers because it gave me real control over the system. Once I moved to CachyOS and Omarchy, building an assistant that could work *with* that system started to feel like a very natural next step.

Right now, the project already supports a real flow:

`Alt+Z` -> record with PipeWire -> transcribe locally -> send to Codex -> act -> respond with voice

I am especially interested in this direction: AI not as another website, but as a tool that understands your machine and helps you operate it.

#Linux #AI #OpenAI #Codex #Python #Hyprland #VoiceAssistant #CachyOS #Omarchy

## Suggested Visuals

### Screenshots I would include

1. The desktop itself with the assistant in use.
   A clean Omarchy desktop shot where the project feels real and integrated, not theoretical.

2. A terminal or app view showing the real flow.
   For example: `Alt+Z`, transcription, Codex action, spoken response, or a visible project log.

3. The project structure or README.
   A screenshot that shows this is an actual engineered system, not just an idea.

4. The voice-codex config file.
   A cropped shot of the model, STT and TTS sections can help technical people understand the setup quickly.

5. The demo GIF/video preview frame.
   Use one frame that clearly shows the assistant responding to a real request.

### Photos or images I would include

1. A photo of the laptop running the setup.
   Preferably a sharp, real-world shot instead of a stock-like image.

2. A close shot of the desktop while the assistant is active.
   This helps connect the code/project to a physical machine and daily use.

3. Optional: a minimal collage.
   One panel with the desktop, one with the code, one with the terminal/logs. Good if you want the post to look more complete without being too busy.

## Best Order for the Carousel

1. Cover image: laptop or desktop hero shot
2. Omarchy desktop with the assistant context
3. Terminal/app flow screenshot
4. Config/code screenshot
5. README or architecture shot
6. Final slide with the short flow:

```text
Alt+Z -> speak -> transcribe -> Codex acts -> voice reply
```

## Notes

- Keep the visuals real. Real desktop, real logs, real code beats polished marketing graphics here.
- If you only use one visual, use the desktop + assistant context shot.
- If you use a video, keep it short and show one complete command from start to finish.
