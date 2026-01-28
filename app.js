// Root-site version (GitHub Pages publishing from repo root)
// This is intentionally kept in sync with docs/app.js, but with a different default base path.

const DEFAULT_BASE_PATH = "./output/";

/** @typedef {{ jersey_number: string, song: string, start_time?: string }} CsvRow */

const els = {
  csvFile: /** @type {HTMLInputElement} */ (document.getElementById("csvFile")),
  csvName: document.getElementById("csvName"),
  loadExample: document.getElementById("loadExample"),
  basePath: /** @type {HTMLInputElement} */ (document.getElementById("basePath")),
  renderBtn: document.getElementById("renderBtn"),
  csvTableBody: document.getElementById("csvTableBody"),
  csvCount: document.getElementById("csvCount"),
  csvFound: document.getElementById("csvFound"),
  csvMissing: document.getElementById("csvMissing"),
  allCount: document.getElementById("allCount"),
  filesList: document.getElementById("filesList"),
  filter: /** @type {HTMLInputElement} */ (document.getElementById("filter")),
  refreshManifest: document.getElementById("refreshManifest"),
};

/** @type {CsvRow[] | null} */
let currentRows = null;

/** @type {Set<string>} */
let availableFiles = new Set();

/** @type {string[]} */
let availableFileList = [];

function normalizeBasePath(p) {
  const trimmed = (p ?? "").trim() || DEFAULT_BASE_PATH;
  return trimmed.endsWith("/") ? trimmed : `${trimmed}/`;
}

function escapeHtml(s) {
  return (s ?? "").replace(/[&<>"']/g, (c) => {
    switch (c) {
      case "&":
        return "&amp;";
      case "<":
        return "&lt;";
      case ">":
        return "&gt;";
      case '"':
        return "&quot;";
      case "'":
        return "&#039;";
      default:
        return c;
    }
  });
}

function parseCsv(text) {
  /** @type {string[][]} */
  const rows = [];
  /** @type {string[]} */
  let row = [];
  let field = "";
  let i = 0;
  let inQuotes = false;

  const pushField = () => {
    row.push(field);
    field = "";
  };

  const pushRow = () => {
    if (row.length === 1 && row[0] === "" && rows.length > 0) return;
    rows.push(row);
    row = [];
  };

  while (i < text.length) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        const next = text[i + 1];
        if (next === '"') {
          field += '"';
          i += 2;
          continue;
        }
        inQuotes = false;
        i += 1;
        continue;
      }
      field += ch;
      i += 1;
      continue;
    }

    if (ch === '"') {
      inQuotes = true;
      i += 1;
      continue;
    }
    if (ch === ",") {
      pushField();
      i += 1;
      continue;
    }
    if (ch === "\n") {
      pushField();
      pushRow();
      i += 1;
      continue;
    }
    if (ch === "\r") {
      i += 1;
      continue;
    }
    field += ch;
    i += 1;
  }

  pushField();
  if (row.length > 1 || row[0] !== "" || rows.length === 0) pushRow();
  return rows;
}

function csvToObjects(csvText) {
  const rows = parseCsv(csvText);
  if (rows.length === 0) return [];
  const headers = rows[0].map((h) => (h ?? "").trim());

  const idxJersey = headers.findIndex((h) => h === "jersey_number");
  const idxSong = headers.findIndex((h) => h === "song");
  const idxStart = headers.findIndex((h) => h === "start_time");

  if (idxJersey === -1 || idxSong === -1) {
    throw new Error("CSV must have headers: jersey_number, song (start_time optional)");
  }

  /** @type {CsvRow[]} */
  const out = [];
  for (let r = 1; r < rows.length; r++) {
    const cols = rows[r];
    const jersey = (cols[idxJersey] ?? "").trim();
    const song = (cols[idxSong] ?? "").trim();
    const start_time = idxStart !== -1 ? (cols[idxStart] ?? "").trim() : "";
    if (!jersey || !song) continue;
    out.push({ jersey_number: jersey, song, ...(start_time ? { start_time } : {}) });
  }
  return out;
}

function setPill(el, text) {
  if (!el) return;
  el.textContent = text;
}

function buildOutputUrl(basePath, jersey) {
  const name = `${jersey}.mp3`;
  return `${normalizeBasePath(basePath)}${encodeURIComponent(name)}`;
}

function renderCsvTable(rows, basePath) {
  const body = els.csvTableBody;
  body.innerHTML = "";

  let found = 0;
  let missing = 0;

  for (const row of rows) {
    const jersey = row.jersey_number;
    const fileName = `${jersey}.mp3`;
    const url = buildOutputUrl(basePath, jersey);
    const isFound = availableFiles.has(fileName);

    if (isFound) found += 1;
    else missing += 1;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${escapeHtml(jersey)}</strong></td>
      <td>${escapeHtml(row.song)}</td>
      <td>${escapeHtml(row.start_time ?? "0")}</td>
      <td>
        ${
          isFound
            ? `<span class="badge ok">found</span> <a class="link" href="${url}" download="${escapeHtml(
                fileName,
              )}">${escapeHtml(fileName)}</a>`
            : `<span class="badge bad">missing</span> <span class="muted">${escapeHtml(
                fileName,
              )}</span>`
        }
      </td>
      <td>
        ${
          isFound
            ? `<audio class="audio" controls preload="none" src="${url}"></audio>`
            : `<span class="muted">—</span>`
        }
      </td>
    `;
    body.appendChild(tr);
  }

  setPill(els.csvCount, `${rows.length} rows`);
  setPill(els.csvFound, `${found} found`);
  setPill(els.csvMissing, `${missing} missing`);

  if (rows.length === 0) {
    body.innerHTML = `<tr><td colspan="5" class="muted">No valid rows found.</td></tr>`;
  }
}

function renderFilesList(basePath, filterText) {
  const q = (filterText ?? "").trim().toLowerCase();
  const list = q
    ? availableFileList.filter((f) => f.toLowerCase().includes(q))
    : availableFileList.slice();

  setPill(els.allCount, `${list.length} files`);

  if (list.length === 0) {
    els.filesList.classList.add("muted");
    els.filesList.textContent = q ? "No matches." : "No files found in manifest.";
    return;
  }

  els.filesList.classList.remove("muted");
  els.filesList.innerHTML = "";

  for (const name of list) {
    const url = `${normalizeBasePath(basePath)}${encodeURIComponent(name)}`;
    const div = document.createElement("div");
    div.className = "file-item";
    div.innerHTML = `
      <div class="name">${escapeHtml(name)}</div>
      <div class="actions">
        <a class="link" href="${url}" download="${escapeHtml(name)}">download</a>
        <audio class="audio" controls preload="none" src="${url}"></audio>
      </div>
    `;
    els.filesList.appendChild(div);
  }
}

async function loadManifest() {
  const url = `./manifest.json?ts=${Date.now()}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to load manifest.json (${res.status})`);
  }
  const json = await res.json();
  if (!json || !Array.isArray(json.files)) {
    throw new Error("manifest.json is invalid (expected { files: string[] })");
  }
  availableFileList = json.files
    .slice()
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  availableFiles = new Set(availableFileList);
}

async function initManifest() {
  setPill(els.allCount, "Loading…");
  els.filesList.classList.add("muted");
  els.filesList.textContent = "Loading manifest…";
  try {
    await loadManifest();
    const basePath = normalizeBasePath(els.basePath.value);
    renderFilesList(basePath, els.filter.value);
    if (currentRows) renderCsvTable(currentRows, basePath);
  } catch (e) {
    setPill(els.allCount, "Error");
    els.filesList.classList.add("muted");
    els.filesList.textContent =
      e instanceof Error ? e.message : "Failed to load manifest.json.";
  }
}

function readFileText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Failed to read file."));
    reader.onload = () => resolve(String(reader.result ?? ""));
    reader.readAsText(file);
  });
}

async function onRender() {
  const basePath = normalizeBasePath(els.basePath.value);
  if (!currentRows) {
    els.csvTableBody.innerHTML =
      '<tr><td colspan="5" class="muted">Upload a CSV and click Render.</td></tr>';
    setPill(els.csvCount, "0 rows");
    setPill(els.csvFound, "0 found");
    setPill(els.csvMissing, "0 missing");
    renderFilesList(basePath, els.filter.value);
    return;
  }
  renderCsvTable(currentRows, basePath);
  renderFilesList(basePath, els.filter.value);
}

els.basePath.value = normalizeBasePath(els.basePath.value || DEFAULT_BASE_PATH);

els.csvFile.addEventListener("change", async () => {
  const file = els.csvFile.files?.[0] ?? null;
  els.csvName.textContent = file ? file.name : "No file selected";
  if (!file) {
    currentRows = null;
    await onRender();
    return;
  }
  try {
    const text = await readFileText(file);
    currentRows = csvToObjects(text);
    await onRender();
  } catch (e) {
    currentRows = null;
    els.csvTableBody.innerHTML = `<tr><td colspan="5" class="muted">${
      e instanceof Error ? escapeHtml(e.message) : "Failed to parse CSV."
    }</td></tr>`;
    setPill(els.csvCount, "0 rows");
    setPill(els.csvFound, "0 found");
    setPill(els.csvMissing, "0 missing");
  }
});

els.loadExample.addEventListener("click", async () => {
  try {
    const res = await fetch("./example.csv", { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to load example.csv (${res.status})`);
    const text = await res.text();
    currentRows = csvToObjects(text);
    els.csvName.textContent = "example.csv (loaded)";
    await onRender();
  } catch (e) {
    currentRows = null;
    els.csvName.textContent = "No file selected";
    els.csvTableBody.innerHTML = `<tr><td colspan="5" class="muted">${
      e instanceof Error ? escapeHtml(e.message) : "Failed to load example.csv."
    }</td></tr>`;
  }
});

els.renderBtn.addEventListener("click", onRender);
els.filter.addEventListener("input", () =>
  renderFilesList(normalizeBasePath(els.basePath.value), els.filter.value),
);
els.refreshManifest.addEventListener("click", initManifest);

initManifest();

