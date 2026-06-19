const SENSITIVE_QUERY_PARTS = [
  "token",
  "auth",
  "code",
  "email",
  "session",
  "key",
  "signature",
  "password",
];

function readSentryConfig() {
  const element = document.getElementById("bwd-sentry-config");
  if (!element) return {};

  try {
    return JSON.parse(element.textContent || "{}");
  } catch (error) {
    void error;
    return {};
  }
}

function sampleRate(value, fallback) {
  const rate = Number(value);
  if (!Number.isFinite(rate)) return fallback;
  return Math.min(1, Math.max(0, rate));
}

function compact(value) {
  return value || undefined;
}

function redactUrl(value) {
  if (!value) return value;

  try {
    const url = new URL(value, window.location.origin);
    Array.from(url.searchParams.keys()).forEach((key) => {
      const normalizedKey = key.toLowerCase();
      if (SENSITIVE_QUERY_PARTS.some((part) => normalizedKey.indexOf(part) !== -1)) {
        url.searchParams.set(key, "[REDACTED]");
      }
    });
    return url.toString();
  } catch (error) {
    void error;
    return "[REDACTED_URL]";
  }
}

function scrubBreadcrumb(breadcrumb) {
  if (breadcrumb && breadcrumb.data && breadcrumb.data.url) {
    breadcrumb.data.url = redactUrl(breadcrumb.data.url);
  }
  return breadcrumb;
}

function scrubEvent(event) {
  if (event && event.request && event.request.url) {
    event.request.url = redactUrl(event.request.url);
  }

  if (event && Array.isArray(event.breadcrumbs)) {
    event.breadcrumbs = event.breadcrumbs.map(scrubBreadcrumb);
  }

  return event;
}

async function initializeSentry() {
  const config = readSentryConfig();

  if (!config.enabled || !config.dsn) return;

  const Sentry = await import(/* webpackChunkName: "sentry" */ "@sentry/browser");
  const tracePropagationTargets =
    Array.isArray(config.tracePropagationTargets) && config.tracePropagationTargets.length
      ? config.tracePropagationTargets
      : [window.location.origin];

  Sentry.init({
    dsn: config.dsn,
    environment: compact(config.environment),
    release: compact(config.release),
    dist: compact(config.dist),
    sendDefaultPii: Boolean(config.sendDefaultPii),
    enableLogs: Boolean(config.enableLogs),
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        maskAllInputs: true,
        blockAllMedia: true,
      }),
    ],
    tracesSampleRate: sampleRate(config.tracesSampleRate, 0.2),
    tracePropagationTargets,
    replaysSessionSampleRate: sampleRate(config.replaysSessionSampleRate, 0.1),
    replaysOnErrorSampleRate: sampleRate(config.replaysOnErrorSampleRate, 1.0),
    beforeBreadcrumb: scrubBreadcrumb,
    beforeSend: scrubEvent,
  });

  Sentry.setTag("app", "builtwithdjango");

  if (config.user) {
    Sentry.setUser(config.user);
  }
}

initializeSentry().catch((error) => {
  void error;
});
