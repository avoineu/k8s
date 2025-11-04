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
│   ├── prod
│   │   ├── Deployment.yaml
│   │   ├── Ingress.yaml
│   │   ├── Service.yaml
│   │   ├── mongodb-replica-statefulset.yaml
│   │   └── mongodb-service.yaml
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
Contient tous les manifests Kubernetes pour déployer l’application et ses dépendances. Les manifests sont principalement pour le namespace dev, mais certains fichiers permettent aussi de créer un environnement de test, production ou de synchronisation automatique.

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

* `Deployment.yaml` : déploiement de l’application Mini-Store pour test.

* `Ingress.yaml` : expose l’application de test via un Ingress.

* `Service.yaml` : service NodePort ou ClusterIP pour le test.

* `mongo-pvc.yaml / mongodb-replica-statefulset.yaml / mongodb-service.yaml` : MongoDB pour l’environnement de test.

#### dossier prod
Manifests Kubernetes pour déployer un environnement de production, isolé du namespace dev et test :
* `Deployment.yaml` : déploiement de l’application Mini-Store pour prod.

* `Ingress.yaml` : expose l’application de prod via un Ingress.

* `Service.yaml` : service NodePort ou ClusterIP pour la prod.

* `mongodb-replica-statefulset.yaml / mongodb-service.yaml` : MongoDB pour l’environnement de prod.

 #### autres fichiers dans k8s

`auto-sync-configmap.yaml` : ConfigMap pour configurer le script de sync automatique.

`auto-sync-cronjob.yaml` : CronJob qui exécute check-and-update.sh périodiquement pour mettre à jour le namespace test.

`auto-sync-rbac.yaml` : Role / RoleBinding pour donner les permissions nécessaires au CronJob.

`dashboard-admin.yaml` : manifeste pour déployer un dashboard admin.

`mongo-pvc.yaml` : PVC pour MongoDB standalone ou replica set.

`mongodb-replica-statefulset.yaml` : StatefulSet pour MongoDB replica set.

`mongodb-service.yaml` : service exposant MongoDB.

`products.json` : fichier JSON contenant les produits initiaux.

`redis-service.yaml / redis-statefulset.yaml` : manifests pour déployer Redis.

### dossier tests
Contient les tests unitaires de l’application.

`test_app.py` : tests Python pour vérifier le comportement de app.py.

## 2. Namespaces

L’application principale est pour l'instant déployée dans le namespace `dev`, à chaque push sur github, la dernière version de l'image `dev` est publié sur DockerHub et elle est alors en maximum 5 minutes pulled et deployé par le Cronjob dans le namespace `test`. Le namespace `test` permet de tester une version plus au point de l'application. Le namespace `prod` met à disposition l'application auprès de tout les utilisateurs. 

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

Le projet utilise quatre namespaces :

* **dev** : environnement principal de développement
* **test** : environnement secondaire, où toute l'équipe de développement peut tester la version final actuelle de l'application.
* **prod** : environnement de production, hébergeant la version stable et validée de l’application, accessible aux utilisateurs finaux  
* **kubernetes-dashboard** : pour le monitoring du cluster

Créer les namespaces (si non existants) :
```
kubectl create ns dev
kubectl create ns test
kubectl create ns prod
kubectl create ns kubernetes-dashboard
```
#### Étape 3 : Déploiement de l’application et des dépendances
Appliquer tous les manifests Kubernetes contenus dans le dossier `k8s/` :
```
kubectl apply -f k8s/ -R
```
Cela déploie :
* L’application **Flask Mini-Store**
* **MongoDB** (base de données principale)
* **Redis** (cache)
* **CronJob** d’auto-sync
* **Ingress Controller**
* les **Services, ConfigMaps, et secrets** nécessaires

Vérifier ensuite le statut des pods et des ressources déployées : :

```
kubectl get pods -A
kubectl get svc -A
kubectl get pvc -A
```
Tous les pods doivent être dans l’état Running ou Completed avant de passer à l’étape suivante.

#### Étape 4 : Configuration du DNS local et accès via Ingress
Pour accéder à l’application via Ingress, ajouter les entrées suivantes dans le fichier `/etc/hosts` :
```
127.0.0.1       dev.localhost
127.0.0.1       test.localhost
127.0.0.1       prod.localhost
```
Puis vérifier les Ingress actifs :
```
kubectl get ingress -A
```
Une fois le contrôleur NGINX déployé et configuré, les environnements deviennent accessibles :

* http://dev.localhost pour l’environnement de développement

* http://test.localhost pour l’environnement de test

* http://prod.localhost pour l’environnement de production

#### Étape 5 : Vérification du cluster
S'assurer que tout le cluster fonctionne correctement : 
```
kubectl get all -A
```

## 4. CI/CD Pipeline 

Le déploiement continu du projet est géré via **GitHub Actions**.  
Chaque push sur la branche principale déclenche automatiquement un pipeline complet qui assure la qualité du code, la création et la mise à jour des images Docker, puis leur propagation dans le cluster.

#### Gestion des secrets 
Les credentials sensibles (comme `KUBE_CONFIG`, `DOCKER_USERNAME`, `DOCKER_PASSWORD`) sont stockés sous forme de **GitHub Secrets** afin de sécuriser les accès lors du déploiement automatique.

* **`KUBE_CONFIG`** :  Contient le contenu du fichier `~/.kube/config` permettant à GitHub Actions d’interagir avec le cluster Kubernetes. Pour l’obtenir, exécuter sur la machine ou le cluster concerné : 
```
  cat ~/.kube/config
  ```

* **`DOCKER_USERNAME`** : Nom d’utilisateur du compte Docker Hub utilisé pour builder et pousser les images Docker.

* **`DOCKER_PASSWORD`** : Mot de passe ou token d’accès personnel associé au compte Docker Hub (Settings → Security → New Access Token).

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

### Avantages

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

Une fois cela fait, il suffit d'apply les fichiers à l'aide de ces commandes :
```
`kubectl apply -f mongo-pvc.yaml -n test`

`kubectl apply -f mongodb-service.yaml -n test`

`kubectl apply -f mongodb-statefulset.yaml -n test`
```

Il faut alors se connecter au primary pod (genéralement le premier pod) à l'aide de cette commande :
```
'kubectl exec -it mongodb-0 -n test -- mongosh'
```

Alors, il faut initialiser le Replica Set :

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
Pour accéder au pod, ajouter un item et afficher le contenu de la DB :
```
kubectl exec -it mongodb-0 -n test -- mongosh 

use shop 

db.items.insertOne({ id: 1, name: "T-shirt", price: 19.99 })

db.items.find() 
```
### 5.2 Dashboard
#### A) Mise en place

* Étape 1 : Appliquer le manifest officiel : 
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.9.0/aio/deploy/recommended.yaml`
```

* Étape 2 : Vérifier le déploiement, les pods doivent être en état **running** : 
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

Choisir l’option « Token » et entrer le Token généré précédemment.
Une fois cela fait, le dashboard sera fonctionnel. 

Il suffit alors d'aller dans la section `deployments`pour mettre à l'échelle (scaling) les pods qu'on veut au nombre que l'on veut. On peut également depuis le dashboard avoir une idée en instantanée de l'usage du CPU et de la mémoire faites par nos pods.


### 5.3 Sharding

Le Sharding est une technique de scaling horizontal utilisée pour répartir les données d’une base MongoDB sur plusieurs nœuds.

#### Architecture
L’infrastructure MongoDB en mode Sharded Cluster repose sur **trois composants principaux** :

1. **Config Servers**  
   - Stockent les **métadonnées du cluster**, notamment la répartition des chunks (fragments de données) entre les shards.  
   - Déployés via le fichier :  
     ```yaml
     config-server-statefulset.yaml
     ```
   - Ces pods sont regroupés dans un **StatefulSet** (souvent 3 réplicas) afin d’assurer la cohérence et la haute disponibilité.

2. **Shards**  
   - Chaque shard contient une **partie des données** de la base.  
   - Chaque shard est lui-même un **ReplicaSet**, garantissant la redondance et la tolérance aux pannes.  
   - Déployés via :  
     ```yaml
     shard1-statefulset.yaml, shard2-statefulset.yaml
     ```
   - Chaque StatefulSet crée automatiquement des **PersistentVolumeClaims (PVC)** pour stocker durablement les données sur les disques associés.

3. **Mongos (Query Router)**  
   - Le composant **mongos** agit comme un **routeur de requêtes** : il reçoit les requêtes clientes et les oriente vers le bon shard selon la clé de sharding.  
   - Les clients et les applications interagissent **uniquement avec mongos**, jamais directement avec les shards.  
   - Déployé via :  
     ```yaml
     mongos-deployment.yaml
     ```
   - Il peut être répliqué (plusieurs pods mongos) pour supporter une charge importante et assurer la haute disponibilité.



#### Initialisation 

Pour se connecter au pod, on peut lancer cette commande : 
```
'kubectl exec -it mongos-xxxxxxxx -n test -- mongosh'
```

Puis executer les commandes suivantes afin d'initialiser le **config-server**, les **shards** et ensuite d'activer le **sharding** :

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

Reprendre les configs ` redis-service.yaml `et `redis-statefulset.yaml` et les apply avec : 
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

Afin de tester si les pods redis marchent bien il suffit de s’y connecter avec : 

```
kubectl exec -it redis-0 -n redis -- redis-cli
```


Ensuite faire ces deux commandes pour obtenir la réponse. : 

```
SET test "hello world"

GET test
```


#### Intégration

Pour intégrer redis à l’app, il faut que dans le `deployment.yaml`, il y ait une value **redis.redis.svc.cluster.local** qui correspond au Service headless crée dans les configs. Ensuite dans votre app il faut l'importer avec : 
```
import redis
```


Et le setup : 
```
REDIS_HOST = os.getenv("REDIS_HOST", "redis.dev.svc.cluster.local")
REDIS_PORT = 6379 cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True) 
```



#### Vérification

Pour notre app, à chaque produit ajouter, on peut vérifier le cache simplement avec :
```
kubectl exec -it redis-0 -n dev -- redis-cli GET items
```



## 6. Guide pour les nouveaux developpeurs 
Ce guide a pour objectif d’aider tout nouveau développeur à prendre en main le projet, du setup local jusqu’au déploiement sur le cluster Kubernetes.

### 6.1 Prérequis

Avant de commencer, assurez-vous d’avoir installé :

- **Python 3.10+**
- **Docker** (si vous souhaitez builder les images localement)
- **kubectl** (pour interagir avec le cluster Kubernetes)
- **Git** (pour cloner et contribuer au projet)
- **Un accès au cluster Kubernetes** (namespace `dev` ou `test`)

### 6.2 Installation du projet

Cloner le dépôt GitHub :
```
git clone https://github.com/avoineu/k8s.git

cd k8s
```

### 6.3 Lancer le cluster local (mode Kubernetes)

Appliquer les manifests Kubernetes pour déployer les ressources nécessaires : 
```
kubectl apply -f k8s/
```

Vérifier que les pods sont bien en cours d’exécution : 
```
kubectl get pods -n dev
```

Pour visualiser les services et ingress :
```
kubectl get svc,ingress -n dev
```

### 6.4 Lancer l’application 

Dans Kubernetes : `kubectl apply` suffit pour que les pods s’exécutent automatiquement.

Si vous souhaitez simplement tester le code Python sans passer par Kubernetes :
```
python app/app.py
```
L’application Flask démarrera alors sur `http://127.0.0.1:5000`.

Ce mode est utile pour le développement rapide ou le débogage avant intégration au cluster.

### 6.5 Tests unitaires

Avant tout push, il est recommandé d’exécuter les tests unitaires :
```
pytest tests/
```
Aussi, un push sur la branche principale déclenchera automatiquement le pipeline GitHub Actions qui exécute ces tests dans le CI/CD.

### 6.6 Déploiement sur le cluster kubernetes

Pour (re)déployer une version sur un namespace spécifique :
```
kubectl apply -f k8s/ -n dev
```
Pour un environnement de test :
```
kubectl apply -f k8s/ -n test
```
À noter que le namespace `prod` est réservé aux versions stables et validées.

### 6.7 Logs & Debug
Afficher les logs d’un pod en cours d’exécution :
```
kubectl logs -f <nom-du-pod> -n dev
```
Entrer dans un pod pour le débogage :
```
kubectl exec -it <nom-du-pod> -n dev -- /bin/bash
```
### 6.8 Accès à MongoDB pour inspection

Se connecter à la base MongoDB :
```
kubectl exec -it mongodb-0 -n dev -- mongosh
```
Puis interroger la base :
```
use shop
db.items.find().pretty()
```

### 6.9 Bonnes pratiques 

* Tester vos changements localement **avant le push**.

* Ne jamais déployer directement sur `prod` sans validation.

* Surveillez les pods avec :
```
kubectl get pods -A
```
* Vérifiez régulièrement l’état du pipeline GitHub Actions.