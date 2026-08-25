# myHCL TND sur Formbricks

Ce dépôt transforme `myHCL_TND_courte_FORMBRICKS.docx` en un questionnaire
parent compatible avec la version stable actuelle de Formbricks.

## Ce qui est inclus

- 255 questions logiques réparties en 19 sections ;
- toutes les questions sont obligatoires ;
- une réponse est exigée pour chaque ligne des matrices ;
- les formulations à la première personne ont été adaptées pour que le parent
  réponde au sujet de son enfant ;
- les mentions « À remplir par le parent » ont été retirées ;
- chaque section utilise le bouton « Enregistrer et continuer » ;
- Formbricks conserve une réponse partielle après chaque section ;
- le lien public active aussi la reprise locale pendant 24 heures sur le même
  appareil et dans le même navigateur.

## Créer le questionnaire en ligne

1. Créer un espace sur [Formbricks Cloud](https://app.formbricks.com).
2. Dans les paramètres de l'organisation, ouvrir **API Keys** et créer une clé
   avec un accès en écriture au workspace concerné.
3. Créer le questionnaire en brouillon avec la commande suivante :

```bash
python3 scripts/create_survey.py --upload
```

La commande demande la clé dans le terminal sans l'afficher. Elle vérifie la
clé, détecte automatiquement le workspace et crée le questionnaire en
brouillon. La clé n'est pas enregistrée.

Après relecture dans l'interface d'administration, publier le questionnaire
depuis Formbricks. Le lien public doit conserver `?offlineSupport=true` pour
activer la reprise de progression.

Pour une utilisation automatisée, les variables facultatives
`FORMBRICKS_API_KEY` et `FORMBRICKS_WORKSPACE_ID` restent prises en charge.

## Générer et contrôler le JSON

```bash
python3 scripts/create_survey.py --output formbricks_survey.json
python3 -m unittest discover -s tests -v
```

Le JSON généré utilise un workspace fictif tant que `FORMBRICKS_WORKSPACE_ID`
n'est pas défini. Ne pas l'envoyer tel quel à l'API.

## Accès et données

Le lien du questionnaire est public. L'administration et les résultats restent
derrière le compte Formbricks. Le champ caché `participant_id` permet d'ajouter
un identifiant dans le lien, par exemple :

`https://app.formbricks.com/s/ID_DU_QUESTIONNAIRE?offlineSupport=true&participant_id=P001`

Avant une diffusion clinique ou de recherche, vérifier la base légale, le
consentement, l'information des participants, la durée de conservation, les
droits d'accès et les licences des échelles. Transformer une échelle
auto-rapportée en hétéro-questionnaire peut modifier ses propriétés
psychométriques ; les formulations adaptées doivent donc être validées par
l'équipe clinique ou scientifique.
