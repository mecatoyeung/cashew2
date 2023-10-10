import os

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from ..models.parser import Parser

PARSERS_URL = reverse('parsers:parsers-list')

def create_user(**params):
    """ Create and return a new user. """
    return get_user_model().objects.create_user(**params)

class PublicParserAPITests(TestCase):
  """ Test unauthenticated API requests. """

  def setUp(self):
    self.client = APIClient()

  def test_auth_required(self):
    """ Test auth is required to call API. """
    res = self.client.get(PARSERS_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateParserTests(TestCase):
  
  def setUp(self):
    self.client = APIClient()
    self.user = create_user(
       username="user@example.com",
        email="user@example.com",
        password="test123",
    )
    self.client.force_authenticate(self.user)

  def test_create_parser_should_be_successful(self):
    """ Test creating a parser. """
    payload = {
        'user': self.user,
        'type': ParserType.LAYOUT,
        'name': "Test Parser",
    }
    res = self.client.post(PARSERS_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    parser = Parser.objects.get(id=res.data['id'])
    for k, v in payload.items():
        self.assertEqual(getattr(parser, k), v)
    self.assertEqual(parser.user, self.user)