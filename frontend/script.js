document.getElementById("xmlInput").addEventListener("input", () => {
  const xmlText = document.getElementById("xmlInput").value.trim();
  document.getElementById("analyseBtn").disabled = xmlText.length === 0;
});

document.getElementById("analyseBtn").addEventListener("click", async () => {
  const xmlText = document.getElementById("xmlInput").value.trim();
  if (!xmlText) return;

  document.getElementById("loading").classList.remove("hidden");
  document.getElementById("analyseBtn").disabled = true;

  // === SIMULATION BEGIN ===
  setTimeout(() => {
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("resultSection").classList.remove("hidden");

    const viewer = document.getElementById("pdfViewer");
    viewer.src = "dummy_report.pdf";

    document.getElementById("downloadBtn").onclick = () => {
      const a = document.createElement("a");
      a.href = "dummy_report.pdf";
      a.download = "HackDMSV_Report.pdf";
      a.click();
    };
  }, 3000); // Simulate delay

  // === BACKEND INTEGRATION (Remove simulation when API is ready) ===
  /*
  const response = await fetch("http://localhost:8000/analyse-text", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ xml: xmlText })
  });

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  document.getElementById("loading").classList.add("hidden");
  document.getElementById("resultSection").classList.remove("hidden");

  document.getElementById("pdfViewer").src = url;

  document.getElementById("downloadBtn").onclick = () => {
    const a = document.createElement("a");
    a.href = url;
    a.download = "HackDMSV_Report.pdf";
    a.click();
  };
  */
});
