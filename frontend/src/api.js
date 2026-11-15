const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error("Cannot reach the FlameBound API. Check that the backend is running.");
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(
      payload?.error?.message || `FlameBound API request failed (${response.status}).`
    );
  }
  return payload;
}

const postJson = (path, payload) => request(path, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

export const getHealth = () => request("/api/health");

export const runScenario = (payload) => postJson(
  "/api/atmosphere/oxygen-partial-pressure",
  payload,
);

export const askAssistant = (question, history = []) => postJson(
  "/api/assistant/chat",
  { question, history },
);
