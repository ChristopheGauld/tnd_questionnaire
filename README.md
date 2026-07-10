# TND - questionnaire Streamlit

Application Streamlit pour diffuser le questionnaire TND par lien public.

## Déploiement Streamlit Cloud

Dans Streamlit Community Cloud :

1. Choisir le dépôt GitHub `ChristopheGauld/tnd_questionnaire`.
2. Choisir la branche `main`.
3. Choisir le fichier principal `streamlit_app.py`.
4. Ajouter les secrets.
5. Déployer.

Secrets minimaux :

```toml
ADMIN_PASSWORD = "mot-de-passe-a-changer"
```

Secrets Google Sheets pour conserver les réponses en ligne :

```toml
GOOGLE_SHEET_ID = "id-du-google-sheet"

[google_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

Partager ensuite le Google Sheet avec le `client_email` du compte de service en droit édition.

## Accès

- Questionnaire public : URL Streamlit normale.
- Administration : ajouter `?mode=admin` à la fin de l'URL.

Sans Google Sheets configuré, les réponses ne sont sauvegardées qu'en local pour les tests.

## Lancement local

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/streamlit run streamlit_app.py
```

## Fichiers principaux

- `streamlit_app.py` : application Streamlit.
- `questionnaire_data.json` : contenu du questionnaire.
- `requirements.txt` : dépendances Streamlit Cloud.
- `.streamlit/config.toml` : thème visuel.

## Note données sensibles

Pour un usage médical/recherche réel, vérifier le cadre RGPD, le consentement, la durée de conservation, les accès au Google Sheet et l'hébergement avant diffusion large.
