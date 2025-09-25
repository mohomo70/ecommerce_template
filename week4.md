# Week 4 — Observability, Security, Extras (Detailed Task Cards)

## W4D1 — Sentry, Loki/Grafana, dashboards/alerts

### 89) Sentry FE integration
**Description (what & why):** Captures client-side errors for monitoring.  
**How:** Add Sentry SDK, wrap app with ErrorBoundary and tracing.  
**Do:** Configure DSN in env, test error capture.  
**DoD:** Manual JS error appears in Sentry dashboard.

### 90) Sentry BE integration
**Description (what & why):** Captures unhandled exceptions and traces in Django.  
**How:** Install `sentry-sdk[django]`, init in settings.  
**Do:** Raise test exception.  
**DoD:** Event visible in Sentry.

### 91) Loki/Promtail log shipping
**Description (what & why):** Centralizes logs for debugging.  
**How:** Deploy Loki + Promtail via Helm, configure to scrape pods.  
**Do:** Apply manifests.  
**DoD:** Logs visible in Grafana explore.

### 92) Grafana dashboards
**Description (what & why):** Visualizes API latency, error rates, resource usage.  
**How:** Import dashboards, connect to Loki + k8s metrics.  
**Do:** Create p95 latency panel.  
**DoD:** Dashboards show live data.

### 93) Alerts
**Description (what & why):** Proactive notifications for outages.  
**How:** Create Grafana alert rules (p95 > 300ms, 5xx > 1%).  
**Do:** Configure notification channel (Slack/email).  
**DoD:** Forced outage triggers alert.

## W4D2 — Backups + restore; media to S3

### 94) Postgres backup CronJob
**Description (what & why):** Nightly pg_dump protects against data loss.  
**How:** Create CronJob with pg_dump to S3.  
**Do:** Apply cronjob.yaml.  
**DoD:** S3 bucket has dated backup file.

### 95) Restore drill
**Description (what & why):** Ensure backups are restorable.  
**How:** Create new ephemeral DB, restore latest dump, run smoke tests.  
**Do:** Document steps.  
**DoD:** Restore completes <10min, data correct.

### 96) Media to S3
**Description (what & why):** Persist user uploads outside cluster and allow CDN distribution.  
**How:** Configure DEFAULT_FILE_STORAGE to S3, migrate existing media.  
**Do:** Update settings, sync files.  
**DoD:** Images load from S3 URL.

## W4D3 — Security hardening

### 97) Security headers
**Description (what & why):** Adds XSS/CSRF/mime protections.  
**How:** Add CSP, HSTS, Referrer-Policy in Django or Ingress.  
**Do:** Test with curl -I.  
**DoD:** Headers present.

### 98) Ingress rate limiting
**Description (what & why):** Mitigates brute force attacks.  
**How:** Nginx ingress annotations for /auth endpoints.  
**Do:** Apply config.  
**DoD:** Excessive requests return 429.

### 99) Pod securityContext & PDB
**Description (what & why):** Enforces non-root containers and safe disruptions.  
**How:** Add runAsNonRoot, readOnlyRootFilesystem, PodDisruptionBudget.  
**Do:** Patch deployments.  
**DoD:** `kubectl describe pod` shows securityContext active.

### 100) NetworkPolicies
**Description (what & why):** Restrict pod-to-pod traffic to only required services.  
**How:** Apply default deny + allow specific flows.  
**Do:** Apply policies.  
**DoD:** Unrelated pod cannot access DB.

### 101) Ratelimit/captcha on auth
**Description (what & why):** Prevent abuse of login endpoints.  
**How:** django-ratelimit + captcha after threshold.  
**Do:** Configure middleware.  
**DoD:** Excessive login attempts blocked.

## W4D4 — PWA + realtime + points skeleton

### 102) PWA setup
**Description (what & why):** Enables offline browsing and installability.  
**How:** next-pwa plugin, manifest.json, service worker.  
**Do:** Add icons, offline cache PLP/PDP.  
**DoD:** Chrome shows install prompt, offline PDP works.

### 103) SSE/Channels for inventory
**Description (what & why):** Updates PLP/PDP when stock changes.  
**How:** Django Channels or SSE endpoint streaming inventory updates.  
**Do:** Build FE hook useInventoryStream.  
**DoD:** Stock change shows banner within 5s.

### 104) Points system
**Description (what & why):** Gamifies shopping and encourages repeat purchases.  
**How:** Add points field, increment on order paid.  
**Do:** Seed badge thresholds.  
**DoD:** Profile shows updated points.

### 105) Feature flags
**Description (what & why):** Allows safe rollout of new features.  
**How:** ConfigMap NEXT_PUBLIC_FLAGS, read in FE.  
**Do:** Wrap features with flag checks.  
**DoD:** Toggling flag hides/shows feature.

## W4D5 — Docs, performance, e2e

### 106) OpenAPI schema & docs
**Description (what & why):** Documents API for FE/devs.  
**How:** drf-spectacular, ReDoc page.  
**Do:** Expose /schema, add link.  
**DoD:** /schema reachable.

### 107) Architecture diagram & ADRs
**Description (what & why):** Helps onboarding and design decisions.  
**How:** Draw.io diagram, ADR markdowns.  
**Do:** Commit to docs folder.  
**DoD:** Onboarding <30min.

### 108) Performance tuning
**Description (what & why):** Meets p95 latency targets.  
**How:** Add indexes, cache hot queries, tune gunicorn.  
**Do:** Run k6 load test.  
**DoD:** p95 <300ms.

### 109) Cache hit rate
**Description (what & why):** Ensure Redis cache effective.  
**How:** Instrument cache metrics.  
**Do:** Tune TTL, keys.  
**DoD:** >60% cache hit rate.

### 110) Playwright e2e suite
**Description (what & why):** Full regression coverage of purchase flow.  
**How:** Write tests signup→checkout→webhook.  
**Do:** Add CI step.  
**DoD:** CI green, videos saved.

### 111) Final QA signoff
**Description (what & why):** Confirms shippable state before production.  
**How:** Manual test plan execution.  
**Do:** Complete checklist.  
**DoD:** All critical bugs resolved.
