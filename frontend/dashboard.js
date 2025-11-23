const API_BASE = "http://localhost:8000";

function render(targetId, data) {
  const el = document.getElementById(targetId);
  el.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

async function fetchJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

document.getElementById("email-btn").addEventListener("click", async () => {
  const email = document.getElementById("email-input").value;
  const apiKey = document.getElementById("api-key-input").value;
  try {
    const data = await fetchJSON(`${API_BASE}/scan-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, api_key: apiKey || null })
    });
    render("email-result", data);
  } catch (err) {
    render("email-result", err.message);
  }
});

document.getElementById("password-btn").addEventListener("click", async () => {
  const password = document.getElementById("password-input").value;
  try {
    const data = await fetchJSON(`${API_BASE}/scan-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password })
    });
    render("password-result", data);
  } catch (err) {
    render("password-result", err.message);
  }
});

document.getElementById("username-btn").addEventListener("click", async () => {
  const username = document.getElementById("username-input").value;
  try {
    const data = await fetchJSON(`${API_BASE}/scan-username`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });
    render("username-result", data);
  } catch (err) {
    render("username-result", err.message);
  }
});

async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

document.getElementById("image-btn").addEventListener("click", async () => {
  const file = document.getElementById("image-file").files[0];
  if (!file) {
    render("image-result", "Please choose an image file.");
    return;
  }
  try {
    const base64 = await fileToBase64(file);
    const data = await fetchJSON(`${API_BASE}/scan-image`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_base64: base64 })
    });
    render("image-result", data);
  } catch (err) {
    render("image-result", err.message);
  }
});

document.getElementById("upload-btn").addEventListener("click", async () => {
  const file = document.getElementById("dataset-file").files[0];
  if (!file) {
    render("upload-result", "Please select a TXT or CSV file.");
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  try {
    const data = await fetchJSON(`${API_BASE}/upload-dataset`, {
      method: "POST",
      body: formData
    });
    render("upload-result", data);
  } catch (err) {
    render("upload-result", err.message);
  }
});

function collectLatestResults() {
  let email = {};
  let password = {};
  let username = {};
  let image = {};
  try { email = JSON.parse(document.getElementById("email-result").textContent); } catch (e) {}
  try { password = JSON.parse(document.getElementById("password-result").textContent); } catch (e) {}
  try { username = JSON.parse(document.getElementById("username-result").textContent); } catch (e) {}
  try { image = JSON.parse(document.getElementById("image-result").textContent); } catch (e) {}
  return { email, password, username, image };
}

document.getElementById("risk-btn").addEventListener("click", async () => {
  const { email, password, username, image } = collectLatestResults();
  const payload = {
    email_breaches: email.breaches || [],
    password_occurrences: password.occurrences || 0,
    username_matches: username.matches || {},
    faces_detected: image.faces_detected || 0
  };
  try {
    const data = await fetchJSON(`${API_BASE}/ai-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    render("risk-result", data);
  } catch (err) {
    render("risk-result", err.message);
  }
});
