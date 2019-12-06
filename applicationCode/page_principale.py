from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from applicationCode.auth import login_required #Windows
from applicationCode.db import get_db #Windows
from . import with_doodle #Windows
from . import envoi_mail #Windows
#import auth # MAC
#from auth import login_required # MAC
#import db #MAC
#from db import get_db #MAC
#import with_doodle #MAC
#import envoi_mail # MAC
import datetime
from datetime import *

# Variable globale contenant toutes les informations du sondage en cours
sondag = []
# Variable globale contenant la liste des calendriers pour le sondage en cours
selec_calendriers = []

bp = Blueprint('page_principale', __name__)

# Sur la page principale, on affiche les sondages en cours de l'utilisateur
@bp.route('/')
@login_required
def liste_sondages_calendriers():
    db = get_db()
    #On récupère les sondages de l'utilisateur dans la base de données
    sondages = db.execute(
        'SELECT * FROM sondage JOIN (SELECT sondage_key FROM sondage_user WHERE user_id = ?) sond ON sondage.key=sond.sondage_key',(g.user['id'],)
        ).fetchall()
    #On récupère les calendriers de l'utilisateur dans la base de données
    calendriers = db.execute(
        'SELECT * FROM calendrier JOIN (SELECT calendrier_id FROM calendrier_user WHERE user_id = ?) cal ON calendrier.id=cal.calendrier_id',(g.user['id'],)
         ).fetchall()
    cal_selec = db.execute(
        'SELECT * FROM sondage_calendrier WHERE user_id = ?',(g.user['id'],)
        ).fetchall()
    return render_template('liste_sondages_calendriers.html', sondages=sondages, calendriers=calendriers, cal_selec=cal_selec)



# L'utilisateur peut choisir d'ajouter un nouveau sondage
@bp.route('/ajouter_sondage', methods=('GET', 'POST'))
@login_required
def ajouter_sondage_key():
    error=None
    existanceCalendrier = False
    db = get_db()
    if request.method == 'POST':
        # On récupère la clé du sondage
        key = request.form['key']

        if not key:
            error = 'Veuillez entrer la clé du sondage.'
        #On vérifie que l'utilisateur n'a  pas déjà ajouté ce sondage
        elif db.execute( 
            'SELECT sondage_key FROM sondage_user WHERE sondage_key = ? AND user_id = ?', (key, g.user['id'])
        ).fetchone() is not None:
            error = 'Vous avez déjà ajouté le sondage {}.'.format(key)

        if error is not None:
            flash(error)
        else:
            nom_utilisateur= (db.execute(
                                    'SELECT nom_doodle FROM user WHERE id = ?', (g.user['id'],)
                                    ).fetchone())['nom_doodle']

            # On récupère la liste des calendriers de l'utilisateur
            liste_calendriers = db.execute(
                'SELECT * FROM calendrier JOIN (SELECT calendrier_id FROM calendrier_user WHERE user_id = ?) cal ON calendrier.id=cal.calendrier_id',(g.user['id'],)
                ).fetchall()

            return render_template('liste_calendriers.html', liste_calendriers=liste_calendriers,
                                   key=key, nom_utilisateur=nom_utilisateur)
            
    return render_template('ajouter_sondage.html')


# L'application présélectionne les créneaux où l'utilisateur est disponible
@bp.route('/<string:key>/<string:nom_utilisateur>/selec_creneaux', methods=('GET','POST',))
@login_required
def ajouter_sondage_selec_creneaux(key,nom_utilisateur):
    db = get_db()
    # On récupère l'adresse du fichier correspondant au calendrier demandé
    if request.method == 'POST':
        cal_ids= request.form

        # On récupère le nom des calendriers sélectionnés
        for cal_id in cal_ids:
            cal = db.execute(
                    'SELECT calendrier_nom FROM calendrier WHERE id = ?', (cal_id,)
                    ).fetchone()['calendrier_nom']
            selec_calendriers.append(cal)
        #print("CALENDRIERS : ",selec_calendriers)
        # On récupère la liste des calendriers de l'utilisateur
        liste_calendriers = db.execute(
            'SELECT * FROM calendrier JOIN (SELECT calendrier_id FROM calendrier_user WHERE user_id = ?) cal ON calendrier.id=cal.calendrier_id',(g.user['id'],)
            ).fetchall()

        # On récupère les créneaux du sondage où l'utilisateur est libre et on les ajoute à la base de données
        sond = with_doodle.recup_creneau(key,nom_utilisateur,liste_calendriers)

        # On complète la liste sondag
        sondag.append(sond[0])
        sondag.append(sond[1])
        sondag.append(sond[2])
        sondag.append(sond[3])
        sondag.append(sond[4])
        sondag.append(sond[5])
        sondag.append(sond[6])
        sondag.append(sond[7])
        sondag.append(sond[8])
        sondag.append(sond[9])
        creneaux = db.execute(
            'SELECT * FROM creneau JOIN creneau_sondage ON id=creneau_id  WHERE sondage_key = ? AND user_id = ?',(key,g.user['id'])
            ).fetchall()
        return render_template('liste_creneaux.html', creneaux=creneaux,key=key,id=g.user['id'],nom_utilisateur=nom_utilisateur,
                           type="ajout",jour_entier=str(sondag[6]),limiteVotePer=str(sond[8]),siNecessaire=str(sond[9]))
    return render_template('liste_calendriers.html', liste_calendriers=liste_calendriers, key=key, nom_utilisateur=nom_utilisateur)
 

# Permet de ne conserver que les créneaux choisis par l'utilisateur
@bp.route('/<string:key>/<int:id>/<string:nom_utilisateur>/<string:type>/<string:jour_entier>/<string:limiteVotePer>/<string:siNecessaire>/modif_creneaux/', methods=('GET','POST',))
@login_required
def ajouter_sondage_modif_creneaux(key,id,nom_utilisateur,type,jour_entier,limiteVotePer,siNecessaire):
    preferences= sondag[1]
    j=0
    n=0
    # On compte combien de créneaux ont été préselectionnés
    for nombre in preferences: 
        if nombre!=0:
            n=n+1
    l=[0 for i in range (0,len(preferences))] 
    
    # On met la même clé (au hasard)
    participant_key = "et5qinsv"
    
    db = get_db()
    creneaux = db.execute(
            'SELECT * FROM creneau JOIN creneau_sondage ON id=creneau_id  WHERE sondage_key = ? AND user_id = ?',(key,g.user['id'])
            ).fetchall()
    
    if request.method == 'POST':
        # On récupère les indices (dans la liste preferences) des créneaux que l'utilisateur a choisi
        val1= request.form
        print(len(val1))
        if siNecessaire=='False' and len(val1)>sondag[8]:
            error = 'Vous avez voté pour trop de créneaux'
            flash(error)
            return render_template('liste_creneaux.html', creneaux=creneaux,key=key,id=id,nom_utilisateur=nom_utilisateur,
                                   type=type,jour_entier=jour_entier,limiteVotePer=sondag[8],siNecessaire=siNecessaire)
        # On parcourt la liste des indices
        for k in val1:
            if siNecessaire == 'False':
                l[int(k)]=1
            # Si le sondage possède l'option 'si Necessaire' l'utilisateur a deux checkbox par créneau
            else:
                # 'O' correspond au cas où l'utilisateur indique qu'il sera présent sans condition
                if k[0]=='O':
                    l[int(k[1])]=2
                # 'S' correspond au cas où l'utilisateur indique qu'il sera présent si nécessaire
                elif k[0]=='S':
                    if l[int(k[1])]==2:
                        error = 'Vous avez voté deux fois pour le même créneau'
                        flash(error)
                        return render_template('liste_creneaux.html', creneaux=creneaux,key=key,id=id,nom_utilisateur=nom_utilisateur,
                                   type=type,jour_entier=jour_entier,limiteVotePer=sondag[8],siNecessaire=siNecessaire)
                    l[int(k[1])]=1
                    
    # On récupère la liste de créneaux préselectionnés
    eventdate=sondag[0].copy()
    
    # Si le sondage n'est pas sur un jour entier
    if not (sondag[6]): 
        for i in range (len(l)-1,-1,-1):
            if preferences[i]==1 or preferences[i]==2:
                j=j+1
                # On retire les créneaux que l'utilisateur n'a pas sélectionné
                if (l[i]!=preferences[i] and not(siNecessaire and l[i]==1)):
                    eventdate.pop((n-j)*2+1) # Correspond à l'heure de fin
                    eventdate.pop((n-j)*2) # Correspond à l'heure de début
    #Si le sondage est sur un jour entier
    else: 
        for i in range (len(l)-1,-1,-1):
            # On retire les créneaux que l'utilisateur n'a pas sélectionné
            if preferences[i]==1 or preferences[i]==2:
                j=j+1
                if (l[i]!=preferences[i] and not(siNecessaire and l[i]==1)):
                    eventdate.pop((n-j))
                    
    # On convertit au bon format pour remplir le sondage Doodle puis on le remplit
    eventdate2 = with_doodle.conversion(eventdate,sondag[3],sondag[4],sondag[5], sondag[6]) 
    with_doodle.remplissage_doodle(l,sondag[2],key,nom_utilisateur,participant_key)
    
    creneau_reserve=""
    # On remplit le(s) calendrier(s) avec les créneaux:
    for cal_nom in selec_calendriers:
        calendrier = (db.execute(
                                'SELECT calendrier_fichier FROM calendrier WHERE calendrier_nom = ?', (cal_nom,)
                                ).fetchone())['calendrier_fichier']
        creneau_reserve=str(with_doodle.reserve_creneaux(eventdate2,sondag[6],key,sondag[7],calendrier))
        
    date=datetime.now().date()
    
    # S'il s'agit d'ajouter un sondage, on l'ajoute dans la base de données
    if (type=="ajout"):
        db.execute(
            'INSERT INTO sondage (key, titre, lieu, description,liste_options,date_maj,date_entree,est_final)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (key, sondag[3], sondag[4], sondag[5], creneau_reserve, date, date, sondag[7])
        )
        db.execute(
            'INSERT INTO sondage_user (sondage_key, user_id)'
            ' VALUES (?, ?)',
        (key, id)
        )
        for nom in selec_calendriers:
            db.execute(
            'INSERT INTO sondage_calendrier (sondage_key, calendrier_nom, user_id)'
            ' VALUES (?, ?, ?)',
            (key, nom, id)
            )
        
    # S'il s'agit de mettre à jour un sondage, on fait juste une mise à jour de la base de données
    elif (type=="maj"):
        db.execute(
                'UPDATE sondage SET liste_options = ?, date_maj = ?, est_final = ?'
                ' WHERE key = ?',
                (creneau_reserve, date, sondag[7], key)
            )   
    db.commit()
    sondag.clear()
    selec_calendriers.clear()
    return redirect(url_for('page_principale'))


# L'utilisateur peut mettre à jour ses sondages afin d'actualiser les changements qu'il y aurait pu avoir, ou de voir s'il est final
@bp.route('/<string:key>/<int:id>/<string:nom_utilisateur>/mise_a_jour_sondage', methods=('POST',))
@login_required
def mise_a_jour_sondage(key,id,nom_utilisateur):

    # On met la même clé (au hasard)
    participant_key = "et5qinsv"
    sondag.clear()
    db = get_db()

    # On récupère les créneaux du sondage
    eventdate = (db.execute(
                            'SELECT liste_options FROM sondage WHERE key = ?', (key,)
                            ).fetchone())['liste_options']
    # On récupère la liste des calendriers de l'utilisateur ainsi que le calendrier à compléter
    liste_calendriers = (db.execute(
                            'SELECT * FROM calendrier JOIN (SELECT calendrier_id FROM calendrier_user WHERE user_id = ?) cal ON calendrier.id=cal.calendrier_id',(g.user['id'],)
                             ).fetchall())
    calendriers = (db.execute(
                            'SELECT calendrier_nom FROM sondage_calendrier WHERE sondage_key = ? AND user_id = ?', (key,g.user['id'])
                            ).fetchall())
    numCal=0
    for i in range(len(calendriers)):
        cal_nom = calendriers[i]['calendrier_nom']
        selec_calendriers.append(cal_nom)
        calendrier = (db.execute(
                                'SELECT calendrier_fichier FROM calendrier WHERE calendrier_nom = ?', (cal_nom,)
                                ).fetchone())['calendrier_fichier']
        # On supprime ensuite les événements correspondant dans le calendrier
        numCal=numCal+1
        with_doodle.efface(eventdate, key, nom_utilisateur, calendrier, numCal)

    # On commence par supprimer des tables creneau et creneau_sondage les anciens créneaux préselectionnés
    db.execute('DELETE FROM creneau WHERE id IN (SELECT creneau_id FROM creneau_sondage WHERE sondage_key = ? AND user_id = ?)', (key,g.user['id']))
    db.execute('DELETE FROM creneau_sondage WHERE sondage_key =? AND user_id = ?', (key,g.user['id']))
    db.commit()

    # On récupère les créneaux où l'utilisateur est libre
    sond=with_doodle.recup_creneau(key, nom_utilisateur, liste_calendriers)

    # On complète la liste sondag
    sondag.append(sond[0])
    sondag.append(sond[1])
    sondag.append(sond[2])
    sondag.append(sond[3])
    sondag.append(sond[4])
    sondag.append(sond[5])
    sondag.append(sond[6])
    sondag.append(sond[7])
    sondag.append(sond[8])
    sondag.append(sond[9])  
    creneaux = db.execute(
                    'SELECT * FROM creneau JOIN creneau_sondage ON id=creneau_id  WHERE sondage_key = ? AND user_id = ?', (key,g.user['id'])
                    ).fetchall()
    return render_template('liste_creneaux.html', creneaux=creneaux,key=key,id=id,nom_utilisateur=nom_utilisateur,
                           type="maj",jour_entier=str(sondag[6]),limiteVotePer=sondag[8],siNecessaire=str(sond[9]))


# L'utilisateur peut supprimer ses sondages s'il le souhaite
@bp.route('/<string:key>/<string:nom_utilisateur>/supprimer_sondage', methods=('POST',))
@login_required
def supprimer_sondage(key, nom_utilisateur):
    db = get_db()
    # On récupère les créneaux du sondage
    eventdate = (db.execute(
                            'SELECT liste_options FROM sondage WHERE key = ?', (key,)
                            ).fetchone())['liste_options']
    # On récupère le(s) calendrier(s)  complété(s)
    calendriers = (db.execute(
                            'SELECT calendrier_nom FROM sondage_calendrier WHERE sondage_key = ? AND user_id = ?', (key,g.user['id'])
                            ).fetchall())
    numCal=0
    # On efface les créneaux réservés par le sondage dans les calendriers et on supprime la participation dans le sondage Doodle
    for i in range(len(calendriers)):
        cal_nom = calendriers[i]['calendrier_nom']
        calendrier = (db.execute(
                                'SELECT calendrier_fichier FROM calendrier WHERE calendrier_nom = ?', (cal_nom,)
                                ).fetchone())['calendrier_fichier']
        numCal=numCal+1
        with_doodle.efface(eventdate, key, nom_utilisateur, calendrier, numCal)
    #On supprime le sondage dans la base de données
    db.execute('DELETE FROM creneau WHERE id IN (SELECT creneau_id FROM creneau_sondage WHERE sondage_key = ? AND user_id = ?)', (key,g.user['id']))
    db.execute('DELETE FROM creneau_sondage WHERE sondage_key =? AND user_id = ?', (key,g.user['id']))
    db.execute('DELETE FROM sondage_calendrier WHERE sondage_key =? AND user_id = ?', (key,g.user['id']))
    db.execute('DELETE FROM sondage WHERE key IN (SELECT sondage_key FROM sondage_user WHERE sondage_key = ? AND user_id = ?)', (key,g.user['id']))
    db.execute('DELETE FROM sondage_user WHERE sondage_key = ? AND user_id = ?', (key,g.user['id']))
    db.commit()
    return redirect(url_for('page_principale'))
    

# L'utilisateur peut choisir d'ajouter un nouveau calendrier
@bp.route('/liste_sondages_calendriers', methods=('GET', 'POST'))
@login_required
def ajouter_calendrier():
    error=None
    db = get_db()
    if request.method == 'POST':
        # On récupère l'adresse du fichier contenant le calendrier
        fichier = request.form['calendrier_fichier']

        # On vérifie que l'utilisateur a bien rentré l'adresse et qu'il n'a pas déjà ajouté ce calendrier
        if not fichier:
            error = 'Veuillez entrer le fichier.'
        elif db.execute(
            'SELECT calendrier_fichier FROM calendrier JOIN (SELECT * FROM calendrier_user WHERE user_id = ?) cal ON calendrier.id=cal.calendrier_id WHERE calendrier_fichier = ?',
            (g.user['id'],fichier,)).fetchone() is not None:
            error = 'Le calendrier {} existe déjà.'.format(fichier)
        try:
            with open(fichier): pass
        except IOError:
            error = "Ce fichier n'existe pas."
            
        if error is not None:
            flash(error)
        else:
            # On récupère le nom du calendrier
            nom = request.form['calendrier_nom']
            # On vérifie que l'utilisateur a bien rentré le nom et qu'il n'a pas déjà nommé un de ses calendriers de la même façon
            if not nom:
                error = 'Veuillez entrer un nom pour le calendrier.'
            elif db.execute(
                'SELECT calendrier_nom FROM calendrier JOIN (SELECT * FROM calendrier_user WHERE user_id = ?) cal ON calendrier.id=cal.calendrier_id WHERE calendrier_nom = ?',
                (g.user['id'],nom,)).fetchone() is not None:
                error = 'Ce nom de calendrier : "{}" existe déjà.'.format(nom)

            if error is not None:
                flash(error)
            else:
                # On récupère la possible description qu'il a donné à son calendrier
                descr = request.form['description']

                # On met à jour la base de données en complétant les tables calendrier et calendrier_user
                db.execute(
                    'INSERT INTO calendrier (calendrier_nom,calendrier_fichier,description)'
                    ' VALUES (?, ?, ?)',
                    (nom,fichier,descr)
                )
                id_calendrier= (db.execute(
                                    'SELECT id FROM calendrier WHERE calendrier_fichier = ?',
                                    (fichier,)).fetchone()['id'])
                db.execute(
                    'INSERT INTO calendrier_user (calendrier_id, user_id)'
                    ' VALUES (?, ?)',
                    (id_calendrier,g.user['id'])
                )
                db.commit()
                return redirect(url_for('page_principale'))

    return render_template('ajouter_calendrier.html')


# L'utilisateur peut supprimer ses calendriers s'il le souhaite
@bp.route('/<int:calendrier_id>/supprimer_calendrier', methods=('POST',))
@login_required
def supprimer_calendrier(calendrier_id):
    db = get_db()
    db.execute(
        'DELETE FROM calendrier WHERE id = ?',(calendrier_id,)
    )
    db.execute(
        'DELETE FROM calendrier_user WHERE calendrier_id = ?', (calendrier_id,)
    )
    db.commit()
    return redirect(url_for('page_principale'))


@bp.route('/parametres')
@login_required
def parametres():
    db = get_db()
    return render_template('parametres.html', username=g.user['username'], nom_doodle=g.user['nom_doodle'], mail=g.user['mail'])
    

@bp.route('/<string:username>/<string:nom_doodle>/<string:mail>/modif_nom_doodle', methods=('GET', 'POST'))
@login_required
def modif_nom_doodle(username, nom_doodle, mail):
    error=None
    db = get_db()
    if request.method == 'POST':
        nom_doodle = request.form['nom_doodle']
        
        if not nom_doodle:
            error = 'Veuillez entrer un nom pour le remplissage des sondages Doodle.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE user SET nom_doodle = ?'
                ' WHERE id = ?',
                (nom_doodle, g.user['id'])
            )   
            db.commit()
            return render_template('parametres.html', username=username, nom_doodle=nom_doodle, mail=mail)
    return render_template('modif_nom_doodle.html')


@bp.route('/<string:username>/<string:nom_doodle>/<string:mail>/modif_mot_de_passe', methods=('GET', 'POST'))
@login_required
def modif_mot_de_passe(username, nom_doodle, mail):
    error=None
    db = get_db()
    if request.method == 'POST':
        ancien_mdp = request.form['mot_de_passe_0']
        mdp = generate_password_hash(request.form['mot_de_passe_1'])
        mdp_bis = request.form['mot_de_passe_2']
        print(check_password_hash(mdp, mdp_bis))

        if not check_password_hash(g.user['password'], ancien_mdp):
            error = 'Mot de passe incorrect.'
        elif not mdp:
            error = 'Veuillez entrer un mot de passe.'
        elif not mdp_bis:
            error = 'Veuillez entrer un mot de passe dans les deux champs.'
        elif not check_password_hash(mdp, mdp_bis):
            error = 'Veuillez entrer le même mot de passe dans les deux champs.'
        

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE user SET password = ?'
                ' WHERE id = ?',
                (mdp, g.user['id'])
            )   
            db.commit()
            return render_template('parametres.html', username=username, nom_doodle=nom_doodle, mail=mail)
    return render_template('modif_mot_de_passe.html')


@bp.route('/<string:username>/<string:nom_doodle>/<string:mail>/modif_mail', methods=('GET', 'POST'))
@login_required
def modif_mail(username, nom_doodle, mail):
    error=None
    db = get_db()
    if request.method == 'POST':
        mail = request.form['mail']
        
        if not mail:
            error = 'Veuillez entrer une adresse mail.'
        elif not envoi_mail.verif_mail(mail):
            error = 'Veuillez entrer une adresse mail valide.'

        if error is not None:
            flash(error)
        else:
            code = envoi_mail.code_verification(mail)
            return render_template('verification_mail.html', username=username, nom_doodle=nom_doodle, mail=mail, code=code)
    return render_template('modif_mail.html')


@bp.route('/<string:username>/<string:nom_doodle>/<string:mail>/<string:code>/verification_code', methods=('GET', 'POST'))
@login_required
def verification_code(username, nom_doodle, mail, code):
    db = get_db()
    error = None
    # On récupère le code de vérification
    if request.method == 'POST':
        code_verif= request.form['code_verif']

        if code_verif is None:
            error = "Veuillez rentrer le code de vérification"
        elif code != code_verif:
            error = "Le code est erroné"

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE user SET mail = ?'
                ' WHERE id = ?',
                (mail, g.user['id'])
            )   
            db.commit()
            return render_template('parametres.html', username=username, nom_doodle=nom_doodle, mail=mail)
    return render_template('verification_code.html')






