# V50 Edge Dashboard API Design

## Goal

Connect the existing Flask + Vanilla JS dashboard to the V50 edge node API so the page can monitor node health, update inference settings, submit image frames, render inference results, list timeline events, and display evidence clips.

## Approach

Keep the current frontend structure. Flask continues to serve `templates/index.html`, while browser-side ES modules under `static/js/` handle all V50 API calls and dashboard behavior.

## Architecture

- `static/js/v50Api.mjs` owns API communication only.
- `static/js/dashboard.mjs` owns DOM state, event handlers, and rendering.
- `templates/index.html` owns markup, Bootstrap styling, and stable element IDs.

The V50 base URL is editable in the UI and saved in `localStorage`, because the phone IP address may change between networks.

## API Behavior

- `GET /ping` returns plain text and drives node status.
- `POST /api/config` sends JSON `{ "threshold": number }`.
- `POST /api/detect` sends the selected `File` or `Blob` directly as binary data, without JSON content type.
- `GET /api/timeline` returns timeline event objects.
- Clip images render by joining the base URL with each `clip_url`.
- `POST /api/model/swap` returns plain text.

## Error Handling

Every API method supports timeout via `AbortController`. Errors are normalized into readable messages for the UI. The dashboard shows connection failures without breaking navigation.

## Testing

Use a small Node test file with built-in `assert` and mocked `fetch`. Tests cover URL construction, JSON requests, binary detect requests, text responses, timeout wiring, and clip URL rendering helpers.
