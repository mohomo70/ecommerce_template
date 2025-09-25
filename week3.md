# Week 3 — Kubernetes on VPS (Detailed Task Cards)

## W3D1 — k3s, certs, DNS

### 68) Install k3s
**Description (what & why):** Sets up a lightweight Kubernetes cluster on your VPS so you can deploy production-like workloads with minimal overhead.  
**How:** Use the official `get.k3s.io` script; disable built-in Traefik if you plan to use nginx-ingress.  
**Do:**  
```bash
curl -sfL https://get.k3s.io | sh -s - --disable traefik
sudo kubectl get nodes
```
**DoD:**  
- `kubectl get nodes` shows the node in `Ready` state.  
- `kubectl get pods -A` shows all system pods running.

### 69) Namespaces
**Description (what & why):** Logical isolation for workloads (infra, prod, monitoring) makes RBAC and resource limits clearer.  
**How:** Create namespaces before deploying services.  
**Do:**  
```bash
kubectl create namespace infra
kubectl create namespace prod
kubectl create namespace monitoring
```
**DoD:**  
- `kubectl get ns` lists `infra`, `prod`, `monitoring`.

### 70) Ingress controller
**Description (what & why):** Routes external HTTP(S) traffic into your cluster services.  
**How:** Install nginx-ingress via Helm or keep Traefik if you prefer.  
**Do:**  
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx -n infra
```
**DoD:**  
- Visiting the cluster IP shows the ingress default backend page.  
- `kubectl get pods -n infra` shows controller pods running.

### 71) cert-manager + ClusterIssuer
**Description (what & why):** Automates TLS cert provisioning using Let’s Encrypt so staging/production have HTTPS by default.  
**How:** Install cert-manager CRDs and configure HTTP-01 ClusterIssuer.  
**Do:**  
```bash
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager -n infra --set installCRDs=true
kubectl apply -f cluster-issuer.yaml
```
**DoD:**  
- Test Ingress with `cert-manager.io/cluster-issuer` annotation gets a valid certificate.  
- `kubectl describe certificate` shows status Ready=True.

### 72) DNS records
**Description (what & why):** Public hostnames are needed to issue TLS certs and access services easily.  
**How:** Create A records for `*.staging.example.com` pointing to VPS IP.  
**Do:**  
- Update DNS provider zone, wait for propagation, verify with `dig`.  
**DoD:**  
- `dig +short www.staging.example.com` resolves to VPS IP.  
- Ingress with TLS loads via HTTPS in browser.

## W3D2 — Postgres & Redis via Helm, secrets, connectivity

### 73) Helm Postgres
**Description (what & why):** Managed database lifecycle inside cluster with persistent storage.  
**How:** Deploy Bitnami Postgres chart with PVC and tuned resources.  
**Do:**  
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install pg bitnami/postgresql -n infra -f values-postgres.yaml
```
**DoD:**  
- Postgres pod Ready; secret with creds created.  
- Port-forward and run `psql` successfully.

### 74) Helm Redis
**Description (what & why):** Provides caching and a Celery broker.  
**How:** Deploy Redis chart with persistence and password.  
**Do:**  
```bash
helm install redis bitnami/redis -n infra -f values-redis.yaml
```
**DoD:**  
- `redis-cli -a $REDIS_PASSWORD ping` → `PONG`.

### 75) App secrets
**Description (what & why):** Keep DB, Stripe, email, and Django secrets out of source control and images.  
**How:** Create Kubernetes Secrets in `prod` namespace and reference them in deployments.  
**Do:**  
```bash
kubectl create secret generic app-secrets   --from-literal=DB_NAME=... --from-literal=DB_PASSWORD=...
```
**DoD:**  
- `kubectl describe secret -n prod app-secrets` shows expected keys.  
- Sensitive data not committed to Git.

### 76) Connectivity tests
**Description (what & why):** Verify network and credentials before deploying apps to reduce rollout failures.  
**How:** Port-forward Postgres/Redis to local and run test queries.  
**Do:**  
```bash
kubectl -n infra port-forward svc/pg-postgresql 5433:5432
psql -h 127.0.0.1 -p 5433 -U postgres
```
**DoD:**  
- Able to connect and run `SELECT 1`.  
- Redis `SET`/`GET` works.

## W3D3 — API manifests, media strategy, migration job

### 77) API Deployment & Service
**Description (what & why):** Runs Django API on K8s with health probes for self-healing.  
**How:** Deployment (2 replicas), Service (ClusterIP), readiness/liveness `/healthz`.  
**Do:**  
- Write `deployment.yaml`, `service.yaml` with resource requests/limits.  
- Configure envFrom Secrets/ConfigMaps.  
**DoD:**  
- `kubectl get pods -n prod` shows all API pods Ready.  
- Port-forward shows `/healthz` returns 200.

### 78) API Ingress
**Description (what & why):** Exposes API publicly with TLS on `api.staging.example.com`.  
**How:** Create Ingress with host and TLS annotation.  
**Do:**  
- Apply `ingress.yaml`.  
**DoD:**  
- `curl https://api.staging.example.com/healthz` → 200.

### 79) Static/media strategy
**Description (what & why):** Ensures static assets and uploaded media are served reliably.  
**How:** Use PVC for media, collectstatic to volume; plan migration to S3 later.  
**Do:**  
- Mount volumes; update Django settings.  
**DoD:**  
- `/static/` served; media upload/read works.

### 80) Migration Job
**Description (what & why):** Automates schema migrations and collectstatic on rollout.  
**How:** K8s Job that runs `manage.py migrate && collectstatic`.  
**Do:**  
- Write `job-migrate.yaml`.  
**DoD:**  
- Job completes with exit code 0; logs show migrations applied.

### 81) NetworkPolicy (api↔db/redis only)
**Description (what & why):** Enforces least privilege by blocking other pods from DB/Redis.  
**How:** Apply default deny policy and allow api→db/redis traffic.  
**Do:**  
- Create `networkpolicy.yaml` in prod.  
**DoD:**  
- Random pod in other ns cannot reach DB; API still works.

## W3D4 — Web manifests, env wiring, Stripe webhook

### 82) Web Deployment & Service
**Description (what & why):** Runs Next.js SSR app in cluster with probes and config.  
**How:** Deployment with readiness/liveness probes and ConfigMap for `NEXT_PUBLIC_*`.  
**Do:**  
- Apply deployment, service yaml.  
**DoD:**  
- Hitting `www.staging…` loads app and calls API successfully.

### 83) Web Ingress + TLS
**Description (what & why):** Securely serves frontend over HTTPS.  
**How:** Ingress with TLS host `www.staging.example.com`.  
**Do:**  
- Apply ingress manifest with cert annotations.  
**DoD:**  
- Browser shows padlock; no mixed content.

### 84) Stripe webhook exposure
**Description (what & why):** Required for payment event handling.  
**How:** Add path `/payments/webhook` in Ingress routing to API.  
**Do:**  
- Test with Stripe CLI forwarding.  
**DoD:**  
- CLI event returns 2xx; API logs event processed.

## W3D5 — CI/CD, HPA, rollback drill

### 85) Build & push GHCR
**Description (what & why):** Creates reproducible container images and stores them centrally.  
**How:** GitHub Actions job builds multi-stage Docker images, scans with Trivy, pushes to GHCR.  
**Do:**  
- Write `cicd.yml` build job.  
**DoD:**  
- Image visible in GHCR; scan has no critical vulns.

### 86) Deploy via CI
**Description (what & why):** Automates rollout on merge to `main` to keep staging fresh.  
**How:** `kubectl apply -k` or ArgoCD sync step in CI.  
**Do:**  
- Configure GitHub Action with KUBECONFIG secret.  
**DoD:**  
- Merge triggers rollout; status posted to PR.

### 87) HPA
**Description (what & why):** Autoscaling keeps latency low under variable load.  
**How:** HorizontalPodAutoscaler at 70% CPU for web/api.  
**Do:**  
- Apply `hpa.yaml`.  
**DoD:**  
- Load test causes scale-up events.

### 88) Rollback drill
**Description (what & why):** Practice recovering from a bad deploy to reduce downtime.  
**How:** Deploy bad image, then use `kubectl rollout undo`.  
**Do:**  
- Document steps and perform test.  
**DoD:**  
- App returns to previous version; downtime < 1 min.
