## Service de produits

**Description :** Ce service gère le catalogue des produits, permettant de consulter, créer et modifier les articles disponibles à la vente.

# Les urls disponibles:

GET /products -> Liste de tous les produits
GET /product/{id} -> Récupère un produit par son ID
POST /products -> Créer un nouveau produit
PUT /product/{id} -> Modifier un produit existant

# Test :

cd product-service
python app.py

curl http://localhost:8001/products
curl http://localhost:8001/product/1
curl -X POST "http://localhost:8001/products" -H "Content-Type: application/json" -d '{"name":"Pizza","price":8.50,"stock":2}'
curl -X PUT "http://localhost:8001/product/1" -H "Content-Type: application/json" -d '{"name":"Café Premium","price":3.00,"stock":15}'
