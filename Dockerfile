# Étape 1 : Image de base Python
FROM python:3.11-slim

# Étape 2 : Crée un dossier de travail
WORKDIR /app

# Étape 3 : Copie les dépendances et installe-les
COPY app/requirements.txt .
RUN pip install -r requirements.txt

# Étape 4 : Copie le reste du code
COPY app/ .

# Étape 5 : Expose le port et lance l’application
EXPOSE 5000
CMD ["python", "app.py"]
