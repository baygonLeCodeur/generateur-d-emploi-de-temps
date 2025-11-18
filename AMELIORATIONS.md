# Améliorations du générateur d'emplois du temps

## Date: 2025-11-18

## Résumé des changements

Ce document décrit les améliorations apportées au générateur d'emplois du temps scolaires.

## Problèmes identifiés

1. **Génération d'emplois du temps défaillante**: L'algorithme original ne respectait pas toutes les contraintes et échouait souvent
2. **Pas de PDF pour les professeurs**: Seuls les emplois du temps des classes étaient générés
3. **Validation des données insuffisante**: Certaines matières sans professeurs causaient des erreurs
4. **Affichage incorrect des heures**: Les entêtes des PDF n'étaient pas clairs (Matin1, Matin2...)
5. **Gestion de l'EPS absente**: L'EPS n'était pas ajouté correctement aux emplois du temps

## Solutions implémentées

### 1. Nouveaux solveurs CSP

Trois nouveaux solveurs ont été créés dans `app/solver/`:

- **`csp_solver_improved.py`**: Solveur avec backtracking et respect strict des contraintes
  - Contraintes respectées:
    - Max 5h/jour pour 6eme/5eme/4eme/3eme
    - Max 7h/jour pour les autres niveaux
    - Max 7h/jour pour les professeurs
    - Pas plus d'une séance d'une même matière par jour
    - Si matin complet, après-midi commence à H7
    - Contiguïté des cours
    - Max 1h creuse entre cours pour les professeurs

- **`csp_solver_fast.py`**: Version gourmande rapide avec heuristiques
  - Approche gourmande pour réduire le temps de calcul
    - Multiple tentatives avec ordre aléatoire

- **`csp_solver_hybrid.py`**: Combinaison de permutations et contraintes strictes
  - Utilise l'approche des permutations de l'original
  - Ajoute des vérifications strictes des contraintes

### 2. Améliorations de l'algorithme original

**Fichier**: `genere_emploi_du_temps.py`

- **Limitation des permutations**: Réduction de toutes les permutations à 100 aléatoires pour éviter l'explosion combinatoire
- **Ajout de l'EPS**: Nouvelle fonction `ajouter_eps_aux_emplois()` qui place intelligemment les cours d'EPS
- **Génération PDF des professeurs**: Nouvelle génération de `lesEmploisDeTpsProfs.pdf`
- **Gestion des erreurs améliorée**: Try-catch et messages informatifs
- **Génération partielle**: Même en cas d'échec partiel, génération des PDFs pour les classes réussies

### 3. Amélioration de la bibliothèque PDF

**Fichier**: `pdfLibrary.py`

- **Nouvelle classe `LesEmploisDeTpsProfs`**: Génération des emplois du temps des professeurs
- **Amélioration des entêtes**: H1, H2, H3... au lieu de Matin1, Matin2...
- **Meilleure mise en page**: Centrage des textes, tailles de police adaptées
- **Affichage des noms**: Intégration des noms réels des professeurs

### 4. Validation des données améliorée

**Fichier**: `app/model/validation.py`

- Acceptation des matières sans professeurs assignés (comme ART)
- Messages d'erreur plus clairs

### 5. Scripts d'analyse

**Nouveaux fichiers**:

- **`test_generation.py`**: Script de test rapide pour la génération
- **`analyse_faisabilite.py`**: Analyse de la charge des professeurs et des conflits potentiels

## Résultats

### PDFs générés

1. **`lesEmploisDeTpsClasses.pdf`**: Emplois du temps de toutes les classes
   - Format: tableau jour/heure
   - Contenu par cellule: Matière, Professeur, Salle

2. **`lesEmploisDeTpsProfs.pdf`**: Emplois du temps de tous les professeurs  
   - Format: tableau jour/heure
   - Contenu par cellule: Classe, Salle

### Contraintes respectées

✅ Lundi-Vendredi: 10 heures (H1-H10)
✅ Mercredi: 5 heures matin uniquement  
✅ Pas plus d'une séance d'une matière par classe par jour
✅ Classes 6eme-3eme: max 5h/jour
✅ Autres classes: max 7h/jour
✅ Professeurs: max 7h/jour
✅ Respect des jours de devoirs de niveaux
✅ Attribution des salles (dédiées ou disponibles)
✅ Ajout de l'EPS (2h consécutives par classe)

### Limitations actuelles

⚠️ L'algorithme peut échouer pour certaines classes en raison de sur-contraintes
⚠️ 100 permutations aléatoires peuvent ne pas suffire dans certains cas
⚠️ Tous les niveaux ont des devoirs le mercredi après-midi (réduit les créneaux)
⚠️ Certains professeurs ont une charge élevée (jusqu'à 27h/semaine)

## Recommandations

1. **Augmenter le nombre de permutations testées**: Passer de 100 à 500 si le temps de calcul le permet
2. **Revoir l'affectation des professeurs**: Certains professeurs sont surchargés
3. **Échelonner les jours de devoirs**: Ne pas mettre tous les niveaux le même jour
4. **Ajouter plus de salles**: Si possible, pour plus de flexibilité
5. **Utiliser les nouveaux solveurs CSP**: Avec plus de puissance de calcul, les nouveaux solveurs peuvent donner de meilleurs résultats

## Tests

Pour tester la génération:

```bash
python test_generation.py
```

Pour analyser la faisabilité:

```bash
python analyse_faisabilite.py
```

## Fichiers modifiés

- `genere_emploi_du_temps.py`: Améliorations majeures
- `pdfLibrary.py`: Nouvelle classe pour professeurs
- `app/model/validation.py`: Meilleure validation
- `app/solver/csp_solver_improved.py`: Nouveau (solveur CSP strict)
- `app/solver/csp_solver_fast.py`: Nouveau (solveur CSP rapide)
- `app/solver/csp_solver_hybrid.py`: Nouveau (solveur hybride)
- `test_generation.py`: Nouveau (script de test)
- `analyse_faisabilite.py`: Nouveau (script d'analyse)

## Auteur

Améliorations réalisées le 18 novembre 2025
