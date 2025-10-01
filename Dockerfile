# Image de base nginx
FROM nginx:alpine

# Copie de ton index.html dans le dossier servi par nginx
COPY index.html /usr/share/nginx/html/index.html

