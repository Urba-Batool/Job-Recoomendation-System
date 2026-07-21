const PRESETS = {
    "data-science": ["python", "sql", "machine learning", "pandas", "numpy", "scikit-learn", "statistics"],
    "frontend": ["javascript", "react", "html", "css", "typescript", "git"],
    "devops": ["docker", "kubernetes", "aws", "linux", "terraform", "ci/cd"],
    "security": ["network security", "linux", "python", "wireshark", "siem", "incident response"],
};

const POPULAR_SKILLS = [
    "python", "sql", "javascript", "react", "machine learning", "docker", 
    "kubernetes", "aws", "pandas", "html", "css", "git", "scikit-learn", "linux"
];

const state = {
    userSkills: new Set(),
    savedJobs: new Set(JSON.parse(localStorage.getItem("savedJobs") || "[]")),
    filters: null,
    allJobs: [],
    lastResults: [],
    matchChart: null,
    missingChart: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const API_BASE = window.location.protocol === "file:" ? "http://localhost:8000" : "";

/* Toast Notification Manager */
function showToast(message, type = "info", duration = 3000) {
    const container = $("#toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
    if (type === "success") {
        icon = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (type === "warning") {
        icon = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    }

    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function parseApiError(data, fallback = "Request failed") {
    if (!data?.detail) return fallback;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail.map((item) => item.msg || String(item)).join(", ");
    }
    return String(data.detail);
}

function showServerError(message) {
    const banner = $("#server-status");
    if (!banner) return;

    const openedDirectly = window.location.protocol === "file:";
    const helpText = openedDirectly
        ? "Opened index.html directly. Connect backend server to serve recommendations."
        : "Ensure python server.py is active.";

    banner.className = "alert alert-warning";
    banner.innerHTML = `
        <strong>Backend Disconnected.</strong> ${message}
        <br><small>${helpText}</small>
        <br><small>Open: <a href="http://localhost:8000" style="color:#818cf8;">http://localhost:8000</a></small>
        <br><button type="button" class="btn btn-secondary btn-sm" id="retry-connection-btn" style="margin-top:0.75rem;">Retry Connection</button>
    `;
    banner.classList.remove("hidden");
    $("#retry-connection-btn")?.addEventListener("click", retryConnection);
}

async function retryConnection() {
    const btn = $("#retry-connection-btn");
    if (btn) {
        btn.textContent = "Connecting...";
        btn.disabled = true;
    }
    try {
        await loadFilters();
        await loadAllJobs();
        clearServerError();
        updateActiveSkills();
        showToast("Connected to AI Recommendation Backend!", "success");
    } catch (err) {
        showServerError(err.message);
    }
}

function clearServerError() {
    const banner = $("#server-status");
    if (!banner) return;
    banner.className = "alert alert-success hidden";
    banner.textContent = "";
}

async function apiFetch(path, options = {}) {
    const res = await fetch(`${API_BASE}${path}`, options);
    let data = null;
    try {
        data = await res.json();
    } catch {
        data = null;
    }
    if (!res.ok) {
        throw new Error(parseApiError(data, `Server error (${res.status})`));
    }
    return data;
}

async function init() {
    bindEvents();
    renderSavedJobs();
    renderQuickSkillsCloud();

    if (window.location.protocol === "file:") {
        showServerError("You opened the HTML file directly. Please access via backend server.");
    }

    try {
        await loadFilters();
        await loadAllJobs();
        clearServerError();
    } catch (err) {
        showServerError(err.message);
    }

    updateActiveSkills();
}

async function loadFilters() {
    state.filters = await apiFetch("/api/filters");

    populateSelect("#location-filter", state.filters.locations);
    populateSelect("#category-filter", state.filters.categories);
    populateSelect("#exp-filter", state.filters.experience_levels);

    const skillsSelect = $("#skills-select");
    skillsSelect.innerHTML = "";
    state.filters.skills.forEach((skill) => {
        const opt = document.createElement("option");
        opt.value = skill;
        opt.textContent = skill;
        skillsSelect.appendChild(opt);
    });

    renderQuickSkillsCloud();
}

async function loadAllJobs() {
    state.allJobs = await apiFetch("/api/jobs");
    renderDatasetTable(state.allJobs);
}

function populateSelect(selector, options) {
    const el = $(selector);
    el.innerHTML = "";
    options.forEach((opt) => {
        const option = document.createElement("option");
        option.value = opt;
        option.textContent = opt;
        el.appendChild(option);
    });
}

function renderQuickSkillsCloud() {
    const container = $("#quick-skills-cloud");
    if (!container) return;
    container.innerHTML = "";

    const skillList = state.filters?.skills?.slice(0, 16) || POPULAR_SKILLS;

    skillList.forEach((skill) => {
        const isSelected = state.userSkills.has(skill.toLowerCase());
        const pill = document.createElement("span");
        pill.className = `skill-cloud-pill ${isSelected ? "active" : ""}`;
        pill.textContent = skill;
        pill.addEventListener("click", () => toggleSkill(skill));
        container.appendChild(pill);
    });
}

function toggleSkill(skill) {
    const s = skill.toLowerCase().trim();
    if (state.userSkills.has(s)) {
        state.userSkills.delete(s);
        showToast(`Removed skill: ${skill}`, "info");
    } else {
        state.userSkills.add(s);
        showToast(`Added skill: ${skill}`, "success");
    }
    syncSelectFromSkills();
    updateActiveSkills();
}

function bindEvents() {
    // Mode radio toggle
    $$('input[name="input-mode"]').forEach((radio) => {
        radio.addEventListener("change", () => {
            const isPdf = radio.value === "pdf" && radio.checked;
            $("#pdf-section").classList.toggle("hidden", !isPdf);
            $("#manual-section").classList.toggle("hidden", isPdf);
        });
    });

    // File Drop Zone
    const dropzone = $("#pdf-dropzone");
    const fileInput = $("#pdf-upload");

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handlePdfUpload({ target: fileInput });
        }
    });

    fileInput.addEventListener("change", handlePdfUpload);
    $("#skills-select").addEventListener("change", syncSkillsFromSelect);

    // Custom skills tag input (press Enter or Comma to add)
    const customInput = $("#custom-skills");
    customInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            const val = customInput.value.trim().toLowerCase();
            if (val) {
                val.split(",").forEach((s) => {
                    const clean = s.trim();
                    if (clean) state.userSkills.add(clean);
                });
                customInput.value = "";
                syncSelectFromSkills();
                updateActiveSkills();
                showToast("Added custom skills!", "success");
            }
        }
    });

    $("#top-n").addEventListener("input", (e) => { $("#top-n-value").textContent = e.target.value; });
    $("#min-score").addEventListener("input", (e) => { $("#min-score-value").textContent = `${e.target.value}%`; });
    
    $("#generate-btn").addEventListener("click", generateRecommendations);
    $("#demo-profile-btn").addEventListener("click", loadDemoProfile);
    $("#preset-select").addEventListener("change", applyPreset);
    $("#reset-skills-btn").addEventListener("click", resetSkills);
    $("#clear-saved-btn").addEventListener("click", clearSavedJobs);
    $("#export-btn").addEventListener("click", exportResults);
    $("#table-search").addEventListener("input", filterDatasetTable);

    // Tab buttons
    $$(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });

    // Modal Close
    $("#modal-close-btn")?.addEventListener("click", closeModal);
    $("#job-modal")?.addEventListener("click", (e) => {
        if (e.target.id === "job-modal") closeModal();
    });
}

async function handlePdfUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const statusEl = $("#pdf-status");
    statusEl.innerHTML = '<div class="alert alert-info">Extracting skills from resume PDF...</div>';

    const formData = new FormData();
    formData.append("file", file);

    try {
        const data = await apiFetch("/api/upload-resume", { method: "POST", body: formData });

        data.skills.forEach((s) => state.userSkills.add(s.toLowerCase()));
        syncSelectFromSkills();
        updateActiveSkills();
        statusEl.innerHTML = `<div class="alert alert-success">Successfully extracted <strong>${data.count}</strong> skills!</div>`;
        showToast(`Extracted ${data.count} skills from PDF!`, "success");
    } catch (err) {
        statusEl.innerHTML = `<div class="alert alert-warning">${err.message}</div>`;
        showToast(err.message, "warning");
    }
}

function syncSkillsFromSelect() {
    const selected = Array.from($("#skills-select").selectedOptions).map((o) => o.value.toLowerCase());
    selected.forEach((s) => state.userSkills.add(s));
}

function syncSelectFromSkills() {
    const select = $("#skills-select");
    Array.from(select.options).forEach((opt) => {
        opt.selected = state.userSkills.has(opt.value.toLowerCase());
    });
}

function updateActiveSkills() {
    const list = Array.from(state.userSkills).sort();
    $("#skill-count").textContent = list.length;
    
    const container = $("#active-skills-list");
    container.innerHTML = "";

    if (!list.length) {
        container.innerHTML = '<span class="skill-chip-empty">No skills selected yet</span>';
    } else {
        list.forEach((skill) => {
            const chip = document.createElement("span");
            chip.className = "skill-chip";
            chip.innerHTML = `
                <span>${skill}</span>
                <span class="skill-chip-remove" data-skill="${skill}">&times;</span>
            `;
            chip.querySelector(".skill-chip-remove").addEventListener("click", () => {
                state.userSkills.delete(skill);
                syncSelectFromSkills();
                updateActiveSkills();
                showToast(`Removed skill: ${skill}`, "info");
            });
            container.appendChild(chip);
        });
    }

    renderQuickSkillsCloud();
}

function applyPreset() {
    const key = $("#preset-select").value;
    if (!key || !PRESETS[key]) return;
    state.userSkills = new Set(PRESETS[key]);
    syncSelectFromSkills();
    updateActiveSkills();
    showToast(`Loaded ${key} preset profile!`, "success");
}

function loadDemoProfile() {
    $("#preset-select").value = "data-science";
    applyPreset();
    $("#custom-skills").value = "";
}

function resetSkills() {
    state.userSkills.clear();
    $("#skills-select").selectedIndex = -1;
    $("#custom-skills").value = "";
    $("#preset-select").value = "";
    $("#pdf-upload").value = "";
    $("#pdf-status").innerHTML = "";
    updateActiveSkills();
    showToast("Skill profile reset", "info");
}

function persistSavedJobs() {
    localStorage.setItem("savedJobs", JSON.stringify([...state.savedJobs]));
}

function renderSavedJobs() {
    const list = $("#saved-list");
    list.innerHTML = "";
    $("#saved-count").textContent = state.savedJobs.size;

    if (!state.savedJobs.size) {
        list.innerHTML = '<li class="saved-empty">No saved jobs yet</li>';
        return;
    }

    state.savedJobs.forEach((jobId) => {
        const job = state.allJobs.find((j) => j.job_id === jobId);
        if (job) {
            const li = document.createElement("li");
            li.innerHTML = `
                <span>${job.job_title}</span>
                <span style="cursor:pointer;color:var(--danger);" class="remove-saved" data-id="${jobId}">&times;</span>
            `;
            li.querySelector(".remove-saved").addEventListener("click", () => toggleSaveJob(jobId));
            list.appendChild(li);
        }
    });
}

function toggleSaveJob(jobId) {
    if (state.savedJobs.has(jobId)) {
        state.savedJobs.delete(jobId);
        showToast("Removed job from bookmarks", "info");
    } else {
        state.savedJobs.add(jobId);
        showToast("Saved job to bookmarks!", "success");
    }
    persistSavedJobs();
    renderSavedJobs();
    if (state.lastResults.length) renderJobCards(state.lastResults);
}

function clearSavedJobs() {
    state.savedJobs.clear();
    persistSavedJobs();
    renderSavedJobs();
    if (state.lastResults.length) renderJobCards(state.lastResults);
    showToast("Cleared saved jobs", "info");
}

async function generateRecommendations() {
    updateActiveSkills();
    let skills = Array.from(state.userSkills);

    if (!skills.length) {
        loadDemoProfile();
        skills = Array.from(state.userSkills);
    }

    const btn = $("#generate-btn");
    btn.classList.add("loading");
    btn.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg> Generating...`;

    try {
        let data = await apiFetch("/api/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_skills: skills,
                top_n: parseInt($("#top-n").value, 10),
                category_filter: $("#category-filter").value || "All Categories",
                exp_filter: $("#exp-filter").value || "All Experience Levels",
                location_filter: $("#location-filter").value || "All Locations",
                min_score: parseFloat($("#min-score").value),
            }),
        });

        if (!data.results.length) {
            data = await apiFetch("/api/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_skills: skills,
                    top_n: parseInt($("#top-n").value, 10),
                    category_filter: "All Categories",
                    exp_filter: "All Experience Levels",
                    location_filter: "All Locations",
                    min_score: 0,
                }),
            });
            showToast("Filters adjusted to display nearest matches", "warning");
        }

        state.lastResults = data.results;
        displayResults(data.results);
        $("#export-btn").classList.remove("hidden");
        clearServerError();
        showToast(`Generated ${data.results.length} ranked job recommendations!`, "success");
    } catch (err) {
        showServerError(err.message);
        showToast(err.message, "warning");
    } finally {
        btn.classList.remove("loading");
        btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg><span class="btn-text">Generate Recommendations</span>`;
    }
}

function asSkillList(value) {
    if (Array.isArray(value)) return value;
    if (typeof value === "string" && value.trim()) return value.split(/\s+/);
    return [];
}

function displayResults(results) {
    $("#results-section").classList.remove("hidden");
    $("#results-section").scrollIntoView({ behavior: "smooth", block: "start" });

    if (!results.length) {
        $("#no-results").classList.remove("hidden");
        $("#results-content").classList.add("hidden");
        return;
    }

    $("#no-results").classList.add("hidden");
    $("#results-content").classList.remove("hidden");

    $("#metric-top-job").textContent = results[0].job_title;
    $("#metric-top-score").textContent = results[0].match_percentage + "%";
    $("#metric-total").textContent = results.length;

    renderJobCards(results);
    try {
        renderCharts(results);
    } catch (err) {
        console.warn("Charts error:", err);
    }
}

function scoreClass(score) {
    if (score >= 65) return "score-high";
    if (score >= 40) return "score-med";
    return "score-low";
}

function renderJobCards(results) {
    const container = $("#job-cards");
    container.innerHTML = "";

    results.forEach((job, idx) => {
        const isSaved = state.savedJobs.has(job.job_id);
        const matchedSkills = asSkillList(job.matched_skills);
        const missingSkills = asSkillList(job.missing_skills);

        const matchedHtml = matchedSkills.length
            ? matchedSkills.map((s) => `<span class="skill-matched-pill">&#10003; ${s}</span>`).join("")
            : '<span style="color:var(--text-muted);font-size:0.85rem;">No direct skill match.</span>';

        const missingHtml = missingSkills.length
            ? missingSkills.map((s) => `<span class="skill-missing-pill">+ ${s}</span>`).join("")
            : '<span class="skill-matched-pill">100% Skills Matched!</span>';

        const card = document.createElement("div");
        card.className = "job-result-card";
        card.innerHTML = `
            <div class="job-header">
                <div class="job-title">#${idx + 1} ${job.job_title}</div>
                <span class="score-pill ${scoreClass(job.match_percentage)}">
                    ${job.match_percentage}% Match
                </span>
            </div>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: 0%;" data-width="${Math.min(100, Math.max(5, job.match_percentage))}%"></div>
            </div>
            <div>
                <span class="meta-tag">📍 ${job.location}</span>
                <span class="meta-tag">💼 ${job.category}</span>
                <span class="meta-tag">🎯 ${job.experience_level}</span>
            </div>
            <div class="skills-row">
                <div><h5>Matched Skills</h5>${matchedHtml}</div>
                <div><h5>Missing Skill Gap</h5>${missingHtml}</div>
            </div>
            <div class="job-actions">
                <button class="btn btn-sm ${isSaved ? "saved" : ""}" data-job-id="${job.job_id}">
                    ${isSaved ? "&#9733; Bookmarked" : "&#9734; Save Job"}
                </button>
                <button class="btn btn-sm btn-secondary open-modal" data-job-id="${job.job_id}">
                    View Full Details
                </button>
                <button class="btn btn-sm toggle-desc" data-job-id="${job.job_id}">Quick Description</button>
            </div>
            <div class="job-description" id="desc-${job.job_id}">
                <p>${job.job_description}</p>
                <p style="margin-top:0.5rem;"><strong>Required Skills:</strong> ${job.required_skills}</p>
            </div>
        `;

        // Action Handlers
        card.querySelector(".btn-sm:not(.toggle-desc):not(.open-modal)").addEventListener("click", () => toggleSaveJob(job.job_id));
        card.querySelector(".open-modal").addEventListener("click", () => openJobModal(job));
        card.querySelector(".toggle-desc").addEventListener("click", (e) => {
            const desc = document.getElementById(`desc-${job.job_id}`);
            desc.classList.toggle("open");
            e.target.textContent = desc.classList.contains("open") ? "Hide Description" : "Quick Description";
        });

        container.appendChild(card);
    });

    // Trigger score bar animation after render
    setTimeout(() => {
        $$(".score-bar-fill").forEach((bar) => {
            bar.style.width = bar.dataset.width;
        });
    }, 100);
}

function openJobModal(job) {
    const modal = $("#job-modal");
    if (!modal) return;

    const matchedSkills = asSkillList(job.matched_skills);
    const missingSkills = asSkillList(job.missing_skills);

    $("#modal-title").textContent = job.job_title;
    $("#modal-body").innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="meta-tag">📍 ${job.location}</span>
                <span class="meta-tag">💼 ${job.category}</span>
                <span class="meta-tag">🎯 ${job.experience_level}</span>
            </div>
            <span class="score-pill ${scoreClass(job.match_percentage)}" style="font-size:1rem;">
                ${job.match_percentage}% Similarity Score
            </span>
        </div>
        <div class="score-bar-bg" style="height:10px;">
            <div class="score-bar-fill" style="width: ${job.match_percentage}%;"></div>
        </div>
        <div style="background:rgba(15,23,42,0.8); border:1px solid var(--border-color); padding:1rem; border-radius:8px;">
            <h5 style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; margin-bottom:0.4rem;">Job Description</h5>
            <p style="font-size:0.92rem; line-height:1.6;">${job.job_description}</p>
        </div>
        <div class="skills-row">
            <div>
                <h5>Matched Skills Matrix</h5>
                ${matchedSkills.length ? matchedSkills.map((s) => `<span class="skill-matched-pill">&#10003; ${s}</span>`).join("") : 'None'}
            </div>
            <div>
                <h5>Missing Skill Gap</h5>
                ${missingSkills.length ? missingSkills.map((s) => `<span class="skill-missing-pill">+ ${s}</span>`).join("") : '<span class="skill-matched-pill">100% Matched!</span>'}
            </div>
        </div>
        <div>
            <h5 style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; margin-bottom:0.4rem;">All Required Skills</h5>
            <p style="font-size:0.88rem; color:var(--text-secondary);">${job.required_skills}</p>
        </div>
    `;

    modal.classList.remove("hidden");
}

function closeModal() {
    $("#job-modal")?.classList.add("hidden");
}

function renderCharts(results) {
    if (state.matchChart) state.matchChart.destroy();
    if (state.missingChart) state.missingChart.destroy();

    const labels = results.map((r) => r.job_title);
    const scores = results.map((r) => r.match_percentage);

    state.matchChart = new Chart($("#match-chart"), {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Match Score (%)",
                data: scores,
                backgroundColor: "#6366f1",
                borderRadius: 6,
            }],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { max: 100, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
                y: { grid: { display: false }, ticks: { color: "#f8fafc" } },
            },
        },
    });

    const missingCounts = {};
    results.forEach((r) => {
        asSkillList(r.missing_skills).forEach((s) => {
            missingCounts[s] = (missingCounts[s] || 0) + 1;
        });
    });

    const sorted = Object.entries(missingCounts).sort((a, b) => b[1] - a[1]).slice(0, 8);

    state.missingChart = new Chart($("#missing-chart"), {
        type: "bar",
        data: {
            labels: sorted.map(([s]) => s),
            datasets: [{
                label: "Occurrence Count",
                data: sorted.map(([, c]) => c),
                backgroundColor: "#f59e0b",
                borderRadius: 6,
            }],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8", stepSize: 1 } },
                y: { grid: { display: false }, ticks: { color: "#f8fafc" } },
            },
        },
    });
}

function renderDatasetTable(jobs) {
    const tbody = $("#jobs-table tbody");
    tbody.innerHTML = "";
    jobs.forEach((job) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${job.job_id}</td>
            <td style="font-weight:600;">${job.job_title}</td>
            <td><span class="meta-tag">${job.category}</span></td>
            <td>${job.experience_level}</td>
            <td>${job.location}</td>
            <td style="font-size:0.82rem; color:var(--text-secondary);">${job.required_skills}</td>
        `;
        tbody.appendChild(tr);
    });
}

function filterDatasetTable() {
    const query = $("#table-search").value.toLowerCase();
    const filtered = state.allJobs.filter((j) =>
        Object.values(j).some((v) => String(v).toLowerCase().includes(query))
    );
    renderDatasetTable(filtered);
}

function switchTab(tabId) {
    $$(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tabId));
    $$(".tab-panel").forEach((p) => p.classList.remove("active"));
    $(`#tab-${tabId}`).classList.add("active");
}

function exportResults() {
    if (!state.lastResults.length) return;
    const blob = new Blob([JSON.stringify(state.lastResults, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `career_ai_recommendations_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Downloaded recommendations report!", "success");
}

document.addEventListener("DOMContentLoaded", init);
