# Guide d'utilisation : Configuration .ini pour exécuter le script Python
Ce script Python utilise un fichier de configuration au format `.ini` afin d'accéder aux paramètres nécessaires pour se connecter à une instance Jira et manipuler ses données. Ce fichier `.ini` doit contenir les informations d'identification et autres paramètres Jira nécessaires.

## Étapes pour configurer et exécuter le script

### 1. Préparation de votre environnement

Assurez-vous que Python (version 3.12 ou supérieure) est installé sur votre machine. Vous pouvez le télécharger à partir de [python.org](https://www.python.org/).

Nous utilisons **uv** pour gérer les dépendances et l'exécution du projet de manière rapide et isolée. Installez `uv` en suivant la documentation officielle ou via `curl -LsSf https://astral.sh/uv/install.sh | sh` (ou `pip install uv`).

### 2. Installation des dépendances

1. Clonez ou téléchargez le dépôt du projet :
   ```bash
   git clone https://github.com/Sorondare/DisplayJiraTickets
   cd DisplayJiraTickets
   ```
2. Installez les dépendances et préparez l'environnement avec `uv` :
   ```bash
   uv sync
   ```

### 3. Création et configuration du fichier `.ini`

1.  Créez un fichier `config.ini` à la racine du projet. Vous pouvez vous baser sur le fichier `config.ini.example` fourni.
2.  Remplissez-le avec vos informations.

Le fichier `.ini` doit contenir une section `[Jira]` avec les clés suivantes :
- **`server`** : l'URL du serveur Jira auquel se connecter.
- **`username`** : le nom d'utilisateur de l'instance Jira.
- **`api_token`** : le jeton de l'API Jira associé au compte utilisateur indiqué.
- **`project_key`** : la clef du projet Jira (par exemple "PROJ").

Voici un exemple de structure correcte d'un fichier `.ini` :

```ini
[Jira]
server = <host url>
username = <username>
api_token = <api token>
language = <jira displayed language (default: en)>
project_key = <project key>

[Report]
username = <jira username used in issues>
introduction = <introduction to the ticket list output>

[Logging]
level = INFO
```

#### Initialisation automatique du mapping des statuts
Pour faciliter la configuration du mapping des statuts Jira, vous pouvez utiliser l'argument `--init`. Cette commande va :
1. Se connecter à Jira en utilisant les informations de la section `[Jira]` de votre `config.ini`.
2. Récupérer tous les statuts disponibles pour le projet spécifié par `project_key` et les injecter (ou compléter) dans la section `[StatusMapping]` de votre `config.ini`.

Pour utiliser cette fonctionnalité, lancez la commande :
```bash
uv run display-daily-tickets --init
```

Une fois l'initialisation terminée, ouvrez votre `config.ini`. Vous y trouverez la section `[StatusMapping]`. Vous devez alors **manuellement** modifier les valeurs pour qu'elles correspondent aux statuts internes du script. Les valeurs possibles sont :
- `TO_DO`
- `IN_PROGRESS`
- `TO_REVIEW`
- `IN_REVIEW`
- `TO_DEPLOY`
- `TO_TEST`
- `IN_TEST`
- `DONE`

Exemple de section `[StatusMapping]` après initialisation :
```ini
[StatusMapping]
# En cours
10001 = TO_DO
# Terminé
10002 = TO_DO
# À faire
10003 = TO_DO
```

Vous devrez la modifier comme suit (les IDs et noms de statuts sont des exemples) :
```ini
[StatusMapping]
# En cours
10001 = IN_PROGRESS
# Terminé
10002 = DONE
# À faire
10003 = TO_DO
```

### 4. Lancer le script

1. Une fois la configuration complète, exécutez le script via `uv` :
   ```bash
   uv run display-daily-tickets
   ```
   **Optionnel** : Si vous souhaitez l'exécuter directement depuis les sources sans utiliser le script de projet configuré, utilisez la commande suivante depuis la racine du projet :
   ```bash
   uv run python src/display.py
   ```

### 5. Lancer les tests
Pour lancer la suite de tests unitaires, utilisez la commande suivante à la racine du projet :
```bash
PYTHONPATH=src uv run python -m unittest discover tests
```

### 6. Résoudre les éventuels problèmes

- Si vous rencontrez des erreurs liées aux permissions lors de l'accès à l'API Jira, assurez-vous que l'API est activée pour votre compte et que le jeton d'API est valide.
- Vérifiez que le fichier `config.ini` est correctement renseigné et que son chemin est correct.

---

Avec cette configuration, le script est prêt à être utilisé sur un environnement tiers. Assurez-vous de partager ce guide et les fichiers nécessaires pour garantir une prise en main facile par vos utilisateurs.
