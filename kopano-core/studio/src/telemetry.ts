import { ApplicationInsights } from '@microsoft/applicationinsights-web';

let appInsights: ApplicationInsights | null = null;

const connectionString = import.meta.env.VITE_APPLICATIONINSIGHTS_CONNECTION_STRING;

export const clientTelemetryConfigured = Boolean(connectionString);

export const initClientTelemetry = () => {
  if (!clientTelemetryConfigured || appInsights) {
    return appInsights;
  }

  appInsights = new ApplicationInsights({
    config: {
      connectionString,
      enableAutoRouteTracking: true,
      disableFetchTracking: false,
      disableAjaxTracking: false,
    },
  });

  appInsights.loadAppInsights();
  appInsights.trackPageView();
  return appInsights;
};

export const trackClientEvent = (name: string, properties: Record<string, string | number | boolean> = {}) => {
  if (!appInsights) {
    return;
  }

  appInsights.trackEvent({ name }, properties);
};
