from __future__ import print_function

import icalendar
from icalendar import *
import datetime


# Renvoie une liste contenant les dates de début et de fin ainsi que l'identifiant des événements contenus dans le calendrier
def lectureCalendrier(fichier):
    # On ouvre le fichier
    f=open(fichier,'r')
    fcal=Calendar.from_ical(f.read())
    
    # On récupère le nombre d'événements contenus dans le calendrier
    n=len(fcal.subcomponents)
    
    # On construit une liste contenant les dates de début et de fin de tous les événements du calendrier
    plage_indipos_lisible=[]
    date_test = datetime.date(1970,1,1)
    for i in range(n):
        comp=fcal.subcomponents[i]
        if comp.name=="VEVENT":
            # On récupère les dates de début et de fin des événements du calendrier
            ds=comp.decoded('dtstart')
            # On fait en sorte que les dates récupérées soient de classe datetime.datetime
            if type(ds)==type(date_test):
                ds=datetime.datetime(ds.year,ds.month,ds.day)
            de=comp.decoded('dtend')
            if type(de)==type(date_test):
                de=datetime.datetime(de.year,de.month,de.day)
            plage_indipos_lisible.append((ds,de,comp.get('uid')))
    
    # On ferme le fichier
    f.close()

    # On renvoie la liste de plages horaires
    return plage_indipos_lisible


#l=lectureCalendrier('cal_essai.ics')


# Ajoute un événement au calendrier contenu dans le fichier 
def ajoutCalendrier(fichier,event):
    # On ouvre le calendrier en mode lecture
    f=open(fichier,'r')
    
    # On récupère le calendrier associé au fichier et on ajoute l'événement au calendrier
    fcal=Calendar.from_ical(f.read())
    fcal.add_component(event)
    
    # On ferme le fichier
    f.close()
    
    # On ouvre de nouveau le fichier, cette fois en mode écriture et on récupère dans le fichier toutes les informations du calendrier
    g=open(fichier,'wb')
    g.write(fcal.to_ical())
    
    # On ferme le fichier
    g.close()


# Fonction permettant de supprimer l'événement possédant la clé 'key' du calendrier 'fichier'
def suppressionCalendrier(fichier,key):
    # On ouvre le calendrier en mode lecture
    f=open(fichier,'r')
    
    # On récupère le calendrier associé au fichier
    fcal=Calendar.from_ical(f.read())
    
    # On cherche l'indice de l'évenement à supprimer
    i=-1
    k=0
    n=len(fcal.subcomponents)
    while i<0 and k<n+1:
        comp=fcal.subcomponents[k]
        if comp.name=="VEVENT":
            Id=comp.get('uid')
            if Id == key:
                i=k
        k+=1
        
    # On supprime l'événement du calendrier
    fcal.subcomponents.pop(i)
    
    # On ferme le fichier
    f.close()
    
    # On ouvre de nouveau le fichier, cette fois en mode écriture
    g=open(fichier,'wb')
    
    # On récupère dans le fichier toutes les informations du calendrier
    g.write(fcal.to_ical())
    
    # On ferme le fichier
    g.close()
