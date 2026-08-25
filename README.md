# Ankit Mukherjee — Conference Poster & Digital Contact Card

A lightweight, mobile-first academic contact card and conference poster distribution website designed for **GIC 2026** (*Genomics International Conference*).

When conference attendees scan the QR code on your printed poster, this page opens instantly in their mobile browser, allowing them to download the full poster PDF, zoom into figures, and save your complete contact details directly into their phone's Contacts app.

---

## 🎯 Features

- 📄 **Direct Poster Download**: Instant 1-tap download of the full-resolution poster PDF (`Ankit_Mukherjee_Poster_GIC2026.pdf` · 2.1 MB).
- 🔍 **Interactive Poster Viewer**: Built-in modal lightbox to inspect and zoom figures directly on mobile or desktop without leaving the webpage.
- 📇 **1-Tap Save Contact (.vcf)**: One-click export to iOS Contacts and Android Google Contacts with name, affiliation, phone, email, poster link, LinkedIn, Google Scholar, ORCID, and GitHub.
- 📋 **1-Click Copy**: Instant clipboard copy for Email and Phone with toast notification.
- 🔗 **Verified Academic Links**: Direct links to LinkedIn, Google Scholar, ORCID, and GitHub profiles.
- ⚡ **Zero Build Step**: Pure static HTML5, CSS3, and modern Vanilla JS — ultra-fast loading even on slow conference Wi-Fi / cellular data.
- 📱 **Mobile-First & Responsive**: Designed for iPhone, Android, tablets, and desktop displays.

---

## 🏷️ Presentation Details

- **Presenter**: Ankit Mukherjee
- **Designation**: Researcher
- **Affiliation**: CSIR–Institute of Genomics and Integrative Biology (CSIR-IGIB), New Delhi, India
- **Conference**: GIC 2026
- **Poster Title**: *Landscape of Clinically Actionable Pharmacogenomic Variation Across Diverse Indian Populations from the GenomeIndia Project*
- **Research Keywords**: Genomics · Pharmacogenomics · Bioinformatics · Population Genomics · Precision Medicine · GenomeIndia

---

## 🖼️ QR Codes for Poster Printing

All QR code assets are stored in the [`assets/`](assets/) directory:

| Asset | Format | Recommended Use |
| :--- | :--- | :--- |
| [`assets/qr-code.svg`](assets/qr-code.svg) | **Vector SVG** | **Recommended for Poster Design** (PowerPoint, LaTeX, Illustrator, Canva, InDesign). Infinite resolution, never pixelates. |
| [`assets/qr-code-print-300dpi.png`](assets/qr-code-print-300dpi.png) | **Raster PNG (300 DPI)** | High-resolution 2400×2400 raster image for Photoshop or direct printing. |
| [`assets/poster-badge-qr.svg`](assets/poster-badge-qr.svg) | **Vector Badge SVG** | Ready-made corner badge with *"SCAN FOR POSTER & CONTACT"* header and presenter details. |
| [`assets/qr-contact-card.png`](assets/qr-contact-card.png) | **Web PNG** | Compact QR code for web footer and digital sharing. |

### 🖨️ Printing Guidelines for Poster Board:
1. **Size**: Print the QR code at a minimum size of **3.5 cm × 3.5 cm (1.4 in × 1.4 in)**. If attendees will scan from a distance of 1–1.5 meters, print it at **5 cm × 5 cm (2.0 in × 2.0 in)**.
2. **Placement**: Place the QR code in either the **top-right** or **bottom-right** corner of your poster board with clear contrast against the poster background.
3. **Quiet Zone**: Keep the built-in white margin around the QR code intact so smartphone cameras can detect it rapidly under conference hall lighting.

---

## 🚀 Instant GitHub Pages Deployment (3 Steps)

### Step 1: Initialize Git and Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Conference poster contact card & print QR"
git branch -M main
git remote add origin https://github.com/AnkitMukherji/ankit-research-contact-card.git
git push -u origin main
```

### Step 2: Enable GitHub Pages
1. Go to your repository on GitHub: `https://github.com/AnkitMukherji/ankit-research-contact-card`
2. Click **Settings** > **Pages** (in the left sidebar).
3. Under **Build and deployment** > **Branch**:
   - Select `main` branch.
   - Select `/(root)` folder.
   - Click **Save**.
4. Within 30–60 seconds, your site will be live at:
   ```
   https://ankitmukherji.github.io/ankit-research-contact-card/
   ```

---

## 🖨️ QR Code Generation Script

You can regenerate QR codes at any time with custom URLs or settings:

```bash
python3 scripts/generate_qr.py --url https://ankitmukherji.github.io/ankit-research-contact-card/
```

---

## 📂 Repository Structure

```text
ankit-research-contact-card/
├── index.html                           # Main contact card webpage
├── styles.css                           # Responsive academic card styles
├── script.js                            # Dynamic vCard builder, copy toasts, & poster modal
├── contact.vcf                          # Pre-generated static vCard file
├── Ankit_Mukherjee_Poster_GIC2026.pdf   # Full conference poster PDF (2.1 MB)
├── README.md                            # Documentation & deployment guide
├── .gitignore                           # Git ignore rules
├── assets/
│   ├── qr-code.svg                      # Vector QR code (infinite resolution)
│   ├── qr-code-print-300dpi.png         # 300 DPI high-res QR code for printing
│   ├── poster-badge-qr.svg              # Ready-to-paste poster corner badge
│   ├── qr-contact-card.png              # Web-optimized QR code
│   └── poster-preview.png               # Fast-loading poster thumbnail
└── scripts/
    └── generate_qr.py                   # Zero-dependency QR generation script
```

---

## 👤 Author Contact

- **Ankit Mukherjee** — CSIR-IGIB
- **Email**: [ankit0204.am@gmail.com](mailto:ankit0204.am@gmail.com)
- **LinkedIn**: [linkedin.com/in/ankit-mukherjee-647ab81ba](https://www.linkedin.com/in/ankit-mukherjee-647ab81ba)
- **Google Scholar**: [scholar.google.com](https://scholar.google.com/citations?user=2D5kUnQAAAAJ&hl=en)
- **ORCID**: [0009-0005-5847-5986](https://orcid.org/0009-0005-5847-5986)
- **GitHub**: [@AnkitMukherji](https://github.com/AnkitMukherji)
