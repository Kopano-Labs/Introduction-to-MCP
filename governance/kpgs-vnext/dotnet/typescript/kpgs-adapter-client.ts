export type KpgsAdapterVersion = {
  adapterId: string;
  adapterVersion: string;
  protocolVersion: string;
  compatible: boolean;
};

export type KpgsTaskSnapshot = {
  taskId: string;
  status: string;
  version: number;
  nextActions: string[];
  userSafeExplanation: string;
  correlationId: string;
};

export type KpgsTaskRequest = {
  taskId: string;
  correlationId: string;
  governingSpecRef: string;
  input: unknown;
  idempotencyKey: string;
};

export class KpgsAdapterClient {
  constructor(
    private readonly baseUrl: string,
    private readonly fetcher: typeof fetch = fetch,
  ) {}

  async version(protocol = '1.0'): Promise<KpgsAdapterVersion> {
    return this.json(`/kpgs/version?protocol=${encodeURIComponent(protocol)}`);
  }

  async getSession(taskId: string, correlationId: string): Promise<KpgsTaskSnapshot | null> {
    return this.json(`/kpgs/session/${encodeURIComponent(taskId)}`, {
      headers: { 'X-Correlation-ID': correlationId },
    });
  }

  async createTask(request: KpgsTaskRequest): Promise<KpgsTaskSnapshot> {
    return this.json('/kpgs/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-KPGS-Task': request.taskId,
        'X-Correlation-ID': request.correlationId,
      },
      body: JSON.stringify(request),
    });
  }

  async command(
    taskId: string,
    correlationId: string,
    command: { commandId: string; name: string; payload?: unknown; idempotencyKey: string },
  ): Promise<KpgsTaskSnapshot> {
    return this.json(`/kpgs/tasks/${encodeURIComponent(taskId)}/commands`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-KPGS-Task': taskId,
        'X-Correlation-ID': correlationId,
      },
      body: JSON.stringify({ ...command, correlationId }),
    });
  }

  private async json<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await this.fetcher(new URL(path, this.baseUrl), init);
    const body = await response.json();
    if (!response.ok) {
      const message = body && typeof body === 'object' && 'error' in body ? String(body.error) : `KPGS adapter HTTP ${response.status}`;
      throw new Error(message);
    }
    return body as T;
  }
}
