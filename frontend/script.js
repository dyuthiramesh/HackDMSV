let selectedFile = null;

function handleFiles(files) {
  const file = files[0];
  const fileNameDisplay = document.getElementById("fileName");

  if (file && file.name.endsWith(".xml")) {
    selectedFile = file;
    document.getElementById("analyseBtn").disabled = false;
    fileNameDisplay.textContent = `📄 Uploaded: ${file.name}`;
  } else {
    alert("Please upload a valid .xml file");
    fileNameDisplay.textContent = "";
    document.getElementById("analyseBtn").disabled = true;
  }
}

document.getElementById("analyseBtn").addEventListener("click", async () => {
  if (!selectedFile) return;

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
  // === SIMULATION END ===

  // === BACKEND INTEGRATION (Remove above when using API) ===
  /*
  const formData = new FormData();
  formData.append("file", selectedFile);

  const response = await fetch("http://localhost:8000/analyse", {
    method: "POST",
    body: formData,
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
