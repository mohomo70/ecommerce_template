#!/bin/bash

# Week 3 Day 5 - CI/CD, HPA, rollback drill
# This script sets up CI/CD and monitoring

set -e

echo "🚀 Starting Week 3 Day 5 setup..."

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

# Verify applications are running
echo "🔍 Verifying applications are running..."
kubectl get pods -n prod -l app=api || {
    echo "❌ API not found. Please run setup-w3d3.sh first."
    exit 1
}

kubectl get pods -n prod -l app=web || {
    echo "❌ Web not found. Please run setup-w3d4.sh first."
    exit 1
}

# Deploy HPA
echo "📈 Deploying Horizontal Pod Autoscalers..."
kubectl apply -f ../apps/api/hpa.yaml
kubectl apply -f ../apps/web/hpa.yaml

# Wait for HPA to be ready
echo "⏳ Waiting for HPA to be ready..."
kubectl wait --for=condition=Ready hpa/api-hpa -n prod --timeout=60s
kubectl wait --for=condition=Ready hpa/web-hpa -n prod --timeout=60s

# Verify HPA
echo "🔍 Verifying HPA..."
kubectl get hpa -n prod

# Create rollback test script
echo "🔄 Creating rollback test script..."
cat << 'EOF' > rollback-test.sh
#!/bin/bash

echo "🧪 Starting rollback test..."

# Get current image
CURRENT_IMAGE=$(kubectl get deployment api-deployment -n prod -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "Current API image: $CURRENT_IMAGE"

# Deploy a bad image
echo "🚫 Deploying bad image..."
kubectl set image deployment/api-deployment api=nginx:1.0 -n prod

# Wait for rollout
echo "⏳ Waiting for bad deployment to rollout..."
kubectl rollout status deployment/api-deployment -n prod --timeout=60s

# Check if pods are failing
echo "🔍 Checking pod status..."
kubectl get pods -n prod -l app=api

# Rollback to previous version
echo "↩️ Rolling back to previous version..."
kubectl rollout undo deployment/api-deployment -n prod

# Wait for rollback to complete
echo "⏳ Waiting for rollback to complete..."
kubectl rollout status deployment/api-deployment -n prod --timeout=60s

# Verify rollback
echo "✅ Verifying rollback..."
kubectl get pods -n prod -l app=api
kubectl get deployment api-deployment -n prod

echo "🎉 Rollback test completed!"
EOF

chmod +x rollback-test.sh

# Create load test script
echo "📊 Creating load test script..."
cat << 'EOF' > load-test.sh
#!/bin/bash

echo "📈 Starting load test..."

# Get API service URL
API_URL=$(kubectl get svc api-service -n prod -o jsonpath='{.spec.clusterIP}')
echo "API URL: http://$API_URL"

# Install hey if not available
if ! command -v hey &> /dev/null; then
    echo "📦 Installing hey load testing tool..."
    wget -O hey https://github.com/rakyll/hey/releases/download/v0.1.4/hey_linux_amd64
    chmod +x hey
    sudo mv hey /usr/local/bin/
fi

# Run load test
echo "🚀 Running load test..."
hey -n 1000 -c 10 -m GET http://$API_URL/api/healthz

echo "📊 Load test completed!"
echo "Check HPA status: kubectl get hpa -n prod"
EOF

chmod +x load-test.sh

# Create monitoring script
echo "📊 Creating monitoring script..."
cat << 'EOF' > monitor.sh
#!/bin/bash

echo "📊 Kubernetes Cluster Status"
echo "=========================="

echo "🔍 Pods:"
kubectl get pods -A

echo ""
echo "📈 HPA Status:"
kubectl get hpa -A

echo ""
echo "🌐 Services:"
kubectl get svc -A

echo ""
echo "🌍 Ingress:"
kubectl get ingress -A

echo ""
echo "💾 PVCs:"
kubectl get pvc -A

echo ""
echo "🔐 Secrets:"
kubectl get secrets -A

echo ""
echo "📋 ConfigMaps:"
kubectl get configmaps -A

echo ""
echo "🛡️ Network Policies:"
kubectl get networkpolicies -A
EOF

chmod +x monitor.sh

echo "✅ Week 3 Day 5 setup complete!"
echo ""
echo "📋 CI/CD and Monitoring information:"
echo "HPA Status: kubectl get hpa -n prod"
echo "Rollback Test: ./rollback-test.sh"
echo "Load Test: ./load-test.sh"
echo "Monitoring: ./monitor.sh"
echo ""
echo "🔍 To verify the setup:"
echo "kubectl get hpa -n prod"
echo "kubectl get pods -n prod"
echo ""
echo "🧪 To test auto-scaling:"
echo "1. Run: ./load-test.sh"
echo "2. Watch: kubectl get hpa -n prod -w"
echo "3. Check: kubectl get pods -n prod"
echo ""
echo "🔄 To test rollback:"
echo "1. Run: ./rollback-test.sh"
echo "2. Verify: kubectl get pods -n prod"
echo ""
echo "📊 To monitor the cluster:"
echo "Run: ./monitor.sh"
echo ""
echo "🎉 Week 3 setup complete! Your ecommerce application is now running on Kubernetes!"
echo ""
echo "📋 Next steps:"
echo "1. Set up your domain DNS records"
echo "2. Update image references in deployment manifests"
echo "3. Configure GitHub secrets for CI/CD"
echo "4. Set up monitoring and alerting"
echo "5. Configure backup strategies"
