"""The deployment entry must serve the real app and static page."""

import importlib
import os
import unittest
from unittest.mock import patch


class MainEntryTests(unittest.TestCase):
    def test_main_app_serves_static_files_and_note_crud(self):
        with patch.dict(os.environ, {}, clear=True), patch(
            'src.database_config.database_uri', return_value='sqlite:///:memory:'
        ):
            main = importlib.import_module('src.main')

        client = main.app.test_client()
        with client.get('/') as page:
            self.assertEqual(page.status_code, 200)
            self.assertIn(b'id="translateBtn"', page.data)
        with client.get('/favicon.ico') as icon:
            self.assertEqual(icon.status_code, 200)

        created = client.post('/api/notes', json={'title': 'Deploy test', 'content': 'Original'})
        self.assertEqual(created.status_code, 201)
        note_id = created.json['id']
        self.assertEqual(client.get(f'/api/notes/{note_id}').json['content'], 'Original')
        updated = client.put(f'/api/notes/{note_id}', json={'content': 'Changed'})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json['content'], 'Changed')
        self.assertEqual(client.delete(f'/api/notes/{note_id}').status_code, 204)
        self.assertEqual(client.get('/api/notes').json, [])


if __name__ == '__main__':
    unittest.main()
