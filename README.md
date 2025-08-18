# Guide d'utilisation : Configuration .ini pour exécuter le script Python
Ce script Python utilise un fichier de configuration au format `.ini` afin d'accéder aux paramètres nécessaires pour se connecter à une instance Jira et manipuler ses données. Ce fichier `.ini` doit contenir les informations d'identification et autres paramètres Jira nécessaires.

## Étapes pour configurer et exécuter le script

### 1. Préparation de votre environnement

1. Assurez-vous que Python (version 3.11 ou supérieure) est installé sur votre machine. Vous pouvez le télécharger à partir de [python.org](https://www.python.org/).
2. Créez et activez un environnement virtuel pour isoler vos dépendances Python :
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Sous Linux/macOS
   .venv\Scripts\activate       # Sous Windows
   ```

### 2. Installation des dépendances

1. Clonez ou téléchargez le dépôt du projet :
   ```bash
   git clone https://github.com/Sorondare/DisplayJiraTickets
   cd DisplayJiraTickets
   ```
2. Installez les dépendances via `pip` :
   ```bash
   pip install .
   ```

### 3. Création et configuration du fichier `.ini`

1.  Créez un fichier `config.ini` à la racine du projet. Vous pouvez vous baser sur le fichier `config.ini.example` fourni.
2.  Remplissez-le avec vos informations.

Le fichier `.ini` doit contenir une section `[Jira]` avec les clés suivantes :
- **`server`** : l'URL du serveur Jira auquel se connecter.
- **`username`** : le nom d'utilisateur de l'instance Jira.
- **`api_token`** : le jeton de l'API Jira associé au compte utilisateur indiqué.
- **`jql_filter`** : la requête JQL pour filtrer les tickets.

Voici un exemple de structure correcte d'un fichier `.ini` :

```ini
[Jira]
server = <host url>
username = <username>
api_token = <api token>
language = <jira displayed language (default: en)>
jql_filter = project = "MyProject" AND assignee = currentUser() AND sprint in openSprints()

[Report]
username = <jira username used in issues>
introduction = <introduction to the ticket list output>

[Logging]
level = INFO
```

### 4. Lancer le script

1. Une fois la configuration complète, exécutez le script à l'aide de la commande définie dans le fichier `pyproject.toml` :
   ```bash
   display-daily-tickets
   ```
   **Optionnel** : Si vous n'avez pas installé le package et que vous souhaitez l'exécuter depuis les sources, utilisez la commande suivante depuis la racine du projet :
   ```bash
   python -m src.display_jira_tickets
   ```

### 5. Résoudre les éventuels problèmes

- Si vous rencontrez des erreurs liées aux permissions lors de l'accès à l'API Jira, assurez-vous que l'API est activée pour votre compte et que le jeton d'API est valide.
- Vérifiez que le fichier `config.ini` est correctement renseigné et que son chemin est correct.

---

Avec cette configuration, le script est prêt à être utilisé sur un environnement tiers. Assurez-vous de partager ce guide et les fichiers nécessaires pour garantir une prise en main facile par vos utilisateurs.
