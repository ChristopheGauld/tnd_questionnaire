# myHCL TND - application questionnaire

Prototype Django pour administrer le questionnaire myHCL TND, recueillir les réponses par lien public et exporter les données en `.xlsx`.

## Démarrage local

```bash
cd "/Users/christophe/Desktop/HP Psy France/Data/tnd_questionnaire"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py import_myhcl_docx --reset
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

## Adresses

- Tableau de bord : http://127.0.0.1:8000/
- Administration Django : http://127.0.0.1:8000/admin/
- Le lien public du questionnaire est affiché dans le tableau de bord.

## Import du document Word

Le questionnaire est importé depuis :

```text
/Users/christophe/Desktop/Assos et Orga/FIND TND/myHCL TND/myHCL_TND.docx
```

Pour réimporter après modification du Word :

```bash
.venv/bin/python manage.py import_myhcl_docx --reset
```

## Export

Le bouton `Télécharger Excel` du tableau de bord produit un fichier `.xlsx` avec :

- une ligne par répondant ;
- une colonne par question ;
- les dates de début et de fin ;
- l'identifiant participant si renseigné.

## Mise en ligne

Le projet est préparé pour Render avec `render.yaml`, `build.sh`, Gunicorn, WhiteNoise et PostgreSQL.

Étapes :

1. Publier ce dossier dans un dépôt GitHub.
2. Créer un Blueprint Render depuis ce dépôt.
3. Attendre le build : migrations, fichiers statiques et questionnaire myHCL TND sont chargés automatiquement.
4. Créer le compte admin dans le Shell Render :

```bash
python manage.py createsuperuser
```

5. Récupérer l'URL `.onrender.com` dans Render et diffuser le lien public du questionnaire.

L'URL admin est définie par `DJANGO_ADMIN_URL`. Par défaut, elle vaut `admin-prive/`, donc l'administration sera accessible à `/admin-prive/` après connexion.

Pour un vrai usage clinique ou recherche, il faudra ajouter avant diffusion :

- hébergement conforme RGPD/HDS selon le contexte ;
- `DJANGO_SECRET_KEY` robuste ;
- `DEBUG=False` ;
- `DJANGO_ALLOWED_HOSTS` avec le domaine de production ;
- HTTPS ;
- politique de consentement et durée de conservation ;
- comptes admin nominatifs et mots de passe forts.
