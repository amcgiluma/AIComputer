import tempfile
import unittest
from pathlib import Path

from voice_codex.memory import DEFAULT_FOLDERS, ensure_memory_dir, load_memory_context


class MemoryTests(unittest.TestCase):
    def test_ensure_memory_dir_creates_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = ensure_memory_dir({"dir": tmp})

            self.assertEqual(root, Path(tmp))
            self.assertTrue((root / "README.md").exists())
            for folder in DEFAULT_FOLDERS:
                self.assertTrue((root / folder).is_dir())

    def test_load_memory_context_reads_user_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "preferences").mkdir()
            (root / "preferences" / "style.md").write_text("Responder directo.", encoding="utf-8")
            (root / "README.md").write_text("No debe entrar en el prompt.", encoding="utf-8")

            context = load_memory_context({"dir": tmp, "max_bytes": 1000})

            self.assertIn("preferences/style.md", context)
            self.assertIn("Responder directo.", context)
            self.assertNotIn("No debe entrar", context)


if __name__ == "__main__":
    unittest.main()
