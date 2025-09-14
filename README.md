# Documentation technique PFE

####  Prérequis système

- Docker `v28.3.3+`
- Docker Compose `v2.39.1+`
- Python `v3.11+`
- pip `v25.1.1+`
- Git `v2.34.1+`
- IDE recommandé : PyCharm ou VSCode

####  Mise en place du collector_service

##### 1. Clonage du repository

```bash
git clone https://github.com/MaelMainsard/ynov_pfe_collector_service.git
cd ynov_pfe_collector_service
```

##### 2.  Configuration de l'environnement

```bash
cp .env.local .env
```

##### 3. Création de l'environnement virtuel


```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
venv\Scripts\activate
```

##### 4.  Installation des dépendances

```bash
pip install -r requirements.txt
```

##### 5.  Démarrage du service

###### Option A : Utilisation sans modification

Si vous ne souhaitez pas faire de modifications dans le service :

```bash
docker compose up -d
```

###### Option B : Développement local

Si vous souhaitez développer ou modifier le service :

1. **Démarrage des services de base (base de données + broker) :**

```bash
docker compose up -d orange_mock postgres
```

2. **Lancement du service en mode développement :**

```bash
python3 main.py
```

##### 6.  Simulation d'envoi de données de station

Vous pouvez facilement simuler l'envoi de données de station en utilisant le CLI mis à disposition :

```bash
cd test

# Test avec des données mockés
python3 test/mock-station.py create-mock-data --station_uid=69919589-d657-4ba2-8657-ee9f28963afe --nbr=100
# Ou nbr est le nombre de données souhaité

# Test avec une donnée simple
python3 test/mock-station.py send-prompt-data \
  --station_uid=69919589-d657-4ba2-8657-ee9f28963afe \
  --air_temperature=25.5 \
  --relative_humidity=60 \
  --soil_moisture=45 \
  --rainfall=0.2 \
  --solar_irradiance=1200 \
  --leaf_wetness_duration=12
```

####  Mise en place du dashboard Superset

##### 1. Clonage du repository

```bash
git clone --depth=1 https://github.com/apache/superset.git
cd superset
```

##### 2. Démarrage de Superset

```bash
docker compose -f docker-compose-light.yml up
```

##### 3. Connecter la base à Superset

1. Accéder au front Superset en allant sur [http://127.0.0.1:9001](http://127.0.0.1:9001)
2. Se connecter avec :
    - Username : `admin`
    - Password : `admin`
3. Aller dans **Settings** → **Database Connection** → **+ Database** → Sélectionner **PostgreSQL**
4. Renseigner les champs basés sur le contenu du `.env`
    - Si le port est fermé, essayer de remplacer l'host par `host.docker.internal`
5. Cliquer sur **Connect** puis sur **Finish**

##### 4.  Créer les datasets

1. Dans **Datasets** → **+ Dataset**
2. Choisir la base de données ajoutée précédemment
3. Dans **Schema**, choisir `public`
4. Choisir une table
5. Répéter l'opération pour les 3 tables : `Station`, `StationParam` et `StationData`
