"""Database selection must never fall back to SQLite on Vercel."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.database_config import database_uri


class DatabaseConfigTests(unittest.TestCase):
    def test_local_without_database_url_uses_existing_sqlite_path(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {}, clear=True):
            uri = database_uri(root)
            self.assertEqual(uri, f"sqlite:///{Path(root) / 'database' / 'app.db'}")
            self.assertTrue((Path(root) / 'database').is_dir())

    def test_postgres_url_does_not_create_a_local_database(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(
            os.environ, {'DATABASE_URL': 'postgresql://'}, clear=True
        ):
            self.assertEqual(database_uri(root), 'postgresql+psycopg2://')
            self.assertFalse((Path(root) / 'database').exists())

        with tempfile.TemporaryDirectory() as root, patch.dict(
            os.environ, {'DATABASE_URL': 'postgres://'}, clear=True
        ):
            self.assertEqual(database_uri(root), 'postgresql+psycopg2://')
            self.assertFalse((Path(root) / 'database').exists())

    def test_vercel_without_database_url_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(
            os.environ, {'NOTETAKER_VERCEL': '1'}, clear=True
        ), patch('src.database_config.os.makedirs') as make_dirs:
            with self.assertRaisesRegex(RuntimeError, 'DATABASE_URL is required'):
                database_uri(root)
            make_dirs.assert_not_called()
            self.assertFalse((Path(root) / 'database').exists())

    def test_non_postgres_database_url_is_rejected(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite://'}, clear=True):
            with self.assertRaisesRegex(ValueError, 'PostgreSQL'):
                database_uri('unused')


if __name__ == '__main__':
    unittest.main()
