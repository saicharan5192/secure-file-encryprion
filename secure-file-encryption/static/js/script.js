function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function setupDropzone(inputId, dropzoneId, infoId) {
  const input = document.getElementById(inputId);
  const zone = document.getElementById(dropzoneId);
  const info = document.getElementById(infoId);
  if (!input || !zone || !info) return;

  const show = () => {
    const file = input.files[0];
    if (!file) {
      info.classList.add("hidden");
      return;
    }
    info.classList.remove("hidden");
    info.innerHTML = `<strong>${escapeHtml(file.name)}</strong><span>${formatBytes(file.size)}</span>`;
  };

  input.addEventListener("change", show);
  ["dragenter", "dragover"].forEach(evt => zone.addEventListener(evt, e => {
    e.preventDefault();
    zone.classList.add("dragging");
  }));
  ["dragleave", "drop"].forEach(evt => zone.addEventListener(evt, e => {
    e.preventDefault();
    zone.classList.remove("dragging");
  }));
  zone.addEventListener("drop", e => {
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      show();
    }
  });
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" }[c]));
}

function setLoading(button, loading, text) {
  button.disabled = loading;
  button.innerHTML = loading ? `<span class="spinner"></span> ${text}` : text;
}

function resultCard(target, success, html) {
  target.innerHTML = `<div class="result-card ${success ? "result-success" : "result-error"}">${html}</div>`;
}

setupDropzone("encryptFile", "encryptDropzone", "encryptFileInfo");
setupDropzone("decryptFile", "decryptDropzone", "decryptFileInfo");

const encryptForm = document.getElementById("encryptForm");
if (encryptForm) {
  encryptForm.addEventListener("submit", async e => {
    e.preventDefault();
    const file = document.getElementById("encryptFile").files[0];
    const password = document.getElementById("encPassword").value;
    const confirm = document.getElementById("encConfirm").value;
    const button = document.getElementById("encryptBtn");
    const result = document.getElementById("encryptResult");

    if (!file) return resultCard(result, false, "<b>No file selected.</b><p>Please choose a file first.</p>");
    if (!password) return resultCard(result, false, "<b>Password required.</b><p>Enter a password before encrypting.</p>");
    if (password !== confirm) return resultCard(result, false, "<b>Password mismatch.</b><p>The two password fields must match.</p>");

    const data = new FormData();
    data.append("file", file);
    data.append("password", password);
    data.append("confirm_password", confirm);

    setLoading(button, true, "Encrypting...");
    try {
      const response = await fetch("/api/encrypt", { method: "POST", body: data });
      const json = await response.json();
      if (!json.success) throw new Error(json.message || "Encryption failed.");
      resultCard(result, true, `
        <div class="result-head"><span class="badge success">SUCCESS</span><b>File encrypted successfully</b></div>
        <p><b>Input:</b> ${escapeHtml(json.input_file)}</p>
        <p><b>Algorithm:</b> AES-256-GCM</p>
        <p><b>Encrypted File:</b> ${escapeHtml(json.encrypted_file)}</p>
        <p class="hash"><b>Original SHA-256:</b><br>${escapeHtml(json.sha256)}</p>
        <div class="result-actions"><a class="btn primary" href="${json.download_url}">Download Encrypted File</a><a class="btn secondary" href="/encrypt">Encrypt Another</a></div>
      `);
    } catch (err) {
      resultCard(result, false, `<b>Encryption failed.</b><p>${escapeHtml(err.message)}</p>`);
    } finally {
      setLoading(button, false, "Encrypt File");
    }
  });
}

const decryptForm = document.getElementById("decryptForm");
if (decryptForm) {
  decryptForm.addEventListener("submit", async e => {
    e.preventDefault();
    const file = document.getElementById("decryptFile").files[0];
    const password = document.getElementById("decPassword").value;
    const button = document.getElementById("decryptBtn");
    const result = document.getElementById("decryptResult");

    if (!file) return resultCard(result, false, "<b>No encrypted file selected.</b><p>Please choose a .enc file first.</p>");
    if (!password) return resultCard(result, false, "<b>Password required.</b><p>Enter the encryption password.</p>");

    const data = new FormData();
    data.append("file", file);
    data.append("password", password);

    setLoading(button, true, "Decrypting...");
    try {
      const response = await fetch("/api/decrypt", { method: "POST", body: data });
      const json = await response.json();
      if (!json.success) throw new Error(json.message || "Decryption failed.");
      const match = json.verification === "MATCH";
      resultCard(result, match, `
        <div class="result-head"><span class="badge ${match ? "success" : "danger"}">${escapeHtml(json.status)}</span><b>Decryption ${match ? "successful" : "failed"}</b></div>
        <p><b>Recovered File:</b> ${escapeHtml(json.recovered_file)}</p>
        <p><b>Verification:</b> <span class="badge success">${escapeHtml(json.verification)}</span></p>
        <p class="hash"><b>Original SHA-256:</b><br>${escapeHtml(json.original_hash)}<br><br><b>Recovered SHA-256:</b><br>${escapeHtml(json.recovered_hash)}</p>
        <div class="result-actions"><a class="btn primary" href="${json.download_url}">Download Recovered File</a></div>
      `);
    } catch (err) {
      resultCard(result, false, `<div class="result-head"><span class="badge danger">FAILED</span><b>Decryption unsuccessful</b></div><p>Incorrect key/password or corrupted encrypted file. Decryption unsuccessful.</p>`);
    } finally {
      setLoading(button, false, "Decrypt File");
    }
  });
}
