/**
 * script.js — Conference Contact Card & Poster Presenter Interactivity
 * Author: Ankit Mukherjee (CSIR-IGIB)
 */

// ==============================================================================
// 1. Central Contact & Presentation Details
// ==============================================================================
const contactData = {
  name: "Ankit Mukherjee",
  organisation: "CSIR–Institute of Genomics and Integrative Biology",
  title: "Researcher",
  email: "ankit0204.am@gmail.com",
  phone: "+919330111538",
  phoneDisplay: "+91 93301 11538",
  linkedin: "https://www.linkedin.com/in/ankit-mukherjee-647ab81ba",
  scholar: "https://scholar.google.com/citations?user=2D5kUnQAAAAJ&hl=en",
  orcid: "https://orcid.org/0009-0005-5847-5986",
  github: "https://github.com/AnkitMukherji",
  website: "https://ankitmukherji.github.io/ankit-research-contact-card/",
  posterUrl: "https://ankitmukherji.github.io/ankit-research-contact-card/Ankit_Mukherjee_Poster_GIC2026.pdf",
  posterTitle: "Landscape of Clinically Actionable Pharmacogenomic Variation Across Diverse Indian Populations from the GenomeIndia Project",
  conference: "GIC 2026",
  note: "Researcher at CSIR-IGIB. Poster presentation at GIC 2026: Pharmacogenomics across Indian populations (GenomeIndia Project). Focus: Genomics, Pharmacogenomics, Population Genomics, Bioinformatics."
};

// ==============================================================================
// 2. vCard 3.0 Generation & Download (iOS, Android, macOS, Windows compatible)
// ==============================================================================
function escapeVCard(str) {
  if (!str) return "";
  return String(str)
    .replace(/\\/g, "\\\\")
    .replace(/;/g, "\\;")
    .replace(/,/g, "\\,")
    .replace(/\n/g, "\\n");
}

function buildVCard() {
  const parts = contactData.name.trim().split(/\s+/);
  const firstName = parts[0] || "";
  const lastName = parts.length > 1 ? parts.slice(1).join(" ") : "";

  const lines = [
    "BEGIN:VCARD",
    "VERSION:3.0",
    `N:${escapeVCard(lastName)};${escapeVCard(firstName)};;;`,
    `FN:${escapeVCard(contactData.name)}`,
    `ORG:${escapeVCard(contactData.organisation)}`,
    `TITLE:${escapeVCard(contactData.title)}`,
    `TEL;TYPE=CELL,VOICE,PREF:${contactData.phone}`,
    `EMAIL;TYPE=INTERNET,PREF:${contactData.email}`,
    `URL;TYPE=WORK:${contactData.website}`,
    `URL;TYPE=POSTER:${contactData.posterUrl}`,
    `X-ABLabel:Poster PDF`,
    `URL;TYPE=LinkedIn:${contactData.linkedin}`,
    `URL;TYPE=Google Scholar:${contactData.scholar}`,
    `URL;TYPE=ORCID:${contactData.orcid}`,
    `URL;TYPE=GitHub:${contactData.github}`,
    `NOTE:${escapeVCard(contactData.note)}`,
    "END:VCARD"
  ];

  return lines.join("\r\n");
}

function downloadVCard() {
  const vcfString = buildVCard();
  const blob = new Blob([vcfString], { type: "text/vcard;charset=utf-8" });
  const downloadUrl = URL.createObjectURL(blob);
  const tempLink = document.createElement("a");
  tempLink.href = downloadUrl;
  tempLink.download = `${contactData.name.toLowerCase().replace(/\s+/g, "_")}.vcf`;
  document.body.appendChild(tempLink);
  tempLink.click();
  document.body.removeChild(tempLink);
  setTimeout(() => URL.revokeObjectURL(downloadUrl), 1500);

  showToast("✓ Contact file (.vcf) downloaded!");
}

// ==============================================================================
// 3. Toast Notifications
// ==============================================================================
let toastTimer = null;
function showToast(message) {
  const toast = document.getElementById("toastNotification");
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add("show");

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2800);
}

// ==============================================================================
// 4. Clipboard Copy with Fallback
// ==============================================================================
async function copyToClipboard(text, label = "Item") {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      // Fallback for non-https / older browsers
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      textarea.style.top = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    showToast(`✓ ${label} copied to clipboard!`);
  } catch (err) {
    showToast(`Failed to copy: ${text}`);
  }
}

// ==============================================================================
// 5. Poster Lightbox / Modal
// ==============================================================================
function initPosterModal() {
  const modal = document.getElementById("posterModal");
  const openThumbBtn = document.getElementById("openPosterPreviewBtn");
  const previewBtn = document.getElementById("previewPosterBtn");
  const closeBtn = document.getElementById("closeModalBtn");
  const modalBody = document.getElementById("modalBody");
  const modalImg = document.getElementById("modalPosterImg");

  if (!modal) return;

  function openModal() {
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (modalBody) modalBody.classList.remove("is-zoomed");
  }

  if (openThumbBtn) openThumbBtn.addEventListener("click", openModal);
  if (previewBtn) previewBtn.addEventListener("click", openModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  // Close on backdrop click
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // Toggle Zoom inside modal
  if (modalBody) {
    modalBody.addEventListener("click", (e) => {
      if (e.target === modalImg || e.target === modalBody) {
        modalBody.classList.toggle("is-zoomed");
      }
    });
  }

  // Keyboard accessibility
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("is-open")) {
      closeModal();
    }
  });
}

// ==============================================================================
// 6. DOM Initialization
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
  // Update year
  const yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Save Contact button handler
  const saveContactBtn = document.getElementById("saveContactBtn");
  if (saveContactBtn) {
    saveContactBtn.addEventListener("click", downloadVCard);
  }

  // Copy buttons
  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const textToCopy = btn.getAttribute("data-copy");
      const label = btn.getAttribute("aria-label")?.replace("Copy ", "") || "Text";
      if (textToCopy) {
        copyToClipboard(textToCopy, label);
      }
    });
  });

  // Initialize modal
  initPosterModal();
});
