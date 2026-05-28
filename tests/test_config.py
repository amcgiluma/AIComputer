import tempfile
import unittest
from pathlib import Path

from voice_codex.config import DEFAULT_CONFIG, ensure_config, load_config


class ConfigTests(unittest.TestCase):
    def test_ensure_and_load_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            ensure_config(path)
            config = load_config(path)
            self.assertEqual(config["handy"]["model"], "canary-180m-flash")
            self.assertEqual(config["tts"]["engine"], "piper")
            self.assertIn("piper_model", config["tts"])
            self.assertEqual(config["codex"]["sandbox"], "danger-full-access")
            self.assertTrue(config["memory"]["enabled"])
            self.assertEqual(config["ui"]["indicator"], "notification")
            self.assertFalse(config["ui"]["show_window_on_start"])

    def test_default_codex_model_label_is_preserved(self):
        self.assertEqual(DEFAULT_CONFIG["codex"]["model_label"], "gpt 5.4 Mini Low")
        self.assertEqual(DEFAULT_CONFIG["codex"]["model"], "gpt-5.4-mini")
        self.assertEqual(DEFAULT_CONFIG["codex"]["model_reasoning_effort"], "low")


if __name__ == "__main__":
    unittest.main()
