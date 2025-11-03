# 🧩 Projet Mini Store

## 1. Structure du projet
Voici la structure interne final du projet


```
├── Dockerfile
├── README.md
├── app
│   ├── app.py
│   ├── requirements.txt
│   └── templates
│       └── index.html
├── check-and-update.sh
├── k8s
│   ├── Deployment.yaml
│   ├── Ingress.yaml
│   ├── Service.yaml
│   ├── auto-sync-configmap.yaml
│   ├── auto-sync-cronjob.yaml
│   ├── auto-sync-rbac.yaml
│   ├── dashboard-admin.yaml
│   ├── mongo
│   │   ├── cfg-pvc.yaml
│   │   ├── cfg-service.yaml
│   │   ├── cfg-statefulset.yaml
│   │   ├── mongos-deployment.yaml
│   │   ├── mongos-service.yaml
│   │   ├── mongos.yaml
│   │   ├── shard1-pvc.yaml
│   │   ├── shard1-service.yaml
│   │   ├── shard1-statefulset.yaml
│   │   ├── shard2-pvc.yaml
│   │   ├── shard2-service.yaml
│   │   └── shard2-statefulset.yaml
│   ├── mongo-pvc.yaml
│   ├── mongodb-replica-statefulset.yaml
│   ├── mongodb-service.yaml
│   ├── products.json
│   ├── redis-service.yaml
│   ├── redis-statefulset.yaml
│   ├── test
│   │   ├── Deployment.yaml
│   │   ├── Ingress.yaml
│   │   ├── Service.yaml
│   │   ├── mongo-pvc.yaml
│   │   ├── mongodb-replica-statefulset.yaml
│   │   └── mongodb-service.yaml
│   └── watch-sync
└── tests
    └── test_app.py
```

### dossier App
Contient le code principal de l'application.

* `app.py` : le fichier principal de l’application Flask Mini-Store. Contient les routes '/' pour l’interface web et '/api/products' pour l’API REST.

* `requirements.txt` : liste des dépendances Python nécessaires.

* `templates/index.html` : le template HTML principal pour l’interface utilisateur.

### check-and-update.sh
Script shell permettant de synchroniser automatiquement le namespace test avec la dernière image déployée sur GitHub/DockerHub.

Il est utilisé dans un CronJob Kubernetes pour vérifier toutes les 5 minutes si la version du namespace test est à jour comparé à celle sur DockerHub, et déclencher un kubectl rollout restart si ce n'est pas le cas.

### dossier k8s
Contient tous les manifests Kubernetes pour déployer l’application et ses dépendances. Les manifests sont principalement pour le namespace dev, mais certains fichiers permettent aussi de créer un environnement de test ou de synchronisation automatique.

#### dossier mongo
Contient tous les manifests pour déployer le cluster MongoDB sharded et ses services :

`cfg-pvc.yaml` : PVC pour les config servers MongoDB.

`cfg-service.yaml` : service pour exposer les config servers.

`cfg-statefulset.yaml` : StatefulSet pour les config servers.

`mongos-deployment.yaml` : déploiement des routeurs mongos.

`mongos-service.yaml` : service exposant les mongos.

`mongos.yaml` : manifeste global pour le déploiement complet des mongos.

`shard1-*.yaml / shard2-*.yaml` : StatefulSets, PVCs et services pour chaque shard du cluster MongoDB.

#### dossier test 

Manifests Kubernetes pour déployer un environnement de test, isolé du namespace dev :

* `Deployment.yaml` : déploiement de l’application Mini-Store pour tests.

* `Ingress.yaml` : expose l’application de test via un Ingress.

* `Service.yaml` : service NodePort ou ClusterIP pour le test.

* `mongo-pvc.yaml / mongodb-replica-statefulset.yaml / mongodb-service.yaml` : MongoDB pour l’environnement de test.

 #### autres fichiers dans k8s

`auto-sync-configmap.yaml` : ConfigMap pour configurer le script de sync automatique.

`auto-sync-cronjob.yaml` : CronJob qui exécute check-and-update.sh périodiquement pour mettre à jour le namespace test.

`auto-sync-rbac.yaml` : Role / RoleBinding pour donner les permissions nécessaires au CronJob.

`dashboard-admin.yaml` : manifeste pour déployer un dashboard admin.

`mongo-pvc.yaml` : PVC pour MongoDB standalone ou replica set.

`mongodb-replica-statefulset.yaml` : StatefulSet pour MongoDB replica set.

`mongodb-service.yaml` : service exposant MongoDB.

`products.json` : fichier JSON contenant les produits initiaux.

`redis-service.yaml / redis-statefulset.yaml` : manifests pour déployer Redis si utilisé.

### dossier tests
Contient les tests unitaires de l’application.

`test_app.py` : tests Python pour vérifier le comportement de app.py.

## 2. Namespaces

L’application principale est pour l'instant déployée dans le namespace `dev`, à chaque push sur github, la dernière version de l'image `dev` est publié sur DockerHub et elle est alors en maximum 5 minutes pulled et deployé par le Cronjob dans le namespace `test`

## 3. Cluster Setup Instructions

### 3.1 Local Setup

Le projet **Mini-Store** est conçu pour fonctionner sur un cluster **Kubernetes** existant,  le déploiement se fait directement sur le cluster configuré via `kubectl`.

#### Étape 1 : Vérification de l’environnement Kubernetes

Avant de commencer, vérifier que `kubectl` est installé et correctement connecté à votre cluster :

```bash
kubectl version --client
kubectl config current-context
kubectl get nodes
```

#### Étape 2 : Création des namespaces

Le projet utilise trois namespaces :

* **dev** : environnement principal de développement
* **test** : environnement secondaire, où toute l'équipe de développement peut tester la version final actuelle de l'application.
* **kubernetes-dashboard** : pour le monitoring du cluster

Créer les namespaces (si non existants) :
```
kubectl create ns dev
kubectl create ns test
kubectl create ns kubernetes-dashboard
```
#### Étape 3 : Déploiement de l’application et des dépendances
Appliquer tous les manifests Kubernetes contenus dans le dossier `k8s/` :
```
kubectl apply -f k8s/ -R
```
Cela déploie :
* L’application **Flask Mini-Store**
* **MongoDB** 
* **Redis** (cache)
* **CronJob** d’auto-sync
* **Ingress Controller**

Vérifier ensuite le statut des pods :

```
kubectl get pods -A
```

#### Étape 4 : Configuration du DNS local et accès via Ingress
Pour accéder à l’application via Ingress, ajouter les entrées suivantes dans `/etc/hosts` :
```
127.0.0.1       dev.localhost
127.0.0.1       test.localhost
```
Puis vérifier les Ingress actifs :
```
kubectl get ingress -A
```
Une fois le contrôleur NGINX en place, l’application est accessible sur :

* http://dev.localhost pour l’environnement de développement

* http://test.localhost pour l’environnement de test

### 3.2 Cloud migration guide

#### Gestion des secrets 
Les credentials sensibles (comme `KUBE_CONFIG`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`) sont stockés sous forme de **GitHub Secrets**.

## 4. CI/CD Pipeline 

Le déploiement continu du projet est géré via **GitHub Actions**.  
Chaque push sur la branche principale déclenche automatiquement un pipeline complet qui assure la qualité du code, la création et la mise à jour des images Docker, puis leur propagation dans le cluster.

### 4.1 Étapes du pipeline GitHub Actions

Le workflow suit la séquence suivante :

1. **Checkout du code**  
   Téléchargement la dernière version du dépôt GitHub.

2. **Setup de Python**  
   Configuration Python et installation des dépendances.

3. **Installation des dépendances**

4. **Tests unitaires**  
   Exécution des tests contenus dans le dossier `tests/` pour valider l’application.

5. **Build de l’image Docker**

6. **Connexion à DockerHub**

7. **Push de l’image Docker**

8. **Vérification des secrets**  
   Le pipeline vérifie que les secrets `KUBE_CONFIG`, `DOCKER_USERNAME`, `DOCKER_PASSWORD` sont bien présents avant d’exécuter les étapes critiques.

### 4.2 Intégration avec Kubernetes (namespace test)

Une fois l’image publiée sur DockerHub, la mise à jour du cluster est automatisée par un **CronJob Kubernetes** via le script `check-and-update.sh`.

### Fonctionnement

* Le CronJob s’exécute toutes les 5 minutes.
* Il vérifie si la dernière image DockerHub correspond à celle actuellement utilisée par le namespace **test**.
* Si une nouvelle image est disponible, le script déclenche le déploiement.

Cela garantit que le namespace **test** reflète toujours la version la plus récente validée par le pipeline.

### Avantage

Ce mécanisme permet de découpler complètement :  

* le **build et le push** (via GitHub Actions)  
* le **déploiement** (via Kubernetes + CronJob)  

assurant ainsi une intégration continue et un déploiement continu (**CI/CD**) entièrement automatisé.

## 5. Monitoring, Scaling Instructions & Redis

### 5.1 Replica set

#### Concept

Il s’agit d’un ensemble de pods MongoDB contenant la même base de données :

* Un Primary : gère les écritures et répliques vers les secondaires.

* Un ou plusieurs Secondaries : répliquent les données et peuvent prendre le relais en cas de panne du Primary.

#### Setup 

Trois fichiers sont nécessaires pour déployer le Replica Set :

* `mongodb-statefulset.yaml` :
Définit les 3 pods MongoDB avec `--replSet rs0` pour activer la réplication.
Chaque pod dispose d’un stockage persistant via un volumeClaimTemplate.

* `mongodb-service.yaml` :
Service headless (clusterIP: None) utilisé pour la découverte automatique des pods (mongodb-0, mongodb-1, mongodb-2).

* `mongo-pvc.yaml` :
Définit les PersistentVolumeClaims (PVC) qui assurent la conservation des données même si un pod redémarre.

Une fois cela fait, il suffit d'apply les fichiers :
```
`kubectl apply -f mongo-pvc.yaml -n test`

`kubectl apply -f mongodb-service.yaml -n test`

`kubectl apply -f mongodb-statefulset.yaml -n test`
```

Pour se connecter au premier pod :
```
'kubectl exec -it mongodb-0 -n test -- mongosh'
```

Ensuite il faut initialiser le Replica Set :

```
rs.initiate({
  _id: "rs0",

  members: [
    { _id: 0, host: "mongodb-0.mongodb-service.test.svc.cluster.local:27017" },

    { _id: 1, host: "mongodb-1.mongodb-service.test.svc.cluster.local:27017" },

    { _id: 2, host: "mongodb-2.mongodb-service.test.svc.cluster.local:27017" }
  ]
})
```
Pour vérifier :
```
rs.status()
```
#### Accès et debug
Pour accéder au pod et ajouter un item dans la DB :
```
`kubectl exec -it mongodb-0 -n test -- mongosh `

`use shop `

`db.items.insertOne({ id: 1, name: "T-shirt", price: 19.99 })`

`db.items.find() `
```
### 5.2 Dashboard
#### A) Mise en place

* Étape 1 : Appliquer le manifest officiel : 
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.9.0/aio/deploy/recommended.yaml`
```

* Étape 2 : Vérifier le déploiement, les pods doivent être en running: 
```
kubectl get pods -n kubernetes-dashboard
```

* Etape 3 : Créer compte admin, il suffit de créer le ServiceAccount avec le rôle admin dans un fichier `dashboard-admin.yaml` (config complète sur le git). Ensuite générer le token d’accès : 
```
kubectl -n kubernetes-dashboard create token admin-user
```

#### B) Accès

Pour accéder au Dashboard lancer : 
```
kubectl proxy
```

Aller sur votre navigateur et lancer : http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

Choisir l’option « Token » et entrer le Token générer précédemment.
Une fois cela fait, le dashboard sera fonctionnel.


### 5.3 Sharding

Le Sharding est une technique de scaling horizontal utilisée pour répartir les données d’une base MongoDB sur plusieurs nœuds.

#### Architecture

`config-server-statefulset.yaml` → déploie les Config Servers qui stockent les métadonnées du cluster.

`shard1-statefulset.yaml, shard2-statefulset.yaml` → déploient les Shards contenant les données réelles (chaque shard est un ReplicaSet).

`mongos-deployment.yaml` → déploie le Router (mongos) qui oriente les requêtes vers le bon shard.



#### Initialisation 

Se connecter au pod : 'kubectl exec -it mongos-xxxxxxxx -n test -- mongosh'


Puis executer les commandes suivantes afin d'initialiser le config-server, les shards et ensuite d'activer le sharding :

```
// Init config server
rs.initiate({
  _id: "rs-config-server",
  configsvr: true,
  members: [
    { _id: 0, host: "config-server-0.config-server.test.svc.cluster.local:27019" },
    { _id: 1, host: "config-server-1.config-server.test.svc.cluster.local:27019" },
    { _id: 2, host: "config-server-2.config-server.test.svc.cluster.local:27019" }
  ]
})

// Init shard1
rs.initiate({
  _id: "rs-shard1",
  members: [
    { _id: 0, host: "shard1-0.shard1.test.svc.cluster.local:27018" },
    { _id: 1, host: "shard1-1.shard1.test.svc.cluster.local:27018" },
    { _id: 2, host: "shard1-2.shard1.test.svc.cluster.local:27018" }
  ]
})

// Init shard2
rs.initiate({
  _id: "rs-shard2",
  members: [
    { _id: 0, host: "shard2-0.shard2.test.svc.cluster.local:27018" },
    { _id: 1, host: "shard2-1.shard2.test.svc.cluster.local:27018" },
    { _id: 2, host: "shard2-2.shard2.test.svc.cluster.local:27018" }
  ]
})

// Depuis mongos : ajouter les shards
sh.addShard("rs-shard1/shard1-0.shard1.test.svc.cluster.local:27018")
sh.addShard("rs-shard2/shard2-0.shard2.test.svc.cluster.local:27018")

// Activer le sharding sur la base
sh.enableSharding("shop")

// Définir la clé de sharding
db.items.createIndex({ id: "hashed" })
sh.shardCollection("shop.items", { id: "hashed" })
```


### 5.4 Redis

Redis est utilisé ici comme système de cache pour accélérer les requêtes en stockant temporairement les données. Il faut pour cela configurer un service pour accéder aux pods et un statefulset pour gérer les pods avec un stockage persistant.

#### Déploiment

Reprendre les configs ` redis-service.yaml `et `redis-statefulset.yaml ` sur GitHub et les apply avec : 
```
kubectl apply -f redis-service.yaml -n redis

kubectl apply -f redis-statefulset.yaml -n redis
```


Vérifier que Redis est en cours d’éxecution: 

```
kubectl get pods -n redis -o wide

kubectl get pvc -n redis
```


#### Test

Pour tester si les pods redis marchent bien il suffit de s’y connecter avec : 

```
kubectl exec -it redis-0 -n redis -- redis-cli
```


Ensuite faireces deux commandes pour obtenir la réponse. : 

```
SET test "hello world"

GET test
```


#### Intégration

Pour l’intégrer à l’app il faut que dans le `deployment.yaml` il y ait une value **redis.redis.svc.cluster.local** qui correspond au Service headless crée dans les configs. Ensuite dans votre app il faut importer avec : 
```
import redis
```


Et le setup : 
```
REDIS_HOST = os.getenv("REDIS_HOST", "redis.dev.svc.cluster.local") # nom du service Redis REDIS_PORT = 6379 cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True) 
```



#### Vérification

Pour notre app, à chaque produit ajouter, on peut vérifier le cache simplement avec :
```
kubectl exec -it redis-1 -n dev -- redis-cli GET items
```



## 6. Guide pour les nouveaux developpeurs 

### 6.1 Installation et préparation

Installer Python 3.10+

Installer les dépendances : `pip install -r requirements.txt`

Cloner le projet : 
`git clone https://github.com/avoineu/k8s.git`

`cd <nom-du-projet>`


### 6.2 Lancer le cluster local

Appliquer les manifests Kubernetes : `kubectl apply -f k8s/`

Vérifier les pods en cours d'éxecution : `kubectl get pods -n dev`

### 6.3 Tests unitaires

Pour effectuer dles tests unitaires :

-Soit lancer `pytest test_app.py/`

-Soit push sur GitHub

### 6.4 Lancer l’application en local

Dans Kubernetes → kubectl apply suffit pour que les pods s’exécutent automatiquement.

Local (hors K8s) → on peut lancer python app/app.py pour tester sans cluster.

### 6.5 Déploiement sur cluster

Pour déployer sur un namespace : `kubectl apply -f k8s/ -n dev`

### 7.6 Logs & Debug

Voir les logs : `kubectl logs -f <nom-du-pod> -n dev`

Accès à MongoDB pour inspection : `kubectl exec -it mongodb-0 -n dev -- mongosh `

`use shop `

`db.items.find().pretty()`