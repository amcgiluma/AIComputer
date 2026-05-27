import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from voice_codex import handy_bridge


class HandyBridgeTests(unittest.TestCase):
    def test_latest_transcription_after(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "history.db"
            with sqlite3.connect(db_path) as db:
                db.execute(
                    """
                    create table transcription_history (
                        id integer primary key autoincrement,
                        file_name text not null,
                        timestamp integer not null,
                        saved boolean not null default 0,
                        title text not null,
                        transcription_text text not null,
                        post_processed_text text
                    )
                    """
                )
                db.execute(
                    """
                    insert into transcription_history
                    (file_name, timestamp, title, transcription_text, post_processed_text)
                    values ('a.wav', 1, 't', 'hola mundo', null)
                    """
                )

            with mock.patch.object(handy_bridge, "HANDY_HISTORY", db_path):
                self.assertEqual(handy_bridge.latest_history_id(), 1)
                self.assertEqual(handy_bridge.latest_transcription_after(0), (1, "hola mundo"))
                self.assertIsNone(handy_bridge.latest_transcription_after(1))


if __name__ == "__main__":
    unittest.main()
