## Service barrier-service

**Description :** Ce service contrôle l'ouverture et la fermeture des barrières d'accès, permettant de gérer l'entrée et la sortie des véhicules.

# urls disponibles

GET / -> Msg d'accueil
GET /status -> Etat de la barrère
POST /ouvrir -> ouvre la barriere
POST /fermer -> ferme la barriere

# test

cd barrier-service
python app.py

url http://localhost:5002/status
curl -X POST http://localhost:5002/ouvrir
curl -X POST http://localhost:5002/fermer
