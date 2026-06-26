# Guide et Conventions pour les Agents (AGENTS.md)

Ce fichier définit le cadre technique, les conventions et les règles de conception à suivre lors de toute intervention sur ce projet.

## 1. Type de technologie

*   **Langage :** Python 3.11 minimum (compatible 3.12).
*   **Système de build / Packaging :** `setuptools` (défini dans `pyproject.toml`).
*   **Dépendances principales :**
    *   `jira` (API client Jira).
*   **Structure du projet :** Layout "src" standard.
    *   Le code source principal est dans `src/`.
    *   Les tests unitaires sont dans `tests/`.

## 2. Conventions de conception et de codage

### Architecture et Design Patterns
*   **POO (Programmation Orientée Objet) :** Utiliser correctement la POO pour structurer le code. Séparer les responsabilités dans des classes dédiées (ex: Client API, Parser de Configuration, Formateur de rapport).
*   **Design Patterns :** Appliquer les design patterns de manière pertinente quand cela résout un problème structurel ou améliore la maintenabilité (ex: Singleton pour des configurations partagées, Factory pour l'instanciation de modèles, etc.). Ne pas sur-ingénierier si ce n'est pas nécessaire.

### Optimisation et Bonnes Pratiques Python
*   **Opérateur Morse (Walrus `:=`) :** Préférer son utilisation pour éviter les calculs redondants ou les doubles recherches dans les dictionnaires (ex: combiné avec `dict.get()`).
*   **Mise en cache locale :** Dans les boucles, mettre en cache les recherches d'attributs fréquents en les assignant à des variables locales (ex: `assignee = issue.assignee` avant la boucle) pour réduire la surcharge de résolution.
*   **Concaténation :** Préférer les `f-strings` pour la concaténation de chaînes afin d'améliorer la lisibilité et les performances.
*   **Recherche de membres (`in`) :** Utiliser des `sets` (ensembles) constants au niveau du module (ex: `IN_PROGRESS_STATUSES`) pour les vérifications d'appartenance à l'intérieur des boucles, garantissant un temps de recherche en O(1).
*   **Logging :** Toujours envelopper les boucles ou traitements lourds utilisés uniquement pour le log de débogage dans une condition `if logger.isEnabledFor(logging.DEBUG):` pour éviter les coûts d'exécution (traversées O(N), allocations) lorsque le niveau de log est supérieur à DEBUG.

## 3. Conventions de Test

*   **Framework :** Utiliser le module standard `unittest`.
*   **Exécution :** Les tests doivent être exécutables depuis la racine du dépôt.
    *   Commande standard : `PYTHONPATH=. python -m unittest discover tests`
    *   *Note:* L'ajout de `PYTHONPATH=.` est indispensable si le package n'est pas installé via `pip install -e .` pour que les imports de type `from display_jira_tickets...` fonctionnent.
*   **Mocking :**
    *   Les appels réseau (via le client Jira) DOIVENT être mockés dans les tests unitaires. Le constructeur `JiraClient.__init__` initialise la connexion, donc `jira.JIRA` doit être mocké.
    *   *Environnements restreints :* Si la bibliothèque `jira` ne peut pas être installée, mocker explicitement le module en haut des tests ou via l'appel en ligne de commande :
        ```python
        import sys
        from unittest.mock import MagicMock
        sys.modules['jira'] = MagicMock()
        ```
        Exemple de commande de test robuste :
        `PYTHONPATH=. python -c "import sys; from unittest.mock import MagicMock; sys.modules['jira'] = MagicMock(); import unittest; unittest.main(module=None, argv=['unittest', 'discover', 'tests'])"`

## 4. Configuration

*   La configuration est gérée via un fichier `config.ini` à la racine (basé sur `config.ini.example`).
*   Ce fichier contient les identifiants Jira et les réglages spécifiques (filtres JQL, mapping de statuts).
