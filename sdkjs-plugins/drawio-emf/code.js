/* global window, document */
(function () {
  // NOTE:
  // - During local development this points to your local FastAPI service.
  // - In production you will point to your deployed service (e.g., https://your-domain/convert/emf).
  // Environment-aware API URL configuration
  const isDevelopment = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  const API_URL = isDevelopment 
    ? "http://127.0.0.1:9000/convert/emf"
    : (window.API_EMF_URL || window.location.origin + "/api/convert/emf");

  function setStatus(msg) {
    const el = document.getElementById("status");
    if (el) el.textContent = msg;
  }

  function getSelectedFile() {
    const input = document.getElementById("file");
    if (!input || !input.files || input.files.length === 0) return null;
    return input.files[0];
  }

  async function convertAndDownload(file) {
    try {
      setStatus("Uploading .drawio and converting to EMF...");

      const formData = new FormData();
      // IMPORTANT: API expects the form field name to be "file"
      formData.append("file", file);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
        headers: {
          // Add auth header if available (for secure endpoints)
          ...(window.AUTH_TOKEN && { "Authorization": "Bearer " + window.AUTH_TOKEN })
        }
      });

      if (!response.ok) {
        const errorMsg = await response.text();
        setStatus("Server error: " + response.status + "\n" + errorMsg);
        console.error("[drawio-emf]", response.status, errorMsg);
        return;
      }

      // We expect an EMF binary payload
      const blob = await response.blob();
      
      // Validate blob
      if (blob.size === 0) {
        setStatus("Error: Server returned empty file. Check conversion service.");
        return;
      }

      // Force download in the browser
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // Use a deterministic output name
      const baseName = (file.name || "diagram.drawio").replace(/\.drawio$/i, "");
      a.download = baseName + ".emf";

      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);
      setStatus("✓ Done. EMF downloaded: " + a.download);
    } catch (err) {
      const errMsg = err && err.message ? err.message : String(err);
      setStatus("Client error: " + errMsg + "\n(Check API_URL and network connection)");
      console.error("[drawio-emf] Error:", err);
    }
  }

  function wireUI() {
    const btn = document.getElementById("btnConvert");
    if (!btn) return;

    btn.addEventListener("click", async () => {
      const file = getSelectedFile();
      if (!file) {
        setStatus("Please choose a .drawio file first.");
        return;
      }
      
      // Validate file extension
      if (!file.name.toLowerCase().endsWith(".drawio")) {
        setStatus("Error: Please select a .drawio file.");
        return;
      }
      
      // Check file size (max 50MB)
      const maxSize = 50 * 1024 * 1024;
      if (file.size > maxSize) {
        setStatus("Error: File is too large. Maximum size: 50MB.");
        return;
      }
      
      await convertAndDownload(file);
    });

    // Log API endpoint for debugging
    console.log("[drawio-emf] Initialized. API endpoint:", API_URL);
    setStatus("Ready. Select a .drawio file and click Convert.");
  }

  wireUI();
})();
