import assert from 'node:assert/strict';
import { V50ApiClient, createTimeoutErrorMessage } from './v50Api.mjs';

function createJsonResponse(body, ok = true, status = 200) {
  return {
    ok,
    status,
    statusText: ok ? 'OK' : 'Server Error',
    headers: new Headers({ 'content-type': 'application/json' }),
    async json() {
      return body;
    },
    async text() {
      return JSON.stringify(body);
    },
  };
}

function createTextResponse(body, ok = true, status = 200) {
  return {
    ok,
    status,
    statusText: ok ? 'OK' : 'Server Error',
    headers: new Headers({ 'content-type': 'text/plain' }),
    async json() {
      throw new Error('not json');
    },
    async text() {
      return body;
    },
  };
}

async function test(name, fn) {
  try {
    await fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    console.error(error);
    process.exitCode = 1;
  }
}

await test('normalizes base URLs and pings text endpoint', async () => {
  const calls = [];
  const client = new V50ApiClient({
    baseUrl: 'http://192.168.0.50:8080/',
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      return createTextResponse('V50 연산 노드 살아있음 ㅇㅇ');
    },
  });

  const result = await client.ping();

  assert.equal(result, 'V50 연산 노드 살아있음 ㅇㅇ');
  assert.equal(calls[0].url, 'http://192.168.0.50:8080/ping');
  assert.equal(calls[0].options.method, 'GET');
});

await test('posts threshold config as JSON', async () => {
  const calls = [];
  const client = new V50ApiClient({
    baseUrl: 'http://v50.local:8080',
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      return createJsonResponse({ status: 'success', msg: '설정 변경 완료' });
    },
  });

  const result = await client.updateConfig(0.7);

  assert.deepEqual(result, { status: 'success', msg: '설정 변경 완료' });
  assert.equal(calls[0].url, 'http://v50.local:8080/api/config');
  assert.equal(calls[0].options.method, 'POST');
  assert.equal(calls[0].options.headers['Content-Type'], 'application/json');
  assert.equal(calls[0].options.body, JSON.stringify({ threshold: 0.7 }));
});

await test('sends detect payload as raw binary without JSON content type', async () => {
  const binary = new Blob(['fake-image'], { type: 'image/jpeg' });
  const calls = [];
  const client = new V50ApiClient({
    baseUrl: 'http://10.0.0.7:8080',
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      return createJsonResponse({
        anomaly: true,
        class: 'person',
        clip: 'anomaly_clip_20260519_143000.jpg',
      });
    },
  });

  const result = await client.detect(binary);

  assert.equal(result.anomaly, true);
  assert.equal(result.class, 'person');
  assert.equal(calls[0].url, 'http://10.0.0.7:8080/api/detect');
  assert.equal(calls[0].options.method, 'POST');
  assert.equal(calls[0].options.body, binary);
  assert.equal(calls[0].options.headers, undefined);
});

await test('loads timeline and resolves clip URLs', async () => {
  const timeline = [
    {
      time: '2026-05-19 14:30:00',
      object: 'person',
      confidence: 0.85,
      clip_url: '/api/clip/anomaly_clip_20260519_143000.jpg',
    },
  ];
  const client = new V50ApiClient({
    baseUrl: 'http://phone:8080',
    fetchImpl: async () => createJsonResponse(timeline),
  });

  const result = await client.getTimeline();
  const clipUrl = client.resolveClipUrl(result[0].clip_url);

  assert.equal(result.length, 1);
  assert.equal(clipUrl, 'http://phone:8080/api/clip/anomaly_clip_20260519_143000.jpg');
});

await test('posts model swap and returns text', async () => {
  const calls = [];
  const client = new V50ApiClient({
    baseUrl: 'http://phone:8080',
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      return createTextResponse('모델 교체 완료');
    },
  });

  const result = await client.swapModel();

  assert.equal(result, '모델 교체 완료');
  assert.equal(calls[0].url, 'http://phone:8080/api/model/swap');
  assert.equal(calls[0].options.method, 'POST');
});

await test('normalizes fetch failures into readable errors', async () => {
  const client = new V50ApiClient({
    baseUrl: 'http://phone:8080',
    fetchImpl: async () => {
      throw new TypeError('Failed to fetch');
    },
  });

  await assert.rejects(
    () => client.ping(),
    /V50 node request failed: Failed to fetch/,
  );
});

await test('formats timeout error message', () => {
  assert.equal(
    createTimeoutErrorMessage(3000),
    'V50 node request timed out after 3000ms',
  );
});
