# 🧩 Projet Hello Kubernetes

## 1. Structure du projet

```
app/   
└── index.html        # Code de l’application

k8s/
│
├── Deployment.yaml   # Déploiement de l’application hello-k8s
├── Service.yaml      # Service pour exposer les pods
└── Ingress.yaml      # Ingress pour accéder à l’application depuis localhost

Dockerfile            # Pour construire l’image Docker de l’application
```

## 2. Namespaces

L’application principale est pour l'instant déployée dans le namespace `dev`.

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