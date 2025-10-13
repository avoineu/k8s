#!/bin/bash
set -e

NAMESPACE="test"
DEPLOYMENT="mini-store-deployment"
IMAGE_REPO="samirbch/mini-store"

# Récupère le tag de l'image actuellement déployée
CURRENT_IMAGE=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}')

# Récupère le dernier tag pushé sur DockerHub
LATEST_TAG=$(curl -s https://hub.docker.com/v2/repositories/${IMAGE_REPO}/tags?page_size=1 | jq -r '.results[0].name')
LATEST_IMAGE="${IMAGE_REPO}:${LATEST_TAG}"

echo "🔍 Image actuelle : $CURRENT_IMAGE"
echo "🔎 Dernière image : $LATEST_IMAGE"

# Compare et met à jour si nécessaire
if [ "$CURRENT_IMAGE" != "$LATEST_IMAGE" ]; then
  echo "🚀 Nouvelle version détectée, mise à jour du déploiement..."
  kubectl set image deployment/$DEPLOYMENT mini-store=$LATEST_IMAGE -n $NAMESPACE
else
  echo "✅ Image déjà à jour, aucune action nécessaire."
fi
