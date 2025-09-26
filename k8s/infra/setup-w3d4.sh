#!/bin/bash

# Week 3 Day 4 - Web manifests, env wiring, Stripe webhook
# This script sets up the web application

set -e

echo "🚀 Starting Week 3 Day 4 setup..."

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

# Verify API is running
echo "🚀 Verifying API is running..."
kubectl get pods -n prod -l app=api || {
    echo "❌ API not found. Please run setup-w3d3.sh first."
    exit 1
}

# Create web config map
echo "📋 Creating web config map..."
kubectl apply -f ../apps/web/configmap.yaml

# Deploy web application
echo "🌐 Deploying web application..."
kubectl apply -f ../apps/web/deployment.yaml
kubectl apply -f ../apps/web/service.yaml
kubectl apply -f ../apps/web/ingress.yaml

# Update API ingress for Stripe webhook
echo "💳 Updating API ingress for Stripe webhook..."
kubectl apply -f ../apps/api/ingress.yaml

# Wait for web deployment to be ready
echo "⏳ Waiting for web deployment to be ready..."
kubectl wait --for=condition=available deployment/web-deployment -n prod --timeout=300s

# Verify web application is running
echo "🔍 Verifying web application is running..."
kubectl get pods -n prod -l app=web

# Test web application
echo "🧪 Testing web application..."
kubectl run web-test --rm -i --restart=Never \
  --namespace prod \
  --image=curlimages/curl:latest \
  -- curl -f http://web-service.prod.svc.cluster.local/ || {
    echo "❌ Web application test failed"
    exit 1
}

# Get ingress external IP
echo "🌍 Getting ingress external IP..."
EXTERNAL_IP=$(kubectl get svc -n infra ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$EXTERNAL_IP" ]; then
    EXTERNAL_IP=$(kubectl get svc -n infra ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
fi

echo "✅ Week 3 Day 4 setup complete!"
echo ""
echo "📋 Web application information:"
echo "Internal URL: http://web-service.prod.svc.cluster.local"
echo "External URL: https://www.staging.example.com"
echo "API URL: https://api.staging.example.com"
echo "Stripe Webhook URL: https://api.staging.example.com/api/payments/webhook"
echo "External IP: $EXTERNAL_IP"
echo ""
echo "🔍 To verify the setup:"
echo "kubectl get pods -n prod"
echo "kubectl get svc -n prod"
echo "kubectl get ingress -n prod"
echo ""
echo "🧪 To test the applications:"
echo "curl https://www.staging.example.com"
echo "curl https://api.staging.example.com/api/healthz"
echo ""
echo "💳 To test Stripe webhook (requires Stripe CLI):"
echo "stripe listen --forward-to https://api.staging.example.com/api/payments/webhook"
echo ""
echo "🚀 Next step: Run ./setup-w3d5.sh to set up CI/CD and monitoring"
