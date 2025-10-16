from django.test import TestCase, Client
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock

class ChatbotAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.chat_url = reverse('chat')

    @patch('chatbot.rag.client')
    def test_chat_endpoint_success(self, mock_openai_client):
        """
        Test that the chat endpoint returns a successful response with a mocked OpenAI client.
        """
        # Mock the embedding response
        mock_embedding = MagicMock()
        mock_embedding.embedding = [0.1] * 1536  # text-embedding-ada-002 dimension
        mock_openai_client.embeddings.create.return_value = MagicMock(data=[mock_embedding])

        # Mock the chat completion response
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a mocked response from Pipo."
        mock_openai_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        data = {'message': 'Hello'}
        response = self.client.post(self.chat_url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())
        self.assertEqual(response.json()['response'], "This is a mocked response from Pipo.")

    def test_chat_endpoint_no_message(self):
        """
        Test that the chat endpoint returns a 400 error if no message is provided.
        """
        data = {}
        response = self.client.post(self.chat_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'No message provided'})

    def test_chat_endpoint_invalid_json(self):
        """
        Test that the chat endpoint returns a 400 error if the JSON is invalid.
        """
        response = self.client.post(self.chat_url, data='not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid JSON'})

    def test_chat_endpoint_invalid_method(self):
        """
        Test that the chat endpoint returns a 405 error for invalid request methods.
        """
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {'detail': 'Method "GET" not allowed.'})
