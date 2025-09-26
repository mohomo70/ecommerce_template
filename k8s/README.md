# Kubernetes Deployment

This directory contains Kubernetes manifests and configuration for deploying the ecommerce application.

## Directory Structure

```
k8s/
├── infra/                 # Infrastructure components
│   ├── namespaces.yaml    # Namespace definitions
│   ├── cluster-issuer.yaml # cert-manager ClusterIssuer
│   ├── values-postgres.yaml # Helm values for Postgres
│   ├── values-redis.yaml  # Helm values for Redis
│   ├── setup-w3d1.sh     # Week 3 Day 1 setup script
│   └── test-ingress.yaml  # Test ingress for verification
├── apps/
│   ├── api/              # API application manifests
│   └── web/              # Web application manifests
├── base/                 # Base Kustomize configurations
└── overlays/             # Environment-specific overlays
    ├── staging/          # Staging environment
    └── prod/             # Production environment
```

## Prerequisites

- Ubuntu 20.04+ VPS with at least 2GB RAM and 2 CPU cores
- Root or sudo access
- Domain name with DNS management access
- Ports 80, 443, and 6443 open in firewall

## Quick Start

### Week 3 Day 1 - Infrastructure Setup

1. **Clone the repository and navigate to k8s directory:**
   ```bash
   git clone <repository-url>
   cd ecommerce_template/k8s/infra
   ```

2. **Run the setup script:**
   ```bash
   ./setup-w3d1.sh
   ```

3. **Update DNS records:**
   - Point `*.staging.example.com` to your VPS IP
   - Point `www.staging.example.com` to your VPS IP
   - Point `api.staging.example.com` to your VPS IP

4. **Verify the setup:**
   ```bash
   kubectl get pods -A
   kubectl get svc -A
   kubectl get ingress -A
   ```

### Week 3 Day 2 - Database Setup

1. **Deploy Postgres and Redis:**
   ```bash
   ./setup-w3d2.sh
   ```

2. **Verify database connectivity:**
   ```bash
   kubectl -n infra port-forward svc/pg-postgresql 5433:5432
   psql -h 127.0.0.1 -p 5433 -U postgres
   ```

### Week 3 Day 3 - API Deployment

1. **Deploy API application:**
   ```bash
   ./setup-w3d3.sh
   ```

2. **Verify API is running:**
   ```bash
   curl https://api.staging.example.com/healthz
   ```

### Week 3 Day 4 - Web Deployment

1. **Deploy web application:**
   ```bash
   ./setup-w3d4.sh
   ```

2. **Verify web application:**
   ```bash
   curl https://www.staging.example.com
   ```

### Week 3 Day 5 - CI/CD and Monitoring

1. **Set up CI/CD:**
   ```bash
   ./setup-w3d5.sh
   ```

2. **Verify auto-scaling:**
   ```bash
   kubectl get hpa -A
   ```

## Environment Variables

The following environment variables need to be set in your VPS:

```bash
export DOMAIN="staging.example.com"
export EMAIL="admin@example.com"
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export DJANGO_SECRET_KEY="your-secret-key"
export DB_PASSWORD="your-db-password"
export REDIS_PASSWORD="your-redis-password"
```

## Troubleshooting

### Common Issues

1. **k3s installation fails:**
   - Ensure you have sufficient resources (2GB RAM, 2 CPU cores)
   - Check if ports 80, 443, 6443 are open

2. **DNS resolution issues:**
   - Wait for DNS propagation (can take up to 24 hours)
   - Use `dig +short www.staging.example.com` to check resolution

3. **Certificate issues:**
   - Check cert-manager logs: `kubectl logs -n infra -l app.kubernetes.io/name=cert-manager`
   - Verify DNS is pointing to the correct IP

4. **Pod startup issues:**
   - Check pod logs: `kubectl logs -n prod <pod-name>`
   - Check resource limits and requests

### Useful Commands

```bash
# Get all resources
kubectl get all -A

# Check pod logs
kubectl logs -n prod <pod-name>

# Port forward for testing
kubectl -n infra port-forward svc/pg-postgresql 5433:5432

# Check ingress status
kubectl describe ingress -n prod

# Check certificate status
kubectl describe certificate -n prod

# Scale deployment
kubectl scale deployment api-deployment -n prod --replicas=3

# Rollback deployment
kubectl rollout undo deployment/api-deployment -n prod
```

## Security Considerations

- All secrets are stored in Kubernetes secrets
- Network policies restrict pod-to-pod communication
- TLS certificates are automatically managed by cert-manager
- Regular security updates should be applied to the VPS

## Monitoring

- Basic monitoring is available through Kubernetes metrics
- For production, consider adding Prometheus and Grafana
- Log aggregation can be set up with ELK stack or similar

## Backup

- Database backups should be configured for production
- Consider using Velero for cluster-level backups
- Test restore procedures regularly
