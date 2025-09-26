#!/bin/bash

# Week 3 Day 1 - k3s, certs, DNS setup
# This script sets up the basic Kubernetes infrastructure

set -e

echo "🚀 Starting Week 3 Day 1 setup..."

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user with sudo access."
   exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "📦 Installing kubectl..."
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "📦 Installing Helm..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

# Install k3s
echo "🔧 Installing k3s..."
curl -sfL https://get.k3s.io | sh -s - --disable traefik

# Wait for k3s to be ready
echo "⏳ Waiting for k3s to be ready..."
sleep 30

# Set up kubectl config
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# Verify k3s installation
echo "✅ Verifying k3s installation..."
kubectl get nodes
kubectl get pods -A

# Create namespaces
echo "📁 Creating namespaces..."
kubectl apply -f namespaces.yaml

# Add Helm repositories
echo "📦 Adding Helm repositories..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install nginx-ingress
echo "🌐 Installing nginx-ingress..."
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace infra \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.externalTrafficPolicy=Local

# Wait for ingress controller to be ready
echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace infra \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# Install cert-manager
echo "🔐 Installing cert-manager..."
helm install cert-manager jetstack/cert-manager \
  --namespace infra \
  --create-namespace \
  --set installCRDs=true \
  --set global.leaderElection.namespace=infra

# Wait for cert-manager to be ready
echo "⏳ Waiting for cert-manager to be ready..."
kubectl wait --namespace infra \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=cert-manager \
  --timeout=300s

# Apply ClusterIssuer
echo "📜 Applying ClusterIssuer..."
kubectl apply -f cluster-issuer.yaml

# Get ingress controller external IP
echo "🌍 Getting ingress controller external IP..."
EXTERNAL_IP=$(kubectl get svc -n infra ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$EXTERNAL_IP" ]; then
    EXTERNAL_IP=$(kubectl get svc -n infra ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
fi

echo "✅ Week 3 Day 1 setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update your DNS records to point to: $EXTERNAL_IP"
echo "2. Create A records for:"
echo "   - *.staging.example.com"
echo "   - www.staging.example.com"
echo "   - api.staging.example.com"
echo "3. Wait for DNS propagation (check with: dig +short www.staging.example.com)"
echo "4. Run: ./setup-w3d2.sh for the next step"
echo ""
echo "🔍 To verify the setup:"
echo "kubectl get pods -A"
echo "kubectl get svc -A"
echo "kubectl get ingress -A"
