const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export async function getHealth(){const r=await fetch(`${API_BASE}/health`);if(!r.ok)throw new Error("Health check failed");return r.json();}
export async function runScenario(payload){const r=await fetch(`${API_BASE}/api/scenario`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});if(!r.ok)throw new Error("Scenario request failed");return r.json();}
export async function askAssistant(question){const r=await fetch(`${API_BASE}/api/assistant`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question})});if(!r.ok)throw new Error("Assistant request failed");return r.json();}
