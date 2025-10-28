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

* comment installer et démarrer cluster
* déploiement des namespaces dev et test 
* exposition via Ingress 

### 3.2 Cloud migration guide

* Gestion des secrets

## 4. CI/CD Pipeline 
GitHub Actions pipeline : description étape par étape.

Checkout, setup Python, install dependencies, run unit tests

Build Docker image, push DockerHub, check secrets

Comment le pipeline s’intègre avec le namespace test.

Option “auto-sync” pour mettre à jour le namespace test après validation du pipeline.

## 5. Monitoring & Scaling Instructions 

### 5.1 Replica set
Pourquoi on utilise un replica set.
Manifests : StatefulSet, Service, PVC.
Comment accéder à la base pour debug/test (kubectl exec ... mongo).

### 5.2 Sharding
Pourquoi le sharding est utilisé.

Architecture : config servers, shards, routeurs mongos.

Commandes pour vérifier l’état (sh.status()).

## 6. Monitoring & Scaling Instructions
dashboard

## 7. Guide pour les nouveaux developpeurs 

Installer Python et dépendances (requirements.txt).

Cloner le repo, setup cluster local.

Lancer les tests unitaires (pytest tests/).

Lancer l’application en local (python app/app.py).

Déployer sur namespace dev/test (kubectl apply -f k8s/...).

Où regarder logs et comment accéder à la base MongoDB.


# Ancien Readme 
## 3. Déploiement

Le déploiement est répliqué avec deux pods.  

Vérifier l’état des pods :

```bash
kubectl get pods -n dev
```


Vérifier que les pods sont dans l’état READY 1/1 :
```
'kubectl get pods -n dev'
```
## 4. Services

Type de service : ClusterIP pour hello-k8s-service.

Vérification : 
````
'kubectl get svc -n dev'
````

Le service est exposé sur le port 80.

## 5. Ingress

Controller utilisé : NGINX

Configuration dans le namespace dev
spec:
  ingressClassName: nginx

Accès à l’application
```
curl http://localhost/
```

## 6. Docker

L’image de l’application est construite à partir du Dockerfile.
Le cluster peut utiliser soit une image locale, soit une image provenant d’un dépôt Docker.

## 7. Commandes principales utilisées
Appliquer les manifests :
```
kubectl apply -f k8s/Deployment.yaml -n dev
kubectl apply -f k8s/Service.yaml -n dev
kubectl apply -f k8s/Ingress.yaml -n dev
```

Vérifications :
```
kubectl get pods -n dev
kubectl get svc -n dev
kubectl get ingress -n dev
```

Supprimer les ressources (en cas de conflit) :

```
kubectl delete ingress --all -n dev
kubectl delete deploy --all -n dev
kubectl delete svc --all -n dev
```

# CHATGPT 

kubectl présent ?
kubectl version --client

Voir quel cluster kubernetes est actif
kubectl config current-context

vérifier s'il y a un ingress controller (nginx) installé
kubectl get pods -A | grep ingress  true
kubectl get svc -A | grep ingress  true

Vérifiez et créer les namespaces
kubectl get ns
kubectl create ns dev  true
kubectl create ns test  true
kubectl create ns prod || true
kubectl create ns kubernetes-dashboard 

Build L'image
docker build -t samirbch/mini-store:v13 .

Appliquer les manifests
kubectl apply -f k8s/ -R

ou 

kubectl apply -f k8s/mongo/ -n prod
kubectl apply -f k8s/ -n prod   fais attention: certains fichiers peuvent contenir namespace explicit

kubectl apply -f k8s/test/ -n test
kubectl apply -f k8s/ -n dev

Vérifiez le post apply
kubectl get pods -n prod
kubectl get pods -n test
kubectl get pods -n dev

kubectl get svc -n prod
kubectl get svc -n test

kubectl get ingress -A

Ajouter
sudo nano /etc/hosts

'
127.0.0.1       dev.localhost
127.0.0.1       test.localhost'

Initialisez sharding
-Se connecter à un pod config server :


kubectl exec -it -n dev mongo-cfg-0 -- mongosh --port 27019

-Vérifier l’état du replica set :


rs.status()

-Initialiser le replica set :


rs.initiate({
  _id: "cfgReplSet",
  configsvr: true,
  members: [
    { _id: 0, host: "mongo-cfg-0.mongo-cfg-svc.dev.svc.cluster.local:27019" },
    { _id: 1, host: "mongo-cfg-1.mongo-cfg-svc.dev.svc.cluster.local:27019" },
    { _id: 2, host: "mongo-cfg-2.mongo-cfg-svc.dev.svc.cluster.local:27019" }
  ]
})

-Redémarrer ton déploiement Mongos pour qu’il se connecte aux config servers correctement :
kubectl rollout restart deployment mongos-deployment -n dev

# Samir
Guide Dashboard:A) Mise en place

Étape 1 : Appliquer le manifest officiel : kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.9.0/aio/deploy/recommended.yaml

Étape 2 : Vérifier le déploiement, les pods doivent être en running:kubectl get pods -n kubernetes-dashboard

Etape 3 : Créer compte admin:Créer le ServiceAccount avec le rôle admin dans un fichier « dashboard-admin.yaml » (config complète sur le git)Ensuite générer le token d’accès : kubectl -n kubernetes-dashboard create token admin-user


B) Accès

Pour accéder au Dashboard lancer : kubectl proxy
Aller dans navigateur : http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

Choisir l’option « Token » et entrer le Token générer précédemment Une fois cela fait, le dashboard sera fonctionnel.

Guide Cache Redis:

Redis est utilisé ici comme **système de cache** pour accélérer les requêtes en stockant temporairement les données.Il faut pour cela configurer un service pour accéder aux pods et un statefulset pour gérer les pods avec un stockage persistant.

A) Déploiment 

Reprendre les configs « redis-service.yaml » et « redis-statefulset.yaml » sur GitHub et les apply avec :kubectl apply -f redis-service.yaml -n redis
kubectl apply -f redis-statefulset.yaml -n redis


Vérifier que Redis est en cours d’éxecution: kubectl get pods -n redis -o wide
kubectl get pvc -n redis

B) Test

Pour tester si les pods redis marchent bien il suffit de s’y connecter avec :
kubectl exec -it redis-0 -n redis -- redis-cli

Ensuite faire un : SET test "hello world"
Et ensuite un : GET test 
Pour obtenir la réponse.

C) Intégration

Pour l’intégrer à l’app il faut que dans le « deployment.yaml » il y ait une value "redis.redis.svc.cluster.local" qui correspond au Service headless crée dans les configs.Ensuite dans votre app il faut importer : import redis

Et le setup : REDIS_HOST = os.getenv("REDIS_HOST", "redis.dev.svc.cluster.local")  # nom du service Redis
REDIS_PORT = 6379
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
4) Vérification

Pour notre app, à chaque produit ajouter, on peut vérifier le cache simplement avec :kubectl exec -it redis-1 -n dev -- redis-cli GET items