#Ce fichier contient toutes les fonctions d'interaction entre le calendrier et le sondage Doodle

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests as rq
import json
import datetime
import time
import flask

from . import with_calendar


url="https://doodle.com/api/v2.0/polls/"


# Fonction qui permet de convertir les dates de début et de fin d'un créneau Doodle sous la forme d'un json.
# Ce json est sous la forme qu'il faut envoyer à google calendar pour ajouter un événement. Il prend en argument le titre, le lieu
#et la description du Doodle ainsi que la liste des dates des créneaux.
def conversion(eventdate,titre,lieu,description, jour_entier):
    res=[]
    if jour_entier :

        for k in range(len(eventdate)):

            event2 = {
                          'summary': titre,
                          'location': lieu,
                          'description': description,
                          'start': {
                            'date': eventdate[k],
                            'timeZone': 'Europe/London',
                          },
                          'end': {
                            'date': eventdate[k],
                            'timeZone': 'Europe/London',
                          },
                          'recurrence': [
                            'RRULE:FREQ=DAILY;COUNT=1'
                          ],
                          'reminders': {
                            'useDefault': False,
                            'overrides': [
                              {'method': 'email', 'minutes': 24 * 60},
                              {'method': 'popup', 'minutes': 10},
                            ],
                          },
                        }

            res.append(event2)

    else :
        for ki in range( len(eventdate)//2):

            event2 = {
                          'summary': titre,
                          'location': lieu,
                          'description': description,
                          'start': {
                            'dateTime': eventdate[2*ki],
                            'timeZone': 'Europe/London',
                          },
                          'end': {
                            'dateTime': eventdate[2*ki+1],
                            'timeZone': 'Europe/London',
                          },
                          'recurrence': [
                            'RRULE:FREQ=DAILY;COUNT=1'
                          ],
                          'reminders': {
                            'useDefault': False,
                            'overrides': [
                              {'method': 'email', 'minutes': 24 * 60},
                              {'method': 'popup', 'minutes': 10},
                            ],
                          },
                        }
            res.append(event2)

    return res


# Fonction qui remplit le Doodle selon les préférences de l'utilisateur receuillies à partir de son calendrier
def remplissage_doodle(preferences,optionsHash,key, nom_utilisateur, participantKey):

    # json à envoyer pour remplir le Doodle
    envoi = {"name" : nom_utilisateur, "preferences" :
    preferences, "participantKey" : participantKey,
    "optionsHash" : optionsHash}

    # url nécessaire pour modifier le Doodle
    url2=url+ key + "/participants"


    # requête post pour écrire pour la première fois dans le Doodle
    ri = rq.post(url2, json = envoi)


# Fonction qui renvoie True si le sondage effectué est sur une journée entière, False sinon
def jourEntier (evenement):
    try :
        evenement["end"]
        return False
    except :
        return True



def recup_creneau(key,nom_utilisateur, participant_key):

    if 'credentials' in flask.session:
        service=with_calendar.connection_cal()

    # 1er janvier 1970 en date python
    a = datetime.datetime(1970, 1, 1)

    # On stocke le json dans le dictionnaire l
    r = rq.get(url+key)
    l = json.loads(r.content)
    optionsHash=l["optionsHash"]

    # Le sondage peut être sur des créneaux horaires restreints ou sur des jours entiers.
    # On initialise à False le booléen qui indique si le sondage est sur des jours entiers ou non.
    jour_entier = False

    # On considère que le sondage n'est pas final pour commencer
    final=False

    # La liste des options (créneaux) de notre Doodle (vide à l'initialisation)
    liste_options = []

    # La liste préférences est la liste de 0 et/ou 1 qu'il faut envoyer au Doodle pour le remplir
    preferences=[]

    # Représente les places des créneaux finaux dans la liste des préférences
    place=[]

    # Compteur représentant le nombre de créneaux
    re=0

    # D'abord, on récupère la liste des dates des débuts et des fins (alternées 2 à 2) des événements du Doodle.

    # On distingue le cas ou le Doodle est fermé ou non

    try:
        # On regarde si le sondage est fermé ou pas
        t=l['closed']
        final = True
        # Si le sondage est fermé, on récupère tous les créneaux qui sont finaux
        for temps in l["options"]:

            jour_entier = jourEntier(temps)

            try:
                # On vérifie si l'événement est final
                bool=temps['final']

                # Date et heure de commencement de l'événement
                secondesEnPlusDebut = int(str(temps["start"])[0:len(str(temps["start"]))])

                # On ajoute l'heure de début à la liste des options
                # L'heure est ajoutée au format : datetime.datetime(yyyy, mm, dd, hh, mm, ss)
                optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut)+3600000)
                liste_options.append(optionDebut)

                # Au début, on met par défaut que la personne est libre à tous les créneaux finaux
                preferences.append(1)

                # Vu qu'on récupère seulement les crénaux finaux, on conserve leur place dans la liste des préférences
                place.append(re)

                # Si le sondage n'est pas sur le jour entier, on récupère l'horaire de fin
                if not jour_entier :

                    # Date et heure de fin de l'événement
                    secondesEnPlusFin = int(str(temps["end"])[0:len(str(temps["end"]))])

                    # On l'ajoute à la liste des options
                    optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin)+3600000)
                    liste_options.append(optionFin)

            except:
                # Si la date n'est pas finale, on ajoute 0 aux préférences, et nous n'avons donc pas à nous soucier des dates non-finales
                preferences.append(0)

            re+=1


    except:
        # Si le sondage est toujours ouvert, on récupère tous les créneaux du Doodle
        for temps in l["options"]:

            jour_entier = jourEntier(temps)

            # Date et heure de commencement de l'événement
            secondesEnPlusDebut = int(str(temps["start"])[0:len(str(temps["start"]))])

            # On ajoute l'heure de début à la liste des options
            optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut)+3600000)
            liste_options.append(optionDebut)

            # Par défaut, on met dans la liste des préférences où on est libre à aucun créneau
            preferences.append(0)

            # On ajoute la place de chaque créneau dans la liste des préferences
            place.append(re)

            # Si le sondage n'est pas sur le jour entier, on récupère l'horaire de fin
            if not jour_entier :

                # Date et heure de fin de l'événement
                secondesEnPlusFin = int(str(temps["end"])[0:len(str(temps["end"]))])

                # On ajoute les deux à la liste des options
                optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin)+3600000)
                liste_options.append(optionFin)

            re+=1


    # On stocke les informations importantes du Doodle
    titre = l["title"]
    try :
        lieu = l["location"]["name"]
    except:
        lieu = "Pas de lieu spécifié"
    try:
        description = l["description"]
    except:
        description = "Pas de description spécifiée"


    # Nous récupérons les événements du calendrier sur les créneaux récupérés dans listes_options


    eventdate=[]
    i = 1

    if jour_entier :

        for option in liste_options :

            # Pour un sondage sur un jour entier, on a la liste de jours du sondage dans liste_options
            jour = str(option)[0:10]
            debut=str(option)[0:10]+'T00:00:00+01:00'
            fin=str(option)[0:10]+'T23:59:59+01:00'
            events_result = service.events().list(calendarId='primary', timeMin=debut, timeMax=fin, singleEvents=True).execute()
            events = events_result.get('items', [])

            # S'il n'y a pas d'événement dans le calendrier cette journée là :
            # On remplit le calendrier en réservant la journée et on modifie la liste preference en mettant 1 à la bonne place dans la liste
            if not events:
                eventdate.append(jour)
                preferences[place[i-1]]=1
            i+=1

    else :

        for option in liste_options :

            # Pour un sondage sur des créneaux et non sur des jours entiers, on a successivement les horaires de début et de fin dans liste_options

            # Si i est pair, c'est une date de début
            if i%2==1 :
                debut=str(option)[0:10]+'T'+str(option)[11:20]+'+01:00'
                i+=1

            # Si i est impair c'est une date de fin
            else :
                fin=str(option)[0:10]+'T'+str(option)[11:20]+'+01:00'
                # On récupère les évènements du calendrier se situant entre début et fin (même s'ils commencent ou terminent après)
                events_result = service.events().list(calendarId='primary', timeMin=debut, timeMax=fin).execute()
                events = events_result.get('items', [])

                # S'il n'y a pas d'évènement dans le calendrier à ce créneau :
                # On remplit le calendrier en réservant le créneau et on modifie la liste preference en mettant 1 à la bonne place dans la liste
                if not events:
                    eventdate.append(debut)
                    eventdate.append(fin)
                    preferences[place[i//2-1]]=1

                i+=1

    # On convertit la liste des horaires des créneaux en liste des événements qu'on va envoyer au calendrier
    eventdate2 = conversion(eventdate,titre,lieu,description, jour_entier)
    remplissage_doodle(preferences,optionsHash,key, nom_utilisateur, participant_key)

    #Cette fonction renvoie la liste des évenements à réserver dans le calendrier, la liste des préférences à envoyer au Doodle et l'optionhash qui est utile
    #pour ecrire dans un Doodle.
    return eventdate2,preferences,optionsHash,titre,lieu,description, jour_entier, final


# On remplit le calendrier avec les créneaux réservés pour le sondage tant qu'il n'est pas terminé
def reserve_creneaux(eventdate, jour_entier, key):

    if 'credentials' in flask.session:
        service=with_calendar.connection_cal()

    eventfinal=[]
    # On parcourt les événements qu'on a converti après avoir récupéré les dates des créneaux dans le Doodle
    for k in eventdate:

        # On réserve le créneau prévu dans le calendrier
        service.events().insert(calendarId='primary', body=k).execute()
        j=0
        # On récupère les événements qu'on vient juste de réserver car lorsqu'on insère un événement il y a un id qui est créé par le calendrier et
        # on en a besoin pour effacer les événements quand nécessaire
        if jour_entier :
            event=service.events().list(calendarId='primary', timeMin=k['start']['date']+'T00:00:00+01:00', timeMax=k['end']['date']+'T23:59:59+01:00', singleEvents=True).execute()['items']
        else :
            event=service.events().list(calendarId='primary', timeMin=k['start']['dateTime'], timeMax=k['end']['dateTime']).execute()['items']

            # La commande précedente renvoie un liste des événements qui ont un moment de commun avec l'intervalle donné, on parcourt donc la liste jusqu'à trouver
            # l'événement qu'on vient d'insérer en comparant les dates de début et de fin
            #while event[j]['end']['dateTime']!=k['end']['dateTime'] and event[j]['start']['dateTime']!=k['start']['dateTime']:
                #j=j+1

            # On l'ajoute à la liste des événements, cette liste est comme eventdate sauf qu'on a les id en plus
        eventfinal.append(event[j])

    return eventfinal



# Cette fonction permet d'effacer du calendrier tous les créneaux réservés précedement à partir du Doodle afin de tout recommencer lors d'une mise à jour
def efface(eventdate, key, nom_utilisateur):

    if 'credentials' in flask.session:
        service=with_calendar.connection_cal()

    # On récupère les événements à effacer et on les supprime
    for evenement in eventdate :
        print(evenement)
        try:
            service.events().delete(calendarId='primary', eventId=evenement['id']).execute()
        except:
            # Au cas où le propriétaire du calendrier a supprimé l'événement à la main
            print('Déja sup')

    # On récupère tout le json du doodle pour retouver l'id de la personne considérée par la mise à jour
    l=rq.get(url+key)
    ri=json.loads(l.content)
    li=0

    # On attend de tomber sur le participant ayant le même nom que le propriétaire du calendrier
    while(ri['participants'][li]['name']!=nom_utilisateur):
        li+=1

    # url nécesssaire pour l'envoi des infos
    url2=url+key+"/participants/"+str(ri['participants'][li]['id'])
    print(url2)
    # requête put qui modifie un post précedent
    ra = rq.delete(url2)


# Fonction qui permet de mettre à jour les réponses apportées au Doodle et les events réservés, par exemple si le Doodle est modifié
def mise_a_jour(key,nom_utilisateur,eventdate, participant_key):

    # On commence par tout effacer dans le calendrier
    efface(eventdate, key, nom_utilisateur)

    # On récupère les créneaux où l'utilisateur est libre
    eventts=recup_creneau(key, nom_utilisateur, participant_key)
    # Enfin, on reserve dans le calendrier les créneaux libres
    creneau_reserve=reserve_creneaux(eventts[0],eventts[6],key)

    return creneau_reserve, eventts[7]
