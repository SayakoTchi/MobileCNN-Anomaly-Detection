const DEFAULT_TIMEOUT_MS = 8000;

export function createTimeoutErrorMessage(timeoutMs) {
  return `V50 node request timed out after ${timeoutMs}ms`;
}

function normalizeBaseUrl(baseUrl) {
  const trimmed = String(baseUrl || '').trim();
  if (!trimmed) {
    throw new Error('V50 base URL is required');
  }
  return trimmed.replace(/\/+$/, '');
}

function joinUrl(baseUrl, path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}

async function parseResponse(response, expectedType) {
  if (!response.ok) {
    const body = await response.text().catch(() => '');
    const suffix = body ? ` - ${body}` : '';
    throw new Error(`V50 node returned ${response.status} ${response.statusText}${suffix}`);
  }

  if (expectedType === 'text') {
    return response.text();
  }

  return response.json();
}

export class V50ApiClient {
  constructor({ baseUrl, fetchImpl = globalThis.fetch, timeoutMs = DEFAULT_TIMEOUT_MS } = {}) {
    if (typeof fetchImpl !== 'function') {
      throw new Error('fetch implementation is required');
    }

    this.baseUrl = normalizeBaseUrl(baseUrl);
    this.fetchImpl = fetchImpl;
    this.timeoutMs = timeoutMs;
  }

  setBaseUrl(baseUrl) {
    this.baseUrl = normalizeBaseUrl(baseUrl);
  }

  resolveClipUrl(clipUrl) {
    if (!clipUrl) {
      return '';
    }
    if (/^https?:\/\//i.test(clipUrl)) {
      return clipUrl;
    }
    return joinUrl(this.baseUrl, clipUrl);
  }

  async request(path, { method = 'GET', body, headers, expectedType = 'json' } = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await this.fetchImpl(joinUrl(this.baseUrl, path), {
        method,
        body,
        headers,
        signal: controller.signal,
      });

      return await parseResponse(response, expectedType);
    } catch (error) {
      if (error?.name === 'AbortError') {
        throw new Error(createTimeoutErrorMessage(this.timeoutMs));
      }
      throw new Error(`V50 node request failed: ${error.message}`);
    } finally {
      clearTimeout(timeoutId);
    }
  }

  ping() {
    return this.request('/ping', { expectedType: 'text' });
  }

  updateConfig(threshold) {
    return this.request('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ threshold }),
    });
  }

  detect(imageBlob) {
    if (!(imageBlob instanceof Blob)) {
      throw new Error('detect requires a Blob or File image payload');
    }

    return this.request('/api/detect', {
      method: 'POST',
      body: imageBlob,
    });
  }

  getTimeline() {
    return this.request('/api/timeline');
  }

  swapModel() {
    return this.request('/api/model/swap', {
      method: 'POST',
      expectedType: 'text',
    });
  }
}
