# installer et activer env python

```bash
# Service Payment
cd payment-service && pip install -r requirements.txt
cd payment-service && python app.py

# Service Barrier
cd barrier-service && pip install -r requirements.txt
cd barrier-service && python app.py

# Service Products
cd product-service && pip install -r requirements.txt
cd product-service && python app.py

# Service Alarm
cd alarm-service && pip install -r requirements.txt
cd alarm-service && python app.py
```

```bash
curl "http://localhost:8000/"          # Paiement
curl "http://localhost:8001/products"  # Produits
curl "http://localhost:8002/status"    # Barrière
curl "http://localhost:8003/health"    # Alarme
```

### Achat Normal

1. **Client prend un produit** → Service Product publie "produit_pris" via MQTT
2. **Barrière surveille** → Timer de 10 secondes démarre
3. **Client paie** → Service Payment publie "paiement_réussi"
4. **Barrière s'ouvre** → Accès autorisé pendant 5 secondes
5. **Fermeture auto** → Barrière se referme automatiquement

```bash
curl "http://localhost:8001/product/1"

curl -X POST "http://localhost:8000/payer?produit=Cafe&montant=2.50"

curl "http://localhost:8002/status"

curl "http://localhost:8003/alarmes"
```

### Vol/Oubli de Paiement

1. **Client prend un produit** → Produit marqué comme pris
2. **Pas de paiement** → Timer de 10s expire
3. **Alarme déclenchée** → Message d'alarme sécurité envoyé
4. **Barrière reste fermée** → Accès bloqué

```bash
curl "http://localhost:8001/product/2"

#10s sans payer

# 3. alarme crée auto
curl "http://localhost:8003/alarmes/security"

# 4. Barrière fermée
curl "http://localhost:8002/status"
```

### Tests Individuels des Services

#### Service Paiement

```bash
curl -X POST "http://localhost:8000/payer?produit=Croissant&montant=1.50"
curl "http://localhost:8000/paiements"
```

#### Service Barrière

```bash
curl "http://localhost:8002/status"
curl -X POST "http://localhost:8002/ouvrir"
curl -X POST "http://localhost:8002/fermer"
```

#### Service Alarme

```bash
curl -X POST "http://localhost:8003/alarme?message=test-manuel"
curl "http://localhost:8003/alarmes"
curl "http://localhost:8003/alarmes/security"
```

#### Service Produits

```bash
curl "http://localhost:8001/products"
curl "http://localhost:8001/product/1"
curl "http://localhost:8001/product/2"
```
