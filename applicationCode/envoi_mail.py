## Importation des modules
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import re

import random
import string

def verif_mail(ch):
    """verifie la syntaxe d'une adresse mail donnée sous forme de chaine"""
    # extraction de l'adresse même dans le cas 'yyyyy <xxxx@xxxx.xxx>' 
    motif = r"^[^<>]*<([^<>]+)>$|(^[^<>]+$)"
    a = re.findall(motif, ch.strip())
    if len(a)>0:
        adr = ''.join(a[0]).strip()
    else:
        adr = ''
    # vérification de syntaxe de l'adresse mail extraite
    if adr=='':
        return False
    else:
        motif = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"
        return re.match(motif, adr)!=None


def code_verification(mail):
    code = ""
    for i in range(4):
        j=random.randint(0,9)
        code += str (j)
    ##  Spécification de l'expéditeur
    Fromadd = "achille.brad.pitt@gmail.com"
    ##  Spécification des destinataires
    Toadd = mail
    ## Spécification des destinataires en copie carbone (cas de plusieurs destinataires)
    cc = []
    ## Spécification du destinataire en copie cachée (en copie cachée)
    #bcc = "judithla30@gmail.com"
    bcc = ""
    ## Création de l'objet "message"
    message = MIMEMultipart()
    ## Spécification de l'expéditeur
    message['From'] = Fromadd
    ## Attache du destinataire à l'objet "message"
    message['To'] = Toadd
    ## Attache des destinataires en copie carbone à l'objet "message" (cas de plusieurs destinataires)
    message['CC'] = ",".join(cc)
    ## Attache du destinataire en copie cachée à l'objet "message"
    message['BCC'] = bcc
    ## Spécification de l'objet de votre mail
    message['Subject'] = "Vérification mail SyncPlanCal"
    ## Message à envoyer
    msg = "Voici le code de vérification : " + code
    ## Attache du message à l'objet "message", et encodage en UTF-8
    message.attach(MIMEText(msg.encode('utf-8'), 'plain', 'utf-8'))
     
    serveur = smtplib.SMTP('smtp.gmail.com', 587)    ## Connexion au serveur sortant (en précisant son nom et son port)
    serveur.starttls()    ## Spécification de la sécurisation
    serveur.login(Fromadd, "syncplancal")    ## Authentification
    texte= message.as_string().encode('utf-8')    ## Conversion de l'objet "message" en chaine de caractère et encodage en UTF-8
    Toadds = [Toadd] + cc + [bcc]    ## Rassemblement des destinataires
    serveur.sendmail(Fromadd, Toadds, texte)    ## Envoi du mail
    serveur.quit()    ## Déconnexion du serveur
    return code


def getPassword(length):
    password = ""
    s1 = string.printable
    s2 = string.punctuation
    s3 = string.whitespace
    i = 0
    while i<8 :
        r = random.choice(s1)
        if r not in s2 and r not in s3:
            password += r
            i+= 1
    return password


def mot_de_passe_oublie(mail,nom_utilisateur):
    mdp = getPassword(8)
    ##  Spécification de l'expéditeur
    Fromadd = "achille.brad.pitt@gmail.com"
    ##  Spécification des destinataires
    Toadd = mail
    ## Spécification des destinataires en copie carbone (cas de plusieurs destinataires)
    cc = []
    ## Spécification du destinataire en copie cachée (en copie cachée)
    #bcc = "judithla30@gmail.com"
    bcc = ""
    ## Création de l'objet "message"
    message = MIMEMultipart()
    ## Spécification de l'expéditeur
    message['From'] = Fromadd
    ## Attache du destinataire à l'objet "message"
    message['To'] = Toadd
    ## Attache des destinataires en copie carbone à l'objet "message" (cas de plusieurs destinataires)
    message['CC'] = ",".join(cc)
    ## Attache du destinataire en copie cachée à l'objet "message"
    message['BCC'] = bcc
    ## Spécification de l'objet de votre mail
    message['Subject'] = "Identifiants SyncPlanCal oubliés"
    ## Message à envoyer
    msg = "Votre nom d'utilisateur est '" + nom_utilisateur + "' et votre nouveau mot de passe est '" + mdp + "'."
    ## Attache du message à l'objet "message", et encodage en UTF-8
    message.attach(MIMEText(msg.encode('utf-8'), 'plain', 'utf-8'))
     
    serveur = smtplib.SMTP('smtp.gmail.com', 587)    ## Connexion au serveur sortant (en précisant son nom et son port)
    serveur.starttls()    ## Spécification de la sécurisation
    serveur.login(Fromadd, "syncplancal")    ## Authentification
    texte= message.as_string().encode('utf-8')    ## Conversion de l'objet "message" en chaine de caractère et encodage en UTF-8
    Toadds = [Toadd] + cc + [bcc]    ## Rassemblement des destinataires
    serveur.sendmail(Fromadd, Toadds, texte)    ## Envoi du mail
    serveur.quit()    ## Déconnexion du serveur
    return mdp



