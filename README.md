# Krystal Elec

Application desktop Windows en Python avec CustomTkinter et SQLite pour Krystal Elec.

## Protection des donnees

L'application enregistre maintenant les donnees dans le profil Windows de l'utilisateur:

- Base locale: `%APPDATA%\\CrystalElec\\data\\elecflow.db`
- Backups locaux: `%APPDATA%\\CrystalElec\\backups`
- Exports PDF: `%APPDATA%\\CrystalElec\\exports`

Au demarrage, si une ancienne base existe dans `data/elecflow.db` (racine projet), elle est migree automatiquement vers `%APPDATA%`.

### Backups automatiques

- Un backup est cree au demarrage.
- Les modifications CRUD (clients, devis, rendez-vous, catalogue) declenchent des backups periodiques.
- Variables optionnelles:
  - `CRYSTALELEC_BACKUP_INTERVAL_MINUTES` (defaut: `5`)
  - `CRYSTALELEC_BACKUP_KEEP` (defaut: `50`)

### Cloud (optionnel)

Deux modes sont supportes:

1. Supabase Storage
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY` (ou `SUPABASE_ANON_KEY`)
   - `SUPABASE_BACKUP_BUCKET` (defaut: `crystalelec-backups`)

2. Webhook custom
   - `CRYSTALELEC_BACKUP_WEBHOOK_URL`

Si aucune variable cloud n'est definie, l'application reste en mode local + backups locaux.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

## Livraison .exe et donnees de test

Les donnees ne sont plus stockees dans le dossier du projet mais dans `%APPDATA%\\CrystalElec`.

- Si tu envoies uniquement l'exe, ton client ne recevra pas tes anciennes donnees de test.
- Ne joins pas manuellement ton `%APPDATA%\\CrystalElec\\data\\elecflow.db` de developpement dans le package de livraison.
