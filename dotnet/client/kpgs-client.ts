export type KpgsIdentityHeaders = {
  subject: string;
  tenant: string;
  domain: string;
  session: string;
  correlationId?: string;
};

export type KpgsTaskCreate = {
  governingSpecRef: string;
  input: unknown;
  idempotencyKey: string;
  updateId: string;
  boundaryMarker?: "#NB";
  crudIntent?: "CREATE";
};

export type KpgsTaskCommand = {
  command: string;
  input: unknown;
  idempotencyKey: string;
  updateId: string;
  boundaryMarker?: "#NB";
};

/**
 * Tiny binding for existing PWAs. It adds KPGS as a service boundary; it does
 * not require React/Next/Vite/MERN applications to move to .NET.
 */
export class KpgsClient {
  constructor(
    private readonly baseUrl: string,
    private readonly identity: () => KpgsIdentityHeaders,
    private readonly fetcher: typeof fetch = fetch,
  ) {}

  health() {
    return this.request("/kpgs/health");
  }

  version() {
    return this.request("/kpgs/version");
  }

  session(id: string) {
    return this.request(`/kpgs/session/${encodeURIComponent(id)}`, { governed: true });
  }

  createTask(input: KpgsTaskCreate) {
    return this.request("/kpgs/tasks", {
      method: "POST",
      body: JSON.stringify({ boundaryMarker: "#NB", crudIntent: "CREATE", ...input }),
      governed: true,
    });
  }

  command(taskId: string, input: KpgsTaskCommand) {
    return this.request(`/kpgs/tasks/${encodeURIComponent(taskId)}/commands`, {
      method: "POST",
      body: JSON.stringify({ boundaryMarker: "#NB", ...input }),
      governed: true,
    });
  }

  evidence(taskId: string) {
    return this.request(`/kpgs/tasks/${encodeURIComponent(taskId)}/evidence`, { governed: true });
  }

  private async request(
    path: string,
    options: { method?: string; body?: string; governed?: boolean } = {},
  ) {
    const headers = new Headers({ "Content-Type": "application/json" });
    if (options.governed) {
      const identity = this.identity();
      headers.set("X-KPGS-Subject", identity.subject);
      headers.set("X-KPGS-Tenant", identity.tenant);
      headers.set("X-KPGS-Domain", identity.domain);
      headers.set("X-KPGS-Session", identity.session);
      if (identity.correlationId) headers.set("X-Correlation-Id", identity.correlationId);
    }

    const response = await this.fetcher(`${this.baseUrl}${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body,
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(`KPGS adapter ${response.status}: ${payload?.detail ?? "request failed"}`);
    }
    return payload;
  }
}
