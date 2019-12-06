from __future__ import print_function

import random
import requests as rq
import json
import datetime
from datetime import timezone
import time
import flask

import with_ics
import icalendar
from icalendar import *

from httplib2 import Http
from oauth2client import file, client, tools

url="https://framadate.org/"

def recup_creneau(key,nom_utilisateur,participant_key,liste_calendriers):
    # 1er janvier 1970 en date python
    a = datetime.datetime(1970, 1, 1)

    # On stocke le json dans le dictionnaire l
    r = rq.get(url+key)
    l = json.loads(r.content)
    print(l)
    return "test"
    
