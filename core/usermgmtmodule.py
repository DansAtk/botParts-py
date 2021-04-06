import sys
import sqlite3
import pytz
import datetime
import calendar

from core import config
from core import commandM
from core import databaseM

mSelf = sys.modules[__name__]
includes = {}
config.imports.update(__name__)

class user:
    def __init__(self
