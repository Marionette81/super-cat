from __future__ import print_function

from flask import g

import random
import requests as rq
import json
import datetime
from datetime import timezone
import time
import flask

from . import with_ics #Windows
from applicationCode.db import get_db #Windows
#import with_ics #MAC
#import db #MAC
#from db import get_db #MAC
import icalendar
from icalendar import *

from httplib2 import Http
from oauth2client import file, client, tools

url="https://doodle.com/api/v2.0/polls/"


# Fonction qui permet de convertir les dates de début et de fin d'un créneau Doodle sous la forme d'un json.
# Ce json est de la forme permettant d'ajouter un événement à un fichier ics.
# Il prend en argument le titre, le lieu et la description du Doodle ainsi que la liste des dates des créneaux.
def conversion(eventdate,titre,lieu,description,jour_entier):
    res=[]
    if jour_entier :
        for k in range(len(eventdate)):
            event2 = {    'summary': str(titre),
                          'location': str(lieu),
                          'description': str(description),
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
        for ki in range(0,len(eventdate),2):
            event2 = {
                          'summary': str(titre),
                          'location': str(lieu),
                          'description': str(description),
                          'start': {
                            'dateTime': eventdate[ki],
                            'timeZone': 'Europe/London',
                          },
                          'end': {
                            'dateTime': eventdate[ki+1],
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
def remplissage_doodle(preferences, optionsHash, key, nom_utilisateur, participantKey):

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



#Cette fonction renvoie la liste des évenements à réserver dans le calendrier, la liste des préférences à envoyer au Doodle
#et l'optionhash qui est utile pour écrire dans un Doodle.
def recup_creneau(key, nom_utilisateur, liste_calendriers):
    db = get_db()
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

    #On considère pour commencer que le sondage ne prends pas en compte l'option "si necessaire"
    siNecessaire= False
    if l['preferencesType']=="YESNOIFNEEDBE":
        siNecessaire=True

    # La liste des options (créneaux) de notre Doodle (vide à l'initialisation)
    liste_options = []

    # La liste préférences est la liste de 0 et/ou 1 qu'il faut envoyer au Doodle pour le remplir
    preferences=[]

    # Représente les places des créneaux finaux dans la liste des préférences
    place=[]

    # Compteur représentant le nombre de créneaux
    re=0

    # D'abord, on récupère la liste des dates des débuts et des fins (alternées 2 à 2) des événements du Doodle.
    # Puis on distingue le cas où le Doodle est fermé ou non
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
                #optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut)+3600000)
                optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut))
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
                    #optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin)+3600000)
                    optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin))
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

            # Par défaut, on met dans la liste des préférences où on est libre à aucun créneau
            preferences.append(0)

            # On vérifie si le créneau est toujours disponible
            if temps["available"]:

                # On ajoute la place de chaque créneau dans la liste des préferences
                place.append(re)

                # On ajoute l'heure de début à la liste des options
                optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut))
                liste_options.append(optionDebut)

                # Si le sondage n'est pas sur le jour entier, on récupère l'horaire de fin
                if not jour_entier :
                    # Date et heure de fin de l'événement
                    secondesEnPlusFin = int(str(temps["end"])[0:len(str(temps["end"]))])

                    # On ajoute les deux à la liste des options
                    optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin))
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
    try :
        limiteVotePers = l['rowConstraint']
    # S'il n'y a pas de limitation du nombre de votes par participant, on met le nombre de créneaux
    except:
        limiteVotePers = re 



    # Nous récupérons les événements du calendrier sur les créneaux récupérés dans listes_options
    eventdate=[]
    test=[]
    # Pour chaque calendrier de l'utilisateur, on vérifie si les créneaux du sondage sont libres
    for cal in liste_calendriers :
        calendrier=cal['calendrier_fichier']
        # Contient les créneaux du sondage libre dans le calendrier en cours
        eventdateprov=[]
        # On récupère les dates de début et de fin des événements contenus dans le calendrier
        events=with_ics.lectureCalendrier(calendrier)
        
        n = len(liste_options)
        
        # Un sondage ne peut être composé que de jours entiers ou de créneaux restreints, pas du mélange des 2
        if jour_entier :
            for i in  range(n):
                option = liste_options[i]
                # Pour un sondage sur un jour entier, on a la liste des jours du sondage dans liste_options
                jour=option.date()
                journeeLibre = True

                # On vérifie s'il y a déjà des événements dans le calendrier cette journée là
                for (dateDeb,dateFin,Id) in events:
                    if  dateDeb.date()==jour or dateFin.date()==jour :
                        journeeLibre = False

                # S'il n'y a pas d'événement dans le calendrier cette journée là :
                # On remplit le calendrier en réservant la journée et on modifie la liste preference en mettant 1 à la bonne place dans la liste
                if journeeLibre:
                    eventdateprov.append(jour)
                    eventdateprov.append(i)
        else :
            for i in range(0,n,2) :
                # Pour un sondage sur des créneaux restreints et non sur des jours entiers, on a successivement les horaires de début et de fin dans liste_options
                # Si i est pair, c'est une date de début, sinon c'est une date de fin
                debutCreneau = liste_options[i].replace(tzinfo=timezone.utc).astimezone(tz=None)
                finCreneau = liste_options[i+1].replace(tzinfo=timezone.utc).astimezone(tz=None)
                creneauLibre = True

                # On vérifie s'il y déjà des événements dans le calendrier sur le créneau
                for (dD,dF,Id) in events:
                    # On remet les horaires sur le même fuseau horaire pour pouvoir les comparer
                    dateDebEvent=dD.replace(tzinfo=timezone.utc).astimezone(tz=None)
                    dateFinEvent=dF.replace(tzinfo=timezone.utc).astimezone(tz=None)
                    # Si un créneau débute ou se termine pendant un des événements du calendrier, cela signifie que l'utilisateur n'est pas libre
                    if dateDebEvent <= debutCreneau <= dateFinEvent or dateDebEvent <= finCreneau <= dateFinEvent or (debutCreneau <= dateDebEvent <= finCreneau and debutCreneau <= dateFinEvent <= finCreneau):
                        creneauLibre = False

                # S'il n'y a pas d'évènement dans le calendrier à ce créneau, on ajoute la date de début et de fin du créneau à eventdateprov, ainsi que l'indice 
                # On remplit le calendrier en réservant le créneau et on modifie la liste preference en mettant 1 à la bonne place dans la liste
                if creneauLibre:
                    eventdateprov.append(debutCreneau)
                    eventdateprov.append(finCreneau)
                    eventdateprov.append(i)

        # On ajoute à la liste test la liste des créneaux retenus pour ce calendrier
        test.append(eventdateprov)

    # On ne remplit eventdate qu'avec les créneaux qui ont été retenus par tous les calendriers
    # C'est-à-dire ceux contenus dans tous les eventdateprov correspondant à chaque calendrier
    p = len(test)
    # On va comparer les créneaux retenus par le 1er calendrier avec ceux retenus par les autres
    q = len(test[0])
    # On distingue toujours les sondages composés de journées entières et ceux composés de créneaux restreints
    if jour_entier:
        for i in range(0,q,2):
            bonCreneau = True
            # On récupère un à un les créneaux retenus avec le 1er calendrier
            creneau = test[0][i]
            # Si pour un calendrier, le creneau n'apparait dans la liste des créneaux retenus, cela signifie que l'utilisateur n'est pas disponible pendant ce créneau 
            for j in range(1,p):
                if creneau not in test[j]:
                    bonCreneau = False
            # Si l'utilisateur est réellement disponible, on ajoute le creneau à eventdate et on remplit la liste des préférences à la place correspondant au créneau
            if bonCreneau:
                eventdate.append(creneau)
                a = test[0][i+1]
                if siNecessaire:
                    preferences[place[a]]=2
                else:
                    preferences[place[a]]=1
                # Enfin, on complète les tables creneau et creneau_sondage de la base de données
                db.execute(
                    'INSERT INTO creneau (cle,jourComplet)'
                    ' VALUES (?, ?)',
                    (key+str(place[a]),creneau,)
                )
                id_creneau= (db.execute(
                                    'SELECT MAX(id) FROM creneau WHERE cle = ?',
                                    (key+str(place[a//2]),)).fetchone()['id'])
                db.execute(
                    'INSERT INTO creneau_sondage (creneau_id,sondage_key,user_id)'
                    ' VALUES (?, ?)',
                    (id_creneau,key,g.user['id'])
                )
                db.commit()

    else:
        for i in range(0,q,3):
            # On récupère les dates de début et de fin des créneaux retenus avec le 1er calendrier
            debutCreneau = test[0][i]
            finCreneau = test[0][i+1]
            # On crée une liste indiquant si le créneau a également été retenu par le j+1ème calendrier
            contientCreneau = (p-1)*[0]
            # On compte le nombre de calendriers ayant retenus le calendrier
            nbCal = 1
            for j in range(1,p):
                r = len(test[j])
                for k in range(0,r,3):
                    # Si le créneau a été retenu par le j+1ème calendrier, on passe la valeur de contientCreneau à 1
                    if test[j][k]==debutCreneau and test[j][k+1]==finCreneau:
                        contientCreneau[j-1]=1
                if contientCreneau[j-1] != 0:
                    nbCal += 1
            # Si le nombre de calendriers ayant retenu le créneau est égal au nombre total de calendriers, l'utilisateur est réellement disponilble
            if nbCal==p :
                # On ajoute le creneau à eventdate et on remplit la liste des préférences à la place correspondant au créneau
                eventdate.append(debutCreneau)
                eventdate.append(finCreneau)
                a = test[0][i+2]
                if siNecessaire:
                    preferences[place[a//2]]=2
                else:
                    preferences[place[a//2]]=1
                # Enfin, on complète les tables creneau et creneau_sondage de la base de données
                db.execute(
                    'INSERT INTO creneau (cle,debut,fin)'
                    ' VALUES (?, ?,?)',
                    (key+str(place[a//2]),debutCreneau,finCreneau,)
                )
                id_creneau= (db.execute(
                                    'SELECT MAX(id) FROM creneau WHERE cle = ?',
                                    (key+str(place[a//2]),)).fetchone()['MAX(id)'])
                #print(id_creneau)
                db.execute(
                    'INSERT INTO creneau_sondage (creneau_id,sondage_key,user_id)'
                    ' VALUES (?, ?, ?)',
                    (id_creneau,key,g.user['id'])
                )
                db.commit()
                

    return eventdate,preferences,optionsHash,titre,lieu,description,jour_entier,final,limiteVotePers,siNecessaire


# On remplit le calendrier avec les créneaux réservés pour le sondage tant qu'il n'est pas terminé
def reserve_creneaux(eventdate, jour_entier, key, final, calendrier):

    eventfinal=[]
    
    # On parcourt les événements qu'on a converti après avoir récupéré les dates des créneaux dans le Doodle
    for k in eventdate:

        # On récupère la liste des identifiants des événements déjà contenus dans le calendrier
        listeId=[]
        for (deb, fin, Id) in with_ics.lectureCalendrier(calendrier):
            listeId.append(Id)
        
        # On crée l'événement correspondant à k
        event = Event()
        event.add('summary', k["summary"].encode('utf8'))
        event.add('location', k["location"].encode('utf8'))
        event.add('description', k["description"].encode('utf8'))
        if jour_entier:
            event.add('dtstart', k["start"]["date"])
            event.add('dtend', k["end"]["date"])
        else:
            event.add('dtstart', k["start"]["dateTime"])
            event.add('dtend', k["end"]["dateTime"])
        if final:
            event.add('status','CONFIRMED')
        else:
            event.add('status','TENTATIVE')
            
        # On génère aléatoirement l'identifiant de l'événement
        Id=random.randint(1,10**7)
        while Id in listeId :
            Id=random.randint(1,10**7)
        event.add('uid', Id)

        # On l'ajoute l'événement
        with_ics.ajoutCalendrier(calendrier,event)

        # On l'ajoute à la liste des événements
        eventfinal.append(k)

    return eventfinal



# Cette fonction permet d'effacer du calendrier tous les créneaux réservés précedement à partir du Doodle
# afin de tout recommencer lors d'une mise à jour
def efface(eventdate, key, nom_utilisateur, calendrier, numCal):

    # On récupère tous les événements du calendrier
    events = with_ics.lectureCalendrier(calendrier)
    # On récupère les créneaux du sondage au bon format
    evtd = eval(eventdate)

    # On récupère les événements à effacer et on les supprime
    for creneau in evtd :
        try:
            # On récupère les dates de début et de fin du créneau
            if creneau.get('start').get('dateTime') == None :
                d = creneau.get('start').get('date')
                f = creneau.get('end').get('date')
                for (dD,dF,Id) in events:
                    # Pour permettre la comparaison des dates, on passe en mode binaire
                    dateDeb=vDatetime(dD).to_ical()
                    dateFin=vDatetime(dF).to_ical()
                    debut=vDatetime(datetime.datetime(d.year,d.month,d.day)).to_ical()
                    fin=vDatetime(datetime.datetime(f.year,f.month,f.day)).to_ical()
                    # Si l'événement possède la même date de début et de fin, c'est celui qu'on cherche, donc on le supprime
                    if dateDeb==debut and dateFin==fin :
                        with_ics.suppressionCalendrier(calendrier, Id)
            else :
                d = creneau.get('start').get('dateTime')
                f = creneau.get('end').get('dateTime')
                for (dD,dF,Id) in events:
                    # Pour permettre la comparaison des dates, on passe en mode binaire
                    dateDeb=vDatetime(dD).to_ical()
                    dateFin=vDatetime(dF).to_ical()
                    debut=vDatetime(d).to_ical()
                    fin=vDatetime(f).to_ical()
                    # Si l'événement possède la même date de début et de fin, c'est celui qu'on cherche, donc on le supprime
                    if dateDeb==debut and dateFin==fin :
                        with_ics.suppressionCalendrier(calendrier, Id)
        except:
            # Au cas où le propriétaire du calendrier a supprimé l'événement à la main
            print('Déja sup')

    # On récupère tout le json du doodle pour retouver l'id de la personne considérée par la mise à jour 
    # On fait ça uniquement pour le premier calendrier (identifié grâce à numCal)
    if (numCal==1):
        l=rq.get(url+key)
        ri=json.loads(l.content)
        li=-1
        
        for i in range (len(ri['participants'])):
            if ri['participants'][i]['name']==nom_utilisateur:
                li=i
                
        if li!=(-1):
            # url nécesssaire pour l'envoi des infos
            url2=url+key+"/participants/"+str(ri['participants'][li]['id'])
            # requête put qui modifie un post précedent
            ra = rq.delete(url2)