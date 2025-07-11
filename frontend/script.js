// document.getElementById("xmlInput").addEventListener("input", () => {
//   const xmlText = document.getElementById("xmlInput").value.trim();
//   document.getElementById("analyseBtn").disabled = xmlText.length === 0;
// });

// document.getElementById("analyseBtn").addEventListener("click", async () => {
//   const xmlText = document.getElementById("xmlInput").value.trim();
//   if (!xmlText) return;

//   document.getElementById("loading").classList.remove("hidden");
//   document.getElementById("analyseBtn").disabled = true;

//   // === SIMULATION BEGIN ===
// //   setTimeout(() => {
// //     document.getElementById("loading").classList.add("hidden");
// //     document.getElementById("resultSection").classList.remove("hidden");

// //     const viewer = document.getElementById("pdfViewer");
// //     viewer.src = "dummy_report.pdf";

// //     document.getElementById("downloadBtn").onclick = () => {
// //       const a = document.createElement("a");
// //       a.href = "dummy_report.pdf";
// //       a.download = "HackDMSV_Report.pdf";
// //       a.click();
// //     };
// //   }, 3000); // Simulate delay

//   // === BACKEND INTEGRATION (Remove simulation when API is ready) ===
//   /*
//   const response = await fetch("http://localhost:8000/analyse-text", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json"
//     },
//     body: JSON.stringify({ xml: xmlText })
//   });

//   const blob = await response.blob();
//   const url = URL.createObjectURL(blob);

//   document.getElementById("loading").classList.add("hidden");
//   document.getElementById("resultSection").classList.remove("hidden");

//   document.getElementById("pdfViewer").src = url;

//   document.getElementById("downloadBtn").onclick = () => {
//     const a = document.createElement("a");
//     a.href = url;
//     a.download = "HackDMSV_Report.pdf";
//     a.click();
//   };
//   */
// });

document.addEventListener("DOMContentLoaded", () => {
  const analyseBtn = document.getElementById("analyseBtn");
  const inputField = document.getElementById("xmlInput");
  const loadingSection = document.getElementById("loading");
  const resultSection = document.getElementById("resultSection");
  const pdfViewer = document.getElementById("pdfViewer");

  let pollInterval;

  inputField.addEventListener("input", () => {
    analyseBtn.disabled = inputField.value.trim() === "";
  });

  analyseBtn.addEventListener("click", async () => {
    const inputValue = inputField.value.trim();
    if (!inputValue) return;

    loadingSection.classList.remove("hidden");
    resultSection.classList.add("hidden");

    try {
      // ✅ Corrected key from 'input' → 'target'
      const triggerResponse = await fetch(
        `http://127.0.0.1:8000/trigger_report?target=${encodeURIComponent(
          inputValue
        )}`,
        {
          method: "POST",
        }
      );

      const { report_id } = await triggerResponse.json();

      // Start polling
      pollInterval = setInterval(async () => {
        const statusRes = await fetch(
          `http://127.0.0.1:8000/status_report/${report_id}`
        );
        const { status } = await statusRes.json();
        console.log(status);
        if (
          statusRes.status === 200 &&
          statusRes.headers.get("Content-Type") === "application/pdf"
        ) {
          clearInterval(pollInterval);

          const blob = await statusRes.blob();
          const url = URL.createObjectURL(blob);

          pdfViewer.src = url;
          loadingSection.classList.add("hidden");
          resultSection.classList.remove("hidden");

          // Download button
          const downloadBtn = document.getElementById("downloadBtn");
          downloadBtn.onclick = () => {
            const a = document.createElement("a");
            a.href = url;
            a.download = "patch_report.pdf";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          };
        } else if (statusRes.status === 200 && status == "processing") {
          // Still processing or not available yet
          console.log("Waiting for report...");
        } else {
          clearInterval(pollInterval);
          loadingSection.classList.add("hidden");
          alert("Error fetching the report.");
        }
      }, 2000);
    } catch (error) {
      clearInterval(pollInterval);
      loadingSection.classList.add("hidden");
      alert("Failed to start analysis: " + error.message);
    }
  });
});
