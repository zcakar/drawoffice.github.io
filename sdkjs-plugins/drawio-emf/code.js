/* global window, document */
(function () {
  // NOTE:
  // - During local development this points to your local FastAPI service.
  // - In production you will point to your deployed service (e.g., https://your-domain/convert/emf).
  const API_URL = "http://127.0.0.1:9000/convert/emf";

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
      });

      if (!response.ok) {
        setStatus("Server error: " + response.status + "\n" + (await response.text()));
        return;
      }

      // We expect an EMF binary payload
      const blob = await response.blob();

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
      setStatus("Done. EMF downloaded: " + a.download);
    } catch (err) {
      setStatus("Client error: " + (err && err.message ? err.message : String(err)));
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
      await convertAndDownload(file);
    });

    setStatus("Ready. Select a .drawio file and click Convert.");
  }

  wireUI();
})();
