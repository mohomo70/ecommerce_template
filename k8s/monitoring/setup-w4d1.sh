#!/bin/bash

# Week 4 Day 1 - Sentry, Loki/Grafana, dashboards/alerts
# This script sets up monitoring and observability

set -e

echo "🚀 Starting Week 4 Day 1 setup..."

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
kubectl get namespace infra prod monitoring || {
    echo "❌ Namespaces not found. Please run setup-w3d1.sh first."
    exit 1
}

# Add Helm repositories
echo "📦 Adding Helm repositories..."
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Loki
echo "📊 Installing Loki for log aggregation..."
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --create-namespace \
  --values loki-values.yaml \
  --wait

# Install Prometheus
echo "📈 Installing Prometheus for metrics..."
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.enabled=false \
  --set alertmanager.enabled=true \
  --wait

# Install Grafana
echo "📊 Installing Grafana for dashboards..."
helm install grafana grafana/grafana \
  --namespace monitoring \
  --create-namespace \
  --values grafana-values.yaml \
  --wait

# Wait for services to be ready
echo "⏳ Waiting for monitoring services to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=loki -n monitoring --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n monitoring --timeout=300s

# Create Sentry test endpoint
echo "🐛 Creating Sentry test endpoint..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: sentry-test
  namespace: prod
data:
  test.py: |
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    def test_sentry():
        # Test error capture
        try:
            raise Exception("Test error for Sentry")
        except Exception as e:
            sentry_sdk.capture_exception(e)
        
        # Test custom event
        sentry_sdk.capture_message("Sentry test message", level="info")
        
        return "Sentry test completed"
EOF

# Update app secrets with Sentry DSN
echo "🔐 Adding Sentry DSN to app secrets..."
kubectl patch secret app-secrets -n prod --type='json' -p='[{"op": "add", "path": "/data/SENTRY_DSN", "value": "'$(echo -n "https://placeholder@sentry.io/placeholder" | base64)'"}]' || {
    echo "Adding Sentry DSN to secrets..."
    kubectl create secret generic app-secrets \
      --namespace prod \
      --from-literal=SENTRY_DSN="https://placeholder@sentry.io/placeholder" \
      --dry-run=client -o yaml | kubectl apply -f -
}

# Update web config with Sentry DSN
echo "🌐 Adding Sentry DSN to web config..."
kubectl patch configmap web-config -n prod --type='json' -p='[{"op": "add", "path": "/data/NEXT_PUBLIC_SENTRY_DSN", "value": "https://placeholder@sentry.io/placeholder"}]' || {
    echo "Adding Sentry DSN to web config..."
    kubectl create configmap web-config \
      --namespace prod \
      --from-literal=NEXT_PUBLIC_SENTRY_DSN="https://placeholder@sentry.io/placeholder" \
      --dry-run=client -o yaml | kubectl apply -f -
}

# Create Grafana alert rules
echo "🚨 Creating Grafana alert rules..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-alerts
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  alerts.yaml: |
    apiVersion: 1
    alerts:
      - uid: high-error-rate
        title: High Error Rate
        condition: C
        data:
          - refId: A
            queryType: ''
            relativeTimeRange:
              from: 300
              to: 0
            datasource:
              type: prometheus
              uid: prometheus
            model:
              expr: 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100'
              interval: ''
              legendFormat: ''
              refId: A
        noDataState: NoData
        execErrState: Alerting
        for: 2m
        annotations:
          summary: High error rate detected
          description: Error rate is above 1% for more than 2 minutes
        labels:
          severity: warning
      - uid: high-latency
        title: High Latency
        condition: C
        data:
          - refId: A
            queryType: ''
            relativeTimeRange:
              from: 300
              to: 0
            datasource:
              type: prometheus
              uid: prometheus
            model:
              expr: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) * 1000'
              interval: ''
              legendFormat: ''
              refId: A
        noDataState: NoData
        execErrState: Alerting
        for: 5m
        annotations:
          summary: High latency detected
          description: 95th percentile latency is above 300ms for more than 5 minutes
        labels:
          severity: warning
EOF

# Get service URLs
echo "🌍 Getting monitoring service URLs..."
GRAFANA_URL=$(kubectl get svc -n monitoring grafana -o jsonpath='{.spec.clusterIP}')
LOKI_URL=$(kubectl get svc -n monitoring loki -o jsonpath='{.spec.clusterIP}')
PROMETHEUS_URL=$(kubectl get svc -n monitoring prometheus-kube-prometheus-prometheus -o jsonpath='{.spec.clusterIP}')

echo "✅ Week 4 Day 1 setup complete!"
echo ""
echo "📋 Monitoring information:"
echo "Grafana: http://$GRAFANA_URL (admin/admin123)"
echo "Loki: http://$LOKI_URL:3100"
echo "Prometheus: http://$PROMETHEUS_URL:9090"
echo ""
echo "🌐 External URLs (after DNS setup):"
echo "Grafana: https://grafana.staging.example.com"
echo ""
echo "🔍 To verify the setup:"
echo "kubectl get pods -n monitoring"
echo "kubectl get svc -n monitoring"
echo "kubectl get ingress -n monitoring"
echo ""
echo "🧪 To test Sentry:"
echo "1. Update SENTRY_DSN in secrets with real Sentry project DSN"
echo "2. Restart API and web deployments"
echo "3. Trigger an error to see it in Sentry dashboard"
echo ""
echo "📊 To access Grafana:"
echo "kubectl port-forward -n monitoring svc/grafana 3000:80"
echo "Then open http://localhost:3000 (admin/admin123)"
echo ""
echo "🚀 Next step: Run ./setup-w4d2.sh for backups and S3 setup"
