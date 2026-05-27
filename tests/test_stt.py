import tempfile
import unittest
from pathlib import Path

from voice_codex.stt import _is_noise_transcript, transcribe_recording


class STTTests(unittest.TestCase):
    def test_missing_audio_returns_none(self):
        config = {"stt": {"engine": "whisper_cpp"}}
        self.assertIsNone(transcribe_recording(config, Path("/missing/audio.wav")))

    def test_missing_whisper_returns_none(self):
        with tempfile.NamedTemporaryFile() as fh:
            fh.write(b"0" * 8192)
            fh.flush()
            config = {
                "stt": {
                    "engine": "whisper_cpp",
                    "whisper_executable": "/missing/whisper-cli",
                    "whisper_model": "/missing/model.bin",
                }
            }
            self.assertIsNone(transcribe_recording(config, Path(fh.name)))

    def test_filters_noise_markers(self):
        self.assertTrue(_is_noise_transcript("[Música]"))
        self.assertTrue(_is_noise_transcript("[Música suave]"))
        self.assertTrue(_is_noise_transcript("[music]"))
        self.assertFalse(_is_noise_transcript("abre youtube con musica"))


if __name__ == "__main__":
    unittest.main()
