import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  debug: false,
  tracePropagationTargets: [
    'localhost',
    /^https:\/\/api\.staging\.example\.com/,
    /^https:\/\/api\.example\.com/,
  ],
  integrations: [
    Sentry.browserTracingIntegration(),
  ],
  beforeSend(event) {
    // Filter out development errors
    if (process.env.NODE_ENV === 'development') {
      return null;
    }
    return event;
  },
});
