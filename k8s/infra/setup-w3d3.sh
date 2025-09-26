#!/bin/bash

# Week 3 Day 3 - API manifests, media strategy, migration job
# This script sets up the API application

set -e

echo "🚀 Starting Week 3 Day 3 setup..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please run setup-w3d1.sh first."
    exit 1
fi

# Verify namespaces exist
echo "📁 Verifying namespaces..."
kubectl get namespace infra prod || {
    echo "❌ Namespaces not found. Please run setup-w3d1.sh first."
    exit 1
}

# Verify database is running
echo "🐘 Verifying database is running..."
kubectl get pods -n infra -l app.kubernetes.io/name=postgresql || {
    echo "❌ Postgres not found. Please run setup-w3d2.sh first."
    exit 1
}

kubectl get pods -n infra -l app.kubernetes.io/name=redis || {
    echo "❌ Redis not found. Please run setup-w3d2.sh first."
    exit 1
}

# Create PVCs
echo "💾 Creating persistent volume claims..."
kubectl apply -f ../apps/api/pvc.yaml

# Wait for PVCs to be bound
echo "⏳ Waiting for PVCs to be bound..."
kubectl wait --for=condition=Bound pvc/media-pvc -n prod --timeout=60s
kubectl wait --for=condition=Bound pvc/static-pvc -n prod --timeout=60s

# Deploy API
echo "🚀 Deploying API application..."
kubectl apply -f ../apps/api/deployment.yaml
kubectl apply -f ../apps/api/service.yaml
kubectl apply -f ../apps/api/ingress.yaml
kubectl apply -f ../apps/api/network-policy.yaml

# Wait for API deployment to be ready
echo "⏳ Waiting for API deployment to be ready..."
kubectl wait --for=condition=available deployment/api-deployment -n prod --timeout=300s

# Run migration job
echo "🔄 Running database migration job..."
kubectl apply -f ../apps/api/migration-job.yaml

# Wait for migration job to complete
echo "⏳ Waiting for migration job to complete..."
kubectl wait --for=condition=complete job/api-migration-job -n prod --timeout=300s

# Check migration job logs
echo "📋 Migration job logs:"
kubectl logs -n prod -l job-name=api-migration-job

# Verify API is running
echo "🔍 Verifying API is running..."
kubectl get pods -n prod -l app=api

# Test API health endpoint
echo "🏥 Testing API health endpoint..."
kubectl run api-test --rm -i --restart=Never \
  --namespace prod \
  --image=curlimages/curl:latest \
  -- curl -f http://api-service.prod.svc.cluster.local/api/healthz || {
    echo "❌ API health check failed"
    exit 1
}

# Get ingress external IP
echo "🌍 Getting ingress external IP..."
EXTERNAL_IP=$(kubectl get svc -n infra ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$EXTERNAL_IP" ]; then
    EXTERNAL_IP=$(kubectl get svc -n infra ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
fi

echo "✅ Week 3 Day 3 setup complete!"
echo ""
echo "📋 API information:"
echo "Internal URL: http://api-service.prod.svc.cluster.local"
echo "External URL: https://api.staging.example.com"
echo "External IP: $EXTERNAL_IP"
echo ""
echo "🔍 To verify the setup:"
echo "kubectl get pods -n prod"
echo "kubectl get svc -n prod"
echo "kubectl get ingress -n prod"
echo "kubectl get pvc -n prod"
echo ""
echo "🧪 To test the API:"
echo "curl https://api.staging.example.com/api/healthz"
echo ""
echo "🚀 Next step: Run ./setup-w3d4.sh to deploy the web application"
