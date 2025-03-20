# Guide d'utilisation : Configuration .ini pour exécuter le script Python
Ce script Python utilise un fichier de configuration au format `.ini` afin d'accéder aux paramètres nécessaires pour se connecter à une instance Jira et manipuler ses données. Ce fichier `.ini` doit contenir les informations d'identification et autres paramètres Jira nécessaires.
## Structure attendue du fichier `.ini`
Le fichier `.ini` doit contenir une section `[Jira]` avec les clés suivantes :
- **`server`** : l'URL du serveur Jira auquel se connecter.
- **`username`** : le nom d'utilisateur de l'instance Jira.
- **`api_token` **: le jeton de l'API Jira associé au compte utilisateur indiqué.
- **`filter_id` **: l'identifiant d'un filtre Jira à utiliser pour récupérer les données.

Voici un exemple de structure correcte d'un fichier `.ini` :
``` ini
[Jira]
server = <hosturl>
username = <username>
api_token = <api_token>
filter_id = <filter_id>
[User]
name = <jira_user_name>
```

## Étapes pour configurer et exécuter le script
1. **Installer les dépendances :** Assurez-vous d'avoir toutes les bibliothèques Python nécessaires installées pour exécuter le script.
2. **Créer un fichier `.ini` :**
    - Créez un fichier `config.ini` (ou un autre nom de votre choix).
    - Remplissez les informations selon le modèle indiqué ci-dessus.

3. **Placer le fichier `.ini` à l'emplacement attendu :** Le script doit être capable d'accéder au fichier `.ini`. Généralement, il doit être placé dans le même dossier que le script Python ou dans un chemin spécifié dans le code.
4. **Exécuter le script Python :** Lancez le script et vérifiez que les paramètres du fichier `.ini sont correctement lus.

## Remarques
- Vous pouvez gérer plusieurs configurations en créant plusieurs fichiers `.ini` et en les spécifiant lors de l'exécution.
- Assurez-vous de ne **pas partager** ce fichier `.ini` contenant vos identifiants ou jetons d'API Jira avec d'autres personnes ou de ne pas le pousser dans un dépôt GIT public.
