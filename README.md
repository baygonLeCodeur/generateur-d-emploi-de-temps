Generateur d'emploi du temps (EDT)
=================================

But
----
Petit projet Python pour générer automatiquement des emplois du temps scolaires et les exporter en PDF.

Organisation
------------
- `main_program.py` : point d'entrée historique (maintenu). Le projet offre maintenant un petit wrapper MVC dans `app/` : `app.controller` pour démarrer l'application.
- `genere_emploi_du_temps.py`, `les_dependances.py` : logique métier principale.
- `mes_dictionnaires.py`, `matieres_seances.json` : données et structures partagées.
- `pdfLibrary.py` : génération PDF.

Exécution
---------
1. Installer dépendances :

```bash
python -m pip install -r requirements.txt
```

2. Lancer l'interface graphique :

```bash
python main_program.py
```

3. Lancer un test headless (sans UI) :

```bash
python run_headless.py
```
Utiliser un environnement virtuel
--------------------------------
Pour créer et activer un environnement virtuel (recommandé) :

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux / zsh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Exécuter la suite de tests dans le venv :

```bash
pytest -q
```

Si tu utilises VS Code, ouvre le dossier du projet après avoir activé le venv, ou utilise la configuration fournie dans `.vscode/settings.json` qui pointe vers `.venv/bin/python`. Cela aidera Pylance à résoudre les imports comme `pytest`.


Fichiers ajoutés
-----------------
- `app/` : structure légère MVC (`model`, `view`, `controller`) pour faciliter la refactorisation.
- `run_headless.py` : script de test minimal pour exécuter le moteur sans UI.
