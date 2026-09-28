"""API regression tests without a real DeepSeek key or persistent database."""

import io
import json
import os
import socket
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from flask import Flask

from src.models.note import db
from src.routes.note import note_bp
from src.routes.translation import DEEPSEEK_URL, DEFAULT_MODEL, translation_bp


class NoteTranslationApiTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(self.app)
        self.app.register_blueprint(note_bp, url_prefix='/api')
        self.app.register_blueprint(translation_bp, url_prefix='/api')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_note_crud_and_search(self):
        created = self.client.post('/api/notes', json={'title': 'Draft', 'content': 'Hello world'})
        self.assertEqual(created.status_code, 201)
        note_id = created.json['id']

        self.assertEqual(self.client.get('/api/notes').json[0]['id'], note_id)
        self.assertEqual(self.client.get(f'/api/notes/{note_id}').json['content'], 'Hello world')
        self.assertEqual(len(self.client.get('/api/notes/search?q=Hello').json), 1)

        updated = self.client.put(f'/api/notes/{note_id}', json={'content': 'Bonjour'})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json['content'], 'Bonjour')
        self.assertEqual(self.client.delete(f'/api/notes/{note_id}').status_code, 204)
        self.assertEqual(self.client.get('/api/notes').json, [])

    def test_translation_input_validation_and_missing_configuration(self):
        with patch.dict(os.environ, {}, clear=True), patch('src.routes.translation.urlopen') as upstream:
            for body in ({'text': '  ', 'target_language': 'en'},
                         {'text': 'Hello', 'target_language': 'xx'}):
                self.assertEqual(self.client.post('/api/translate', json=body).status_code, 400)
            self.assertEqual(self.client.post('/api/translate', json=[]).status_code, 400)
            response = self.client.post('/api/translate', json={'text': 'Hello', 'target_language': 'fr'})
            self.assertEqual(response.status_code, 503)
            self.assertIn('DEEPSEEK_API_KEY', response.json['error'])
            upstream.assert_not_called()

    def test_translation_request_and_response(self):
        note = self.client.post('/api/notes', json={'title': 'Original', 'content': 'Hello'}).json
        fake_response = io.BytesIO(json.dumps({
            'choices': [{'message': {'content': 'Bonjour'}}]
        }).encode('utf-8'))
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'}, clear=True), \
             patch('src.routes.translation.urlopen') as upstream:
            upstream.return_value.__enter__.return_value = fake_response
            response = self.client.post('/api/translate', json={
                'text': 'Hello', 'target_language': 'fr', 'api_key': 'ignored-client-value'
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'translation': 'Bonjour'})
        self.assertEqual(self.client.get(f"/api/notes/{note['id']}").json['content'], 'Hello')
        sent_request = upstream.call_args.args[0]
        self.assertEqual(sent_request.full_url, DEEPSEEK_URL)
        self.assertEqual(sent_request.get_header('Authorization'), 'Bearer test-key')
        self.assertEqual(upstream.call_args.kwargs['timeout'], 30)
        sent_body = json.loads(sent_request.data)
        self.assertEqual(sent_body['model'], DEFAULT_MODEL)
        self.assertEqual(sent_body['thinking'], {'type': 'disabled'})
        self.assertEqual(sent_body['messages'][1], {'role': 'user', 'content': 'Hello'})
        self.assertNotIn('ignored-client-value', json.dumps(sent_body))

    def test_optional_model_override(self):
        fake_response = io.BytesIO(b'{"choices":[{"message":{"content":"Bonjour"}}]}')
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key', 'DEEPSEEK_MODEL': 'deepseek-v4-pro'}, clear=True), \
             patch('src.routes.translation.urlopen') as upstream:
            upstream.return_value.__enter__.return_value = fake_response
            response = self.client.post('/api/translate', json={'text': 'Hello', 'target_language': 'fr'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(upstream.call_args.args[0].data)['model'], 'deepseek-v4-pro')

    def test_provider_timeout_and_error(self):
        body = {'text': 'Hello', 'target_language': 'fr'}
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test-key'}, clear=True), \
             patch('src.routes.translation.urlopen') as upstream:
            upstream.side_effect = socket.timeout()
            self.assertEqual(self.client.post('/api/translate', json=body).status_code, 504)

            upstream.side_effect = HTTPError(DEEPSEEK_URL, 429, 'rate limited', {}, None)
            response = self.client.post('/api/translate', json=body)
            self.assertEqual(response.status_code, 503)
            self.assertIn('rate limit', response.json['error'])
            self.assertNotIn('test-key', response.json['error'])

            upstream.side_effect = HTTPError(DEEPSEEK_URL, 401, 'unauthorized', {}, None)
            response = self.client.post('/api/translate', json=body)
            self.assertEqual(response.status_code, 502)
            self.assertIn('DEEPSEEK_API_KEY', response.json['error'])

            upstream.side_effect = HTTPError(DEEPSEEK_URL, 402, 'insufficient balance', {}, None)
            response = self.client.post('/api/translate', json=body)
            self.assertEqual(response.status_code, 503)
            self.assertIn('balance', response.json['error'])


if __name__ == '__main__':
    unittest.main()
