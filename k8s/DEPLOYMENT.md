# Kubernetes Deployment Guide

This guide walks you through deploying the ecommerce application on Kubernetes using k3s.

## Prerequisites

- Ubuntu 20.04+ VPS with at least 4GB RAM and 2 CPU cores
- Root or sudo access
- Domain name with DNS management access
- GitHub repository with CI/CD secrets configured
- Ports 80, 443, and 6443 open in firewall

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repository-url>
cd ecommerce_template/k8s/infra
```

### 2. Configure Environment Variables

```bash
export DOMAIN="staging.example.com"
export EMAIL="admin@example.com"
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
```

### 3. Run Setup Scripts

```bash
# Day 1: Infrastructure
./setup-w3d1.sh

# Day 2: Database
./setup-w3d2.sh

# Day 3: API
./setup-w3d3.sh

# Day 4: Web
./setup-w3d4.sh

# Day 5: CI/CD and Monitoring
./setup-w3d5.sh
```

## Detailed Setup

### Week 3 Day 1 - Infrastructure

Sets up k3s, cert-manager, and ingress controller.

**What it does:**
- Installs k3s with Traefik disabled
- Creates namespaces (infra, prod, monitoring)
- Installs nginx-ingress controller
- Installs cert-manager with Let's Encrypt
- Creates ClusterIssuer for automatic TLS certificates

**Verification:**
```bash
kubectl get pods -A
kubectl get svc -A
kubectl get ingress -A
```

### Week 3 Day 2 - Database

Deploys Postgres and Redis using Helm charts.

**What it does:**
- Deploys Postgres with persistent storage
- Deploys Redis with persistent storage
- Creates Kubernetes secrets for database credentials
- Creates config maps for application configuration
- Tests database connectivity

**Verification:**
```bash
kubectl get pods -n infra
kubectl get secrets -n prod
kubectl get configmap -n prod
```

### Week 3 Day 3 - API

Deploys the Django API application.

**What it does:**
- Creates persistent volume claims for media and static files
- Deploys API deployment with health checks
- Creates API service and ingress
- Runs database migration job
- Sets up network policies

**Verification:**
```bash
kubectl get pods -n prod
curl https://api.staging.example.com/api/healthz
```

### Week 3 Day 4 - Web

Deploys the Next.js web application.

**What it does:**
- Creates web config map
- Deploys web deployment with health checks
- Creates web service and ingress
- Updates API ingress for Stripe webhook
- Tests web application

**Verification:**
```bash
kubectl get pods -n prod
curl https://www.staging.example.com
```

### Week 3 Day 5 - CI/CD and Monitoring

Sets up continuous deployment and auto-scaling.

**What it does:**
- Deploys Horizontal Pod Autoscalers
- Creates CI/CD GitHub Actions workflow
- Sets up Docker images for both applications
- Creates monitoring and testing scripts
- Provides rollback testing

**Verification:**
```bash
kubectl get hpa -n prod
./load-test.sh
./rollback-test.sh
```

## Configuration

### Environment Variables

The following environment variables are automatically configured:

**Database:**
- `DB_NAME`: ecommerce
- `DB_USER`: ecommerce
- `DB_PASSWORD`: Generated automatically
- `DB_HOST`: pg-postgresql.infra.svc.cluster.local
- `DB_PORT`: 5432

**Redis:**
- `REDIS_PASSWORD`: Generated automatically
- `REDIS_HOST`: redis-master.infra.svc.cluster.local
- `REDIS_PORT`: 6379

**Django:**
- `DJANGO_SECRET_KEY`: Generated automatically
- `DEBUG`: False
- `ALLOWED_HOSTS`: www.staging.example.com,api.staging.example.com

**Next.js:**
- `NEXT_PUBLIC_API_BASE_URL`: https://api.staging.example.com
- `NODE_ENV`: production

### Secrets Management

All sensitive data is stored in Kubernetes secrets:

```bash
# View secrets
kubectl get secrets -n prod

# View secret details
kubectl describe secret app-secrets -n prod
```

### Resource Limits

**API Pods:**
- CPU: 250m request, 500m limit
- Memory: 256Mi request, 512Mi limit

**Web Pods:**
- CPU: 250m request, 500m limit
- Memory: 256Mi request, 512Mi limit

**Auto-scaling:**
- Min replicas: 2
- Max replicas: 10
- CPU threshold: 70%
- Memory threshold: 80%

## Monitoring

### Health Checks

Both applications have health check endpoints:

- API: `https://api.staging.example.com/api/healthz`
- Web: `https://www.staging.example.com/`

### Monitoring Scripts

```bash
# View cluster status
./monitor.sh

# Test auto-scaling
./load-test.sh

# Test rollback
./rollback-test.sh
```

### Useful Commands

```bash
# Get all resources
kubectl get all -A

# View pod logs
kubectl logs -n prod -l app=api

# Scale deployment
kubectl scale deployment api-deployment -n prod --replicas=3

# Rollback deployment
kubectl rollout undo deployment/api-deployment -n prod

# View HPA status
kubectl get hpa -n prod

# Port forward for debugging
kubectl -n infra port-forward svc/pg-postgresql 5433:5432
```

## CI/CD

### GitHub Actions

The CI/CD pipeline automatically:

1. **Tests:** Runs Python and Node.js tests
2. **Builds:** Creates Docker images for both applications
3. **Scans:** Runs Trivy vulnerability scans
4. **Deploys:** Updates Kubernetes deployments
5. **Verifies:** Checks deployment status

### Required Secrets

Configure these secrets in your GitHub repository:

- `KUBECONFIG`: Base64 encoded kubeconfig file
- `GITHUB_TOKEN`: Automatically provided

### Manual Deployment

```bash
# Update image tags
sed -i "s|ghcr.io/your-username/ecommerce-api:latest|ghcr.io/your-username/ecommerce-api:v1.0.0|g" k8s/apps/api/deployment.yaml

# Apply changes
kubectl apply -f k8s/apps/api/deployment.yaml
kubectl rollout status deployment/api-deployment -n prod
```

## Troubleshooting

### Common Issues

1. **Pod startup failures:**
   ```bash
   kubectl describe pod <pod-name> -n prod
   kubectl logs <pod-name> -n prod
   ```

2. **Database connection issues:**
   ```bash
   kubectl -n infra port-forward svc/pg-postgresql 5433:5432
   psql -h 127.0.0.1 -p 5433 -U ecommerce -d ecommerce
   ```

3. **Certificate issues:**
   ```bash
   kubectl describe certificate -n prod
   kubectl logs -n infra -l app.kubernetes.io/name=cert-manager
   ```

4. **Ingress issues:**
   ```bash
   kubectl describe ingress -n prod
   kubectl get svc -n infra ingress-nginx-controller
   ```

### Logs

```bash
# API logs
kubectl logs -n prod -l app=api

# Web logs
kubectl logs -n prod -l app=web

# Ingress logs
kubectl logs -n infra -l app.kubernetes.io/name=ingress-nginx

# Cert-manager logs
kubectl logs -n infra -l app.kubernetes.io/name=cert-manager
```

## Security

### Network Policies

Network policies restrict pod-to-pod communication:

- API pods can only connect to database and Redis
- Web pods can only connect to API
- Database and Redis are isolated to infra namespace

### Secrets

- All secrets are stored in Kubernetes secrets
- No sensitive data in container images
- Secrets are not logged or exposed in environment variables

### TLS

- All external traffic uses HTTPS
- Certificates are automatically managed by cert-manager
- Let's Encrypt staging certificates for testing

## Backup

### Database Backup

```bash
# Create backup
kubectl exec -n infra pg-postgresql-0 -- pg_dump -U ecommerce ecommerce > backup.sql

# Restore backup
kubectl exec -i -n infra pg-postgresql-0 -- psql -U ecommerce ecommerce < backup.sql
```

### Persistent Volumes

```bash
# List PVCs
kubectl get pvc -n prod

# Backup PVC data
kubectl exec -n prod <pod-name> -- tar -czf /tmp/backup.tar.gz /app/media
```

## Scaling

### Horizontal Scaling

```bash
# Scale API
kubectl scale deployment api-deployment -n prod --replicas=5

# Scale Web
kubectl scale deployment web-deployment -n prod --replicas=5
```

### Vertical Scaling

Update resource limits in deployment manifests:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## Maintenance

### Updates

1. Update image tags in deployment manifests
2. Apply changes: `kubectl apply -f k8s/apps/api/deployment.yaml`
3. Monitor rollout: `kubectl rollout status deployment/api-deployment -n prod`

### Cleanup

```bash
# Delete all resources
kubectl delete namespace prod infra monitoring

# Uninstall k3s
sudo /usr/local/bin/k3s-uninstall.sh
```

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review pod logs and events
3. Check GitHub Issues
4. Consult Kubernetes documentation
