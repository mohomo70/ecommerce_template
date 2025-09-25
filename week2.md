# Week 2 — Checkout, Payments, Email (Detailed Task Cards)

## W2D1 — Checkout wizard + order draft

### 46) Checkout stepper
**Description (what & why):** A guided multi-step flow helps reduce user confusion and ensures required data is collected in order.  
**How:** Implement stepper routes (Address → Shipping → Review) with state persisted on server.  
**Do:** Build stepper UI, route guards, navigation buttons.  
**DoD:** Navigating steps preserves state, deep links work when prerequisites are met.

### 47) Address form + validation
**Description (what & why):** Properly validated address data ensures correct shipping and tax calculation.  
**How:** Build a React Hook Form with Zod schema; per-field validation and inline error display.  
**Do:** Create form with fields (name, street, city, zip, country, phone).  
**DoD:** Invalid input shows errors; valid saves to draft and updates totals.

### 48) Order draft API
**Description (what & why):** Centralized server-side calculation of totals avoids client drift.  
**How:** Implement POST `/orders/draft` and PATCH `/orders/draft/{id}` that return draft id, totals, shipping options.  
**Do:** Create DRF views/serializers for draft, implement recalculation logic.  
**DoD:** Returns consistent `{draft_id, totals, shipping_options}` payloads.

### 49) Review step
**Description (what & why):** A final confirmation step prevents accidental purchases and shows out-of-stock items before payment.  
**How:** Display canonical totals and lines from server, re-check stock before confirm.  
**Do:** Render review UI with edit buttons for previous steps.  
**DoD:** OOS items block checkout with a clear message.

### 50) Autosave/resume
**Description (what & why):** Lets customers recover progress if they refresh or close the page.  
**How:** Persist draft server-side, reload it on checkout mount.  
**Do:** Implement autosave on step change, load existing draft if present.  
**DoD:** Refresh mid-checkout resumes on the same step with data intact.

## W2D2 — Stripe Payment Intents + webhook + state machine

### 51) Create payment intent
**Description (what & why):** Prepares a secure payment session and returns Stripe client secret.  
**How:** Implement POST `/payments/intent` tied to the draft order.  
**Do:** Call Stripe API server-side, return client secret to FE.  
**DoD:** Stripe dashboard shows intent; FE receives usable secret.

### 52) Client confirmation
**Description (what & why):** Securely collects card info and confirms payment.  
**How:** Use Stripe Elements and `confirmCardPayment` with client secret.  
**Do:** Build payment page, handle success/failure flows.  
**DoD:** Successful payment redirects to receipt; failures show retry UI.

### 53) Persist idempotency
**Description (what & why):** Avoids duplicate orders/charges if client retries.  
**How:** Generate idempotency key per draft and persist.  
**Do:** Store in DB and send as Stripe header.  
**DoD:** Multiple submits result in a single finalized order.

### 54) Webhook handler
**Description (what & why):** Stripe events are source of truth; required for async confirmations.  
**How:** Create `/payments/webhook`, validate signature, finalize order in a DB transaction.  
**Do:** Implement idempotent handler that ignores duplicates.  
**DoD:** Stripe replays don’t double-finalize orders.

### 55) Order state machine
**Description (what & why):** Enforces valid order lifecycle transitions and simplifies reporting.  
**How:** Use finite state machine: draft → awaiting_payment → paid → fulfilled → cancelled.  
**Do:** Implement status fields and guard transitions.  
**DoD:** Invalid transitions blocked with 400; valid transitions update consistently.

## W2D3 — Transactional email via Celery

### 56) Celery worker setup
**Description (what & why):** Offloads slow email sending to background tasks.  
**How:** Add Celery worker + beat using Redis broker, add health task.  
**Do:** Configure celery.py, add process to docker-compose.  
**DoD:** `celery inspect ping` responds OK.

### 57) Email backend & templates
**Description (what & why):** Send order confirmations to customers.  
**How:** Use Resend/SendGrid in prod, Mailhog in dev. Create HTML+text templates.  
**Do:** Implement templates and email service.  
**DoD:** Paid order triggers email; Mailhog shows email in dev.

### 58) Signal to task
**Description (what & why):** Decouples order creation from email delivery with retries.  
**How:** Django signal on order.paid enqueues Celery task with backoff.  
**Do:** Implement signal, configure retry policy.  
**DoD:** Killing worker mid-send results in a single email after retry.

## W2D4 — i18n, currency, personalization

### 59) Locale routing
**Description (what & why):** Localized UI improves trust and conversion.  
**How:** Add `next-intl`, define locales, add switcher and middleware.  
**Do:** Create `en.json`, `de.json`, add locale switch.  
**DoD:** Switching locale persists and affects all pages.

### 60) Currency formatting
**Description (what & why):** Shows correct currency format per locale.  
**How:** Use `Intl.NumberFormat` with locale + currency.  
**Do:** Wrap all price displays in formatter.  
**DoD:** Prices switch format correctly between locales.

### 61) Recently viewed
**Description (what & why):** Boosts engagement by letting users revisit products.  
**How:** Track product views in local storage or server.  
**Do:** Build widget for PDP/PLP.  
**DoD:** Viewed products list persists across refresh.

### 62) Recommendations slot
**Description (what & why):** Improves upsell and cross-sell.  
**How:** Call `/recommendations` and render products.  
**Do:** Build `Recommended` component with graceful empty state.  
**DoD:** Recommendations render when API responds, hide otherwise.

### 63) Theme toggle
**Description (what & why):** Supports dark/light mode preferences.  
**How:** Add toggle in header, persist to storage.  
**Do:** Implement theme context and toggle.  
**DoD:** Theme persists after refresh.

## W2D5 — A11y sweep & UX polish

### 64) Landmarks & navigation
**Description (what & why):** Improves accessibility for keyboard and screen reader users.  
**How:** Add semantic landmarks and skip link.  
**Do:** Update layouts with `<header>`, `<main>`, `<footer>`.  
**DoD:** Keyboard navigation follows logical order.

### 65) Focus & ARIA
**Description (what & why):** Makes controls accessible to screen readers.  
**How:** Add visible focus rings, ARIA attributes.  
**Do:** Audit controls and fix missing labels.  
**DoD:** axe shows 0 critical issues.

### 66) Error handling & boundaries
**Description (what & why):** Graceful error messages improve trust.  
**How:** Add global error boundary and network error toasts.  
**Do:** Wrap app in error boundary, create fallback UI.  
**DoD:** Simulated API error shows user-friendly message.

### 67) Loading skeleton library
**Description (what & why):** Keeps UI stable while loading data.  
**How:** Use consistent skeleton components.  
**Do:** Replace spinners with skeletons on PLP/PDP.  
**DoD:** Skeletons show under slow network without layout shift.
