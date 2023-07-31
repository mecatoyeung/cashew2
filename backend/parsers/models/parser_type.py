from django.db import models

from datetime import datetime
from django.utils import timezone

from enum import Enum

from django.contrib.auth.models import User

class ParserType(Enum):

  LAYOUT = "LAYOUT"
  ROUTING = "ROUTING"

  @classmethod
  def choices(cls):
    return tuple((i.name, i.value) for i in cls)
