#!/bin/bash

# Week 4 Day 2 - Backups + restore; media to S3
# This script sets up backup and S3 media storage

set -e

echo "🚀 Starting Week 4 Day 2 setup..."

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

# Create AWS credentials secret
echo "🔐 Creating AWS credentials secret..."
kubectl create secret generic aws-credentials \
  --namespace infra \
  --from-literal=access-key-id="${AWS_ACCESS_KEY_ID:-placeholder}" \
  --from-literal=secret-access-key="${AWS_SECRET_ACCESS_KEY:-placeholder}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Update app secrets with AWS credentials
echo "🔐 Adding AWS credentials to app secrets..."
kubectl patch secret app-secrets -n prod --type='json' -p='[{"op": "add", "path": "/data/AWS_ACCESS_KEY_ID", "value": "'$(echo -n "${AWS_ACCESS_KEY_ID:-placeholder}" | base64)'"}]' || {
    kubectl create secret generic app-secrets \
      --namespace prod \
      --from-literal=AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-placeholder}" \
      --dry-run=client -o yaml | kubectl apply -f -
}

kubectl patch secret app-secrets -n prod --type='json' -p='[{"op": "add", "path": "/data/AWS_SECRET_ACCESS_KEY", "value": "'$(echo -n "${AWS_SECRET_ACCESS_KEY:-placeholder}" | base64)'"}]' || {
    kubectl create secret generic app-secrets \
      --namespace prod \
      --from-literal=AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-placeholder}" \
      --dry-run=client -o yaml | kubectl apply -f -
}

# Add S3 configuration to app secrets
echo "📦 Adding S3 configuration to app secrets..."
kubectl patch secret app-secrets -n prod --type='json' -p='[{"op": "add", "path": "/data/AWS_STORAGE_BUCKET_NAME", "value": "'$(echo -n "${AWS_STORAGE_BUCKET_NAME:-ecommerce-media}" | base64)'"}]' || {
    kubectl create secret generic app-secrets \
      --namespace prod \
      --from-literal=AWS_STORAGE_BUCKET_NAME="${AWS_STORAGE_BUCKET_NAME:-ecommerce-media}" \
      --dry-run=client -o yaml | kubectl apply -f -
}

kubectl patch secret app-secrets -n prod --type='json' -p='[{"op": "add", "path": "/data/AWS_S3_REGION_NAME", "value": "'$(echo -n "${AWS_S3_REGION_NAME:-us-east-1}" | base64)'"}]' || {
    kubectl create secret generic app-secrets \
      --namespace prod \
      --from-literal=AWS_S3_REGION_NAME="${AWS_S3_REGION_NAME:-us-east-1}" \
      --dry-run=client -o yaml | kubectl apply -f -
}

# Deploy backup CronJob
echo "💾 Deploying PostgreSQL backup CronJob..."
kubectl apply -f postgres-backup-cronjob.yaml

# Create restore job (for testing)
echo "🔄 Creating restore job template..."
kubectl apply -f postgres-restore-job.yaml

# Update API deployment to include S3 support
echo "🚀 Updating API deployment for S3 support..."
kubectl patch deployment api-deployment -n prod --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": "AWS_ACCESS_KEY_ID", "valueFrom": {"secretKeyRef": {"name": "app-secrets", "key": "AWS_ACCESS_KEY_ID"}}}}]' || true

kubectl patch deployment api-deployment -n prod --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": {"secretKeyRef": {"name": "app-secrets", "key": "AWS_SECRET_ACCESS_KEY"}}}}]' || true

kubectl patch deployment api-deployment -n prod --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": "AWS_STORAGE_BUCKET_NAME", "valueFrom": {"secretKeyRef": {"name": "app-secrets", "key": "AWS_STORAGE_BUCKET_NAME"}}}}]' || true

kubectl patch deployment api-deployment -n prod --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": "AWS_S3_REGION_NAME", "valueFrom": {"secretKeyRef": {"name": "app-secrets", "key": "AWS_S3_REGION_NAME"}}}}]' || true

# Restart API deployment to pick up new environment variables
echo "🔄 Restarting API deployment..."
kubectl rollout restart deployment/api-deployment -n prod

# Wait for rollout to complete
echo "⏳ Waiting for API rollout to complete..."
kubectl rollout status deployment/api-deployment -n prod --timeout=300s

# Create media migration job
echo "📁 Creating media migration job..."
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: media-migration-job
  namespace: prod
spec:
  template:
    spec:
      containers:
      - name: migration
        image: ghcr.io/your-username/ecommerce-api:latest
        command:
        - /bin/bash
        - -c
        - |
          echo "Starting media migration to S3..."
          python manage.py migrate_media_to_s3 --dry-run
          echo "Media migration job completed"
        envFrom:
        - secretRef:
            name: app-secrets
        - configMapRef:
            name: app-config
        env:
        - name: DATABASE_URL
          value: "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)"
        - name: CELERY_BROKER_URL
          value: "redis://:$(REDIS_PASSWORD)@$(REDIS_HOST):$(REDIS_PORT)/0"
        volumeMounts:
        - name: media-volume
          mountPath: /app/media
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: media-volume
        persistentVolumeClaim:
          claimName: media-pvc
      restartPolicy: Never
  backoffLimit: 3
EOF

# Wait for migration job to complete
echo "⏳ Waiting for media migration job to complete..."
kubectl wait --for=condition=complete job/media-migration-job -n prod --timeout=300s

# Check migration job logs
echo "📋 Media migration job logs:"
kubectl logs -n prod -l job-name=media-migration-job

# Create backup verification script
echo "🧪 Creating backup verification script..."
cat << 'EOF' > verify-backup.sh
#!/bin/bash

echo "🔍 Verifying backup setup..."

# Check if backup CronJob is scheduled
echo "Checking backup CronJob..."
kubectl get cronjob postgres-backup -n infra

# List recent backups (if S3 is configured)
if [ ! -z "$AWS_ACCESS_KEY_ID" ] && [ ! -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Listing recent backups in S3..."
    aws s3 ls s3://ecommerce-backups/postgres/ --region us-east-1 | head -5
else
    echo "AWS credentials not configured. Skipping S3 verification."
fi

# Check restore job
echo "Checking restore job..."
kubectl get job postgres-restore -n infra

echo "✅ Backup verification complete!"
EOF

chmod +x verify-backup.sh

echo "✅ Week 4 Day 2 setup complete!"
echo ""
echo "📋 Backup and S3 information:"
echo "Backup CronJob: Daily at 2 AM UTC"
echo "S3 Bucket: ${AWS_STORAGE_BUCKET_NAME:-ecommerce-media}"
echo "S3 Region: ${AWS_S3_REGION_NAME:-us-east-1}"
echo ""
echo "🔍 To verify the setup:"
echo "kubectl get cronjob -n infra"
echo "kubectl get job -n infra"
echo "kubectl get secrets -n prod | grep aws"
echo ""
echo "🧪 To test backup:"
echo "1. Manually trigger backup: kubectl create job --from=cronjob/postgres-backup postgres-backup-manual -n infra"
echo "2. Check S3 bucket for backup files"
echo "3. Run restore test: kubectl create job --from=job/postgres-restore postgres-restore-test -n infra"
echo ""
echo "📁 To migrate media to S3:"
echo "1. Update AWS credentials in secrets"
echo "2. Run: kubectl create job --from=job/media-migration-job media-migration-manual -n prod"
echo "3. Check S3 bucket for migrated files"
echo ""
echo "🚀 Next step: Run ./setup-w4d3.sh for security hardening"
