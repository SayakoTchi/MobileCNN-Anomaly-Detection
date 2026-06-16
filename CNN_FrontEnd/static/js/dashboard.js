import { V50ApiClient } from './v50Api.js';

const BASE_URL_STORAGE_KEY = 'edgeVision.v50BaseUrl';
// 백엔드 서버 주소
const DEFAULT_BASE_URL = 'http://192.168.216.204:8080';

const state = {
  timeline: [],
  client: new V50ApiClient({
    baseUrl: localStorage.getItem(BASE_URL_STORAGE_KEY) || DEFAULT_BASE_URL,
  }),
};

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatConfidence(confidence) {
  if (typeof confidence !== 'number') {
    return '-';
  }
  return `${Math.round(confidence * 100)}%`;
}

function setText(id, text) {
  const element = $(id);
  if (element) {
    element.textContent = text;
  }
}

function setNotice(message, type = 'info') {
  const notice = $('notice');
  notice.className = `alert alert-${type} py-2 px-3 mb-3`;
  notice.textContent = message;
  notice.hidden = false;
}

function clearNotice() {
  const notice = $('notice');
  notice.hidden = true;
  notice.textContent = '';
}

function setNodeStatus(label, tone) {
  const badge = $('node-status-badge');
  badge.className = `badge rounded-pill text-bg-${tone}`;
  badge.textContent = label;
}

async function withButtonLoading(button, label, task) {
  const original = button.innerHTML;
  button.disabled = true;
  button.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>${label}`;
  try {
    return await task();
  } finally {
    button.disabled = false;
    button.innerHTML = original;
  }
}

function getClipUrl(event) {
  if (event.clip_url) {
    return state.client.resolveClipUrl(event.clip_url);
  }
  if (event.clip) {
    return state.client.resolveClipUrl(`/api/clip/${event.clip}`);
  }
  return '';
}

function eventTemplate(event, { compact = false } = {}) {
  const clipUrl = getClipUrl(event);
  const objectName = event.object || event.class || 'unknown';
  const time = event.time || 'time unavailable';
  const confidence = formatConfidence(event.confidence);
  const borderClass = event.anomaly ? 'border-danger' : 'border-success';
  const badgeClass = event.anomaly ? 'text-bg-danger' : 'text-bg-success';

  return `
    <article class="event-item ${compact ? 'event-compact' : ''} ${borderClass}">
      ${clipUrl && !compact ? `<img src="${escapeHtml(clipUrl)}" alt="${escapeHtml(objectName)} evidence clip" class="event-thumb">` : ''}
      <div class="event-body">
        <div class="d-flex justify-content-between gap-2 align-items-start">
          <div>
            <h6 class="mb-1 text-light">${escapeHtml(objectName)}</h6>
            <p class="mb-0 text-secondary small">${escapeHtml(time)}</p>
          </div>
          <span class="badge ${badgeClass}">${event.anomaly ? 'ANOMALY' : 'EVENT'}</span>
        </div>
        <div class="d-flex justify-content-between align-items-center mt-2">
          <span class="text-secondary small">confidence</span>
          <strong class="text-mint">${confidence}</strong>
        </div>
      </div>
    </article>
  `;
}

function renderTimeline(events) {
  const safeEvents = Array.isArray(events) ? events : [];
  state.timeline = safeEvents;

  const recentEvents = safeEvents.slice(0, 4);
  $('recent-events').innerHTML = recentEvents.length
    ? recentEvents.map((event) => eventTemplate(event, { compact: true })).join('')
    : '<p class="empty-state">최근 이벤트가 없습니다.</p>';

  $('history-list').innerHTML = safeEvents.length
    ? safeEvents.map((event) => eventTemplate(event)).join('')
    : '<p class="empty-state">타임라인 로그가 비어 있습니다.</p>';

  const anomalyEvents = safeEvents.filter((event) => event.anomaly || event.confidence >= 0.8);
  $('anomaly-list').innerHTML = anomalyEvents.length
    ? anomalyEvents.map((event) => eventTemplate({ ...event, anomaly: true })).join('')
    : '<p class="empty-state">표시할 이상 이벤트가 없습니다.</p>';

  setText('event-count', String(safeEvents.length));
  setText('last-event-time', safeEvents[0]?.time || '-');
}

async function refreshTimeline() {
  clearNotice();
  const events = await state.client.getTimeline();
  renderTimeline(events);
}

function renderDetectResult(result) {
  const resultPanel = $('detect-result');
  const clipUrl = getClipUrl(result);

  resultPanel.hidden = false;
  resultPanel.innerHTML = `
    <div class="d-flex justify-content-between align-items-start gap-3">
      <div>
        <p class="mb-1 text-secondary small">분석 결과</p>
        <h6 class="text-light mb-2">${result.anomaly ? '이상 상황 감지' : '정상 프레임'}</h6>
        <p class="mb-0 small">
          class: <strong>${escapeHtml(result.class || 'unknown')}</strong>
          ${result.clip ? ` · clip: <strong>${escapeHtml(result.clip)}</strong>` : ''}
        </p>
      </div>
      <span class="badge ${result.anomaly ? 'text-bg-danger' : 'text-bg-success'}">${result.anomaly ? 'ANOMALY' : 'NORMAL'}</span>
    </div>
    ${clipUrl ? `<img src="${escapeHtml(clipUrl)}" alt="Detection evidence" class="detect-preview mt-3">` : ''}
  `;
}

function bindNavigation() {
  document.querySelectorAll('[data-page-target]').forEach((link) => {
    link.addEventListener('click', () => {
      const pageId = link.dataset.pageTarget;

      document.querySelectorAll('.page-content').forEach((page) => page.classList.remove('active'));
      document.querySelectorAll('[data-page-target]').forEach((navLink) => navLink.classList.remove('active'));

      $(`page-${pageId}`).classList.add('active');
      link.classList.add('active');
    });
  });
}

function bindApiControls() {
  const baseUrlInput = $('v50-base-url');
  baseUrlInput.value = state.client.baseUrl;

  $('save-base-url').addEventListener('click', () => {

    try {
      state.client.setBaseUrl(baseUrlInput.value);
      localStorage.setItem(BASE_URL_STORAGE_KEY, state.client.baseUrl);
      setNotice(`저장되었습니다: ${state.client.baseUrl}`, 'success');
      setText('health-message', `저장된 백엔드 주소: ${state.client.baseUrl}`);
    } catch (error) {
      setNotice(error.message, 'danger');
      setText('health-message', error.message);
    }
  });

  $('ping-node').addEventListener('click', (event) => {
    withButtonLoading(event.currentTarget, '확인 중', async () => {
      try {
        const message = await state.client.ping();
        setNodeStatus('Online', 'success');
        $('device-online-badge').className = 'badge rounded-pill text-bg-success';
        $('device-online-badge').textContent = 'Online';
        setText('health-message', message);
        setNotice('V50 노드와 연결되었습니다.', 'success');
      } catch (error) {
        setNodeStatus('Offline', 'danger');
        $('device-online-badge').className = 'badge rounded-pill text-bg-danger';
        $('device-online-badge').textContent = 'Offline';
        setText('health-message', error.message);
        setNotice(error.message, 'danger');
      }
    });
  });

  const configForm = $('config-form');
  if (configForm) {
    configForm.addEventListener('submit', (event) => {
      event.preventDefault();

      withButtonLoading($('apply-threshold'), '적용 중', async () => {
        try {
          const threshold = Number($('threshold-input').value);

          if (!Number.isFinite(threshold) || threshold < 0 || threshold > 1) {
            throw new Error('threshold는 0부터 1 사이의 숫자여야 합니다.');
          }

          const result = await state.client.updateConfig(threshold);
          setNotice(result.msg || result.message || '설정 변경 완료', 'success');
        } catch (error) {
          setNotice(error.message, 'danger');
        }
      });
    });
  }

  const detectForm = $('detect-form');
  if (detectForm) {
    detectForm.addEventListener('submit', (event) => {
      event.preventDefault();

      withButtonLoading($('run-detect'), '분석 중', async () => {
        try {
          const file = $('frame-file').files[0];

          if (!file) {
            throw new Error('분석할 이미지 파일을 선택해 주세요.');
          }

          const result = await state.client.detect(file);
          renderDetectResult(result);
          setNotice('프레임 분석 요청이 완료되었습니다.', 'success');
        } catch (error) {
          setNotice(error.message, 'danger');
        }
      });
    });
  }

  const refreshTimelineButton = $('refresh-timeline');
  if (refreshTimelineButton) {
    refreshTimelineButton.addEventListener('click', (event) => {
      withButtonLoading(event.currentTarget, '갱신 중', async () => {
        try {
          await refreshTimeline();
          setNotice('타임라인을 갱신했습니다.', 'success');
        } catch (error) {
          setNotice(error.message, 'danger');
        }
      });
    });
  }

  const swapModelButton = $('swap-model');
  if (swapModelButton) {
    swapModelButton.addEventListener('click', (event) => {
      withButtonLoading(event.currentTarget, '교체 중', async () => {
        try {
          const message = await state.client.swapModel();
          setNotice(message, 'success');
        } catch (error) {
          setNotice(error.message, 'danger');
        }
      });
    });
  }
}

function updateTime() {
  const now = new Date();
  const timeString = now.toLocaleTimeString('ko-KR', {
    timeZone: 'Asia/Seoul',
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
  });

  setText('current-time-display', timeString);
}

async function init() {
  bindNavigation();
  bindApiControls();
  updateTime();
  setInterval(updateTime, 60000);

  try {
    await refreshTimeline();
  } catch (error) {
    setNodeStatus('Unknown', 'secondary');
    renderTimeline([]);
    setNotice(`초기 타임라인 로드 실패: ${error.message}`, 'warning');
  }
}

init();
