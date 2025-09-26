#!/bin/bash

# Week 3 Day 2 - Postgres & Redis via Helm, secrets, connectivity
# This script sets up the database infrastructure

set -e

echo "🚀 Starting Week 3 Day 2 setup..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please run setup-w3d1.sh first."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ helm not found. Please run setup-w3d1.sh first."
    exit 1
fi

# Verify namespaces exist
echo "📁 Verifying namespaces..."
kubectl get namespace infra prod || {
    echo "❌ Namespaces not found. Please run setup-w3d1.sh first."
    exit 1
}

# Deploy Postgres
echo "🐘 Deploying Postgres..."
helm install pg bitnami/postgresql \
  --namespace infra \
  --values values-postgres.yaml \
  --wait

# Wait for Postgres to be ready
echo "⏳ Waiting for Postgres to be ready..."
kubectl wait --namespace infra \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=postgresql \
  --timeout=300s

# Deploy Redis
echo "🔴 Deploying Redis..."
helm install redis bitnami/redis \
  --namespace infra \
  --values values-redis.yaml \
  --wait

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --namespace infra \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=redis \
  --timeout=300s

# Get database credentials
echo "🔑 Getting database credentials..."
PG_PASSWORD=$(kubectl get secret --namespace infra pg-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
PG_USER_PASSWORD=$(kubectl get secret --namespace infra pg-postgresql -o jsonpath="{.data.password}" | base64 -d)
REDIS_PASSWORD=$(kubectl get secret --namespace infra redis -o jsonpath="{.data.redis-password}" | base64 -d)

# Create app secrets
echo "🔐 Creating app secrets..."
kubectl create secret generic app-secrets \
  --namespace prod \
  --from-literal=DB_NAME=ecommerce \
  --from-literal=DB_USER=ecommerce \
  --from-literal=DB_PASSWORD=$PG_USER_PASSWORD \
  --from-literal=DB_HOST=pg-postgresql.infra.svc.cluster.local \
  --from-literal=DB_PORT=5432 \
  --from-literal=REDIS_PASSWORD=$REDIS_PASSWORD \
  --from-literal=REDIS_HOST=redis-master.infra.svc.cluster.local \
  --from-literal=REDIS_PORT=6379 \
  --from-literal=DJANGO_SECRET_KEY=$(openssl rand -base64 32) \
  --from-literal=STRIPE_PUBLISHABLE_KEY=pk_test_placeholder \
  --from-literal=STRIPE_SECRET_KEY=sk_test_placeholder \
  --from-literal=STRIPE_WEBHOOK_SECRET=whsec_placeholder \
  --dry-run=client -o yaml | kubectl apply -f -

# Create config map for non-sensitive configuration
echo "📋 Creating config map..."
kubectl create configmap app-config \
  --namespace prod \
  --from-literal=DEBUG=False \
  --from-literal=ALLOWED_HOSTS=www.staging.example.com,api.staging.example.com \
  --from-literal=EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
  --from-literal=CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis-master.infra.svc.cluster.local:6379/0 \
  --dry-run=client -o yaml | kubectl apply -f -

# Test connectivity
echo "🔍 Testing database connectivity..."

# Test Postgres connectivity
echo "Testing Postgres connection..."
kubectl run postgres-test --rm -i --restart=Never \
  --namespace prod \
  --image=postgres:13 \
  --env="PGPASSWORD=$PG_USER_PASSWORD" \
  -- psql -h pg-postgresql.infra.svc.cluster.local -U ecommerce -d ecommerce -c "SELECT 1;" || {
    echo "❌ Postgres connection test failed"
    exit 1
}

# Test Redis connectivity
echo "Testing Redis connection..."
kubectl run redis-test --rm -i --restart=Never \
  --namespace prod \
  --image=redis:7-alpine \
  -- redis-cli -h redis-master.infra.svc.cluster.local -a $REDIS_PASSWORD ping || {
    echo "❌ Redis connection test failed"
    exit 1
}

# Create network policy for database access
echo "🛡️ Creating network policy..."
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: infra
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
EOF

echo "✅ Week 3 Day 2 setup complete!"
echo ""
echo "📋 Database information:"
echo "Postgres:"
echo "  Host: pg-postgresql.infra.svc.cluster.local"
echo "  Port: 5432"
echo "  Database: ecommerce"
echo "  Username: ecommerce"
echo "  Password: $PG_USER_PASSWORD"
echo ""
echo "Redis:"
echo "  Host: redis-master.infra.svc.cluster.local"
echo "  Port: 6379"
echo "  Password: $REDIS_PASSWORD"
echo ""
echo "🔍 To verify the setup:"
echo "kubectl get pods -n infra"
echo "kubectl get secrets -n prod"
echo "kubectl get configmap -n prod"
echo "kubectl get networkpolicy -n prod"
echo ""
echo "🚀 Next step: Run ./setup-w3d3.sh to deploy the API"
