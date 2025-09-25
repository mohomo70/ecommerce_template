# Week 1 — Foundations & Catalog (Detailed Task Cards)

## W1D1 — Repos, build system, dev stack up

### 1) Initialize monorepo

**Description (what & why):** Create a single repository that houses both frontend (Next.js) and backend (Django) so you can share tooling, CI, and docs. Monorepo simplifies dependency management and atomic PRs across FE/BE.  
**How:** Root `package.json` with PNPM workspaces; `apps/` for projects.
**Do:** `git init && pnpm init -w`; add workspaces to package.json.  
**DoD:** `pnpm -r -w list` shows workspaces.

### 2) Add root tooling (Prettier & ESLint)
**Description (what & why):** Consistent code style and lint rules prevent diff noise and catch issues early.  
**How:** Install Prettier + ESLint at root, add scripts.  
**Do:** Configure `.prettierrc`, `.eslintrc.cjs`.  
**DoD:** `pnpm format` and `pnpm lint` succeed.

### 3) Commit conventions (commitlint + husky + lint-staged)
**Description (what & why):** Enforces conventional commits for clean changelogs and automated release notes.  
**How:** Install commitlint, husky, lint-staged; set pre-commit + commit-msg hooks.  
**Do:** Setup husky with `npx husky init`.  
**DoD:** Invalid commit messages are blocked.

### 4) Root CI skeleton (GitHub Actions)
**Description (what & why):** CI pipeline ensures PRs are tested and main branch is always green.  
**How:** Add `.github/workflows/ci.yml`.  
**Do:** Matrix for Node+Python, run lint/typecheck/build, pytest.  
**DoD:** Test PR shows CI passing.

### 5) Scaffold Next.js app
**Description (what & why):** Base Next 14 App Router project with TS gives SSR/ISR and typed DX.  
**How:** `pnpm create next-app apps/web --ts --eslint --app --src-dir --import-alias "@/*"`  
**Do:** Start dev server.  
**DoD:** Homepage renders, build passes.

### 6) Add Tailwind to web
**Description (what & why):** Utility-first CSS speeds up development and enforces design consistency.  
**How:** Install Tailwind, generate config, wire globals.css.  
**Do:** Add content paths, test with sample class.  
**DoD:** Tailwind class visually affects UI.

### 7) Install shadcn/ui
**Description (what & why):** Provides accessible, styled UI primitives with Tailwind tokens.  
**How:** `pnpm -F web dlx shadcn-ui@latest init`, generate components.  
**Do:** Render demo page.  
**DoD:** Components render as expected.

### 8) Data layer & forms (TanStack Query, RHF, Zod)
**Description (what & why):** Provides server state caching, form validation, type safety.  
**How:** Add providers in layout, test sample form.  
**Do:** Create schema + form.  
**DoD:** Inline validation and cached queries work.

### 9) Web foundation (layout/typography/theme/error/loading)
**Description (what & why):** Sets a consistent base layout and skeleton loading states.  
**How:** Create `layout.tsx`, typography scale, theme toggle, error boundaries.  
**Do:** Build global skeletons.  
**DoD:** Theme persists, error boundary shows fallback.

### 10) Scaffold Django project
**Description (what & why):** Backend service with admin and migrations.  
**How:** `django-admin startproject core apps/api`, add apps, migrate.  
**Do:** Create superuser.  
**DoD:** Admin accessible, migrations applied.

### 11) DRF + settings split (+/healthz)
**Description (what & why):** DRF for REST endpoints, settings split for dev/prod parity. `/healthz` for monitoring.  
**How:** Add `settings/{base,dev,prod}.py`, configure DRF + CORS.  
**Do:** Add `/healthz` view.  
**DoD:** `/api/healthz` returns 200 JSON.

### 12) Dockerfiles (web & api)
**Description (what & why):** Containerize services for consistent local/prod envs.  
**How:** Multi-stage builds with non-root user.  
**Do:** Create Dockerfile.web and Dockerfile.api.  
**DoD:** `docker build` and run succeed.

### 13) Dev docker-compose
**Description (what & why):** Single command local stack improves onboarding.  
**How:** Compose services: web, api, db, redis, mailhog, nginx.  
**Do:** Add healthchecks, volume mounts.  
**DoD:** `docker compose up --build` serves app+api locally.

## W1D2 — Auth foundation (session + CSRF), FE screens

### 14) Custom User model (email login)
**Description (what & why):** Use email as login to avoid username collisions.  
**How:** Swap AUTH_USER_MODEL.  
**Do:** Update settings, run migrations.  
**DoD:** Admin works with email.

### 15) Session auth endpoints
**Description (what & why):** Use session cookies + CSRF for secure auth.  
**How:** Add allauth/djoser routes.  
**Do:** Implement `/auth/login`, `/auth/logout`, `/auth/register`.  
**DoD:** POST login sets sessionid, /me returns user.

### 16) CORS & CSRF wiring
**Description (what & why):** Allow FE to call BE with cookies securely.  
**How:** Configure CORS_ALLOWED_ORIGINS, CORS_ALLOW_CREDENTIALS.  
**Do:** Send X-CSRFToken header.  
**DoD:** Cookies set and used successfully.

### 17) Roles & permissions
**Description (what & why):** Role-based access control gates sensitive endpoints.  
**How:** Add roles ArrayField and DRF permission_classes.  
**Do:** Create IsAdminRole class.  
**DoD:** Unauthorized user gets 403 on admin endpoint.

### 18) FE Login page
**Description (what & why):** Entry point for session auth.  
**How:** RHF+Zod form, credentials: 'include'.  
**Do:** Implement /login route.  
**DoD:** Successful login redirects, invalid shows error.

### 19) FE Signup page
**Description (what & why):** Allows account creation.  
**How:** RHF form, call /auth/register.  
**Do:** Implement /signup route.  
**DoD:** Can create account and log in.

### 20) Forgot/reset password flow
**Description (what & why):** Lets users recover access.  
**How:** Token email link, reset form.  
**Do:** Build forgot/reset pages.  
**DoD:** Flow completes and session invalidated.

### 21) Protected routing
**Description (what & why):** Redirect unauth users from private pages.  
**How:** Wrapper calls /me, redirects unauth.  
**Do:** Wrap /account.  
**DoD:** Visiting /account unauth redirects to login.

### 22) Role badge in header
**Description (what & why):** Displays user roles, helpful for dev/test.  
**How:** Fetch /me and render chip.  
**Do:** Add RoleChip component.  
**DoD:** Chip shows correct role.

## W1D3 — Catalog models, admin, seed, read APIs

### 23) Category model
**Description (what & why):** Hierarchical category tree powers PLP filters.  
**How:** Self-FK parent field, slug unique.  
**Do:** Add migration.  
**DoD:** Nested categories create successfully.

### 24) Product & Variant models
**Description (what & why):** Represents products and SKUs with stock & price.  
**How:** Product has attributes JSON, variant holds SKU, stock.  
**Do:** Implement models.  
**DoD:** Admin can create product with variants.

### 25) Media model & admin preview
**Description (what & why):** Images are critical to e-commerce.  
**How:** Media model FK to product, admin inline preview.  
**Do:** Add model + admin.  
**DoD:** Thumbnails visible in admin.

### 26) Search indexes
**Description (what & why):** Improves query performance for PLP/search.  
**How:** Add tsvector and btree indexes.  
**Do:** Create migration.  
**DoD:** EXPLAIN shows index usage.

### 27) Seed products
**Description (what & why):** Enables realistic dev data and perf testing.  
**How:** Mgmt command generate 100 products.  
**Do:** `python manage.py seed_products`.  
**DoD:** 100+ products visible in admin/API.

### 28) Products list API
**Description (what & why):** Serves PLP data.  
**How:** DRF ListAPIView with filters and pagination.  
**Do:** Implement /products endpoint.  
**DoD:** Filters/sorting work, pagination correct.

### 29) Product detail API
**Description (what & why):** Serves PDP data.  
**How:** RetrieveAPIView by slug.  
**Do:** Implement /products/{slug}.  
**DoD:** Returns full product info.

### 30) Performance logging
**Description (what & why):** Measure DB time to catch regressions.  
**How:** Middleware logs query time.  
**Do:** Implement and attach X-DB-Time header.  
**DoD:** PLP shows <= 50ms DB time.

### 31) Basic API tests
**Description (what & why):** Lock behavior, prevent regressions.  
**How:** Pytest list/detail tests.  
**Do:** Write tests.  
**DoD:** pytest green.

## W1D4 — PLP/PDP (SSR/ISR), SEO basics

### 32) PLP with URL-driven filters
**Description (what & why):** Shareable state improves UX/SEO.  
**How:** Sync filters to searchParams.  
**Do:** Build filter UI and sync state.  
**DoD:** Reload reproduces filters.

### 33) PLP skeletons & empty state
**Description (what & why):** Better perceived performance and guidance.  
**How:** Skeleton components and empty state message.  
**Do:** Implement skeletons.  
**DoD:** Skeletons visible on slow network.

### 34) PDP SSR/ISR
**Description (what & why):** SEO-friendly server render and cache.  
**How:** generateStaticParams or SSR.  
**Do:** Implement PDP page with ISR.  
**DoD:** View source shows HTML.

### 35) PDP image gallery
**Description (what & why):** Product imagery critical for conversions.  
**How:** next/image with responsive sizes.  
**Do:** Implement gallery.  
**DoD:** No CLS, responsive images load.

### 36) Read-only reviews block
**Description (what & why):** Adds social proof.  
**How:** Render reviews summary from API.  
**Do:** Implement block.  
**DoD:** Shows rating count/avg.

### 37) SEO metadata & JSON-LD
**Description (what & why):** Improves SERP and rich results.  
**How:** generateMetadata and inject JSON-LD.  
**Do:** Add canonical, breadcrumbs.  
**DoD:** Rich Results test passes.

### 38) Sitemap/robots
**Description (what & why):** Helps search engine discovery.  
**How:** next-sitemap config.  
**Do:** Generate sitemap.xml.  
**DoD:** /sitemap.xml reachable.

### 39) Lighthouse SEO >= 90
**Description (what & why):** Objective quality bar.  
**How:** Run Lighthouse mobile.  
**Do:** Fix issues until score >= 90.  
**DoD:** Save report screenshot.

## W1D5 — Cart API + FE cart with optimistic sync

### 40) Cart model & endpoints
**Description (what & why):** Server-authoritative cart for stock validation.  
**How:** Session/user scoped, idempotent upsert.  
**Do:** Implement CRUD endpoints.  
**DoD:** Full CRUD works.

### 41) Server validation (qty/stock)
**Description (what & why):** Prevent oversell and invalid qty.  
**How:** Validate qty <= stock, atomic ops.  
**Do:** Add validation in serializer.  
**DoD:** Exceed stock returns 400.

### 42) Canonical totals
**Description (what & why):** Backend is source of truth for pricing/tax.  
**How:** Return totals object.  
**Do:** Implement calculation.  
**DoD:** Totals match displayed values.

### 43) FE cart drawer & page
**Description (what & why):** Gives quick access + detailed view.  
**How:** Build drawer + /cart page.  
**Do:** Implement UI components.  
**DoD:** Drawer/page synced.

### 44) Optimistic updates + rollback
**Description (what & why):** Improves perceived speed, rollback on error.  
**How:** TanStack Query mutation with onError rollback.  
**Do:** Implement optimistic updates.  
**DoD:** Failure reverts instantly.

### 45) Cart tests
**Description (what & why):** Prevent regressions in purchase flow.  
**How:** Unit + API tests.  
**Do:** Write tests.  
**DoD:** CI passes with coverage.
