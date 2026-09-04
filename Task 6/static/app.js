/**
 * Frontend logic for Internee.pk Intern AI Chatbot
 */

let allFaqs = [];
let activeCategoryFilter = "All";

document.addEventListener("DOMContentLoaded", () => {
  loadSuggestions();
  loadFaqs();
  loadTickets();
  loadAnalytics();
});

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll(".nav-item").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-view").forEach(view => view.classList.remove("active"));

  const targetBtn = document.getElementById(`tab-${tabId}-btn`);
  const targetView = document.getElementById(`view-${tabId}`);

  if (targetBtn && targetView) {
    targetBtn.classList.add("active");
    targetView.classList.add("active");
  }

  // Update header title
  const titles = {
    chat: { title: "Intern Query & Support AI", subtitle: "Instant 24/7 intelligent answers for tasks, portal, submissions & certificates" },
    faqs: { title: "Knowledge Base & Guidelines", subtitle: "Curated repository of official internship policies and guidelines" },
    tickets: { title: "Support Ticket Desk", subtitle: "Manage escalated intern issues and track resolution status" },
    analytics: { title: "Coordinator AI Intelligence Hub", subtitle: "Performance metrics, live query activity, and resolution analytics" }
  };

  if (titles[tabId]) {
    document.getElementById("page-title").innerText = titles[tabId].title;
    document.getElementById("page-subtitle").innerText = titles[tabId].subtitle;
  }

  if (tabId === "tickets") loadTickets();
  if (tabId === "analytics") loadAnalytics();
}

// 1. CHAT HANDLING
async function handleSendMessage(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("query-input");
  const query = input.value.trim();
  if (!query) return;

  // Append user message
  appendUserMessage(query);
  input.value = "";

  // Show typing indicator
  const typingId = showTypingIndicator();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, intern_name: "Muhammad Hamza" })
    });

    const data = await res.json();
    removeTypingIndicator(typingId);

    appendBotMessage(data);
  } catch (err) {
    removeTypingIndicator(typingId);
    appendBotErrorMessage("Sorry, our NLP server encountered an issue connecting. Please try again.");
  }
}

function sendPresetQuery(text) {
  const input = document.getElementById("query-input");
  input.value = text;
  handleSendMessage();
}

function appendUserMessage(text) {
  const container = document.getElementById("chat-messages");
  const msgRow = document.createElement("div");
  msgRow.className = "message-row user";
  msgRow.innerHTML = `
    <div class="user-avatar">👨‍💻</div>
    <div class="message-bubble">
      <div class="bubble-content">
        <p>${escapeHtml(text)}</p>
      </div>
    </div>
  `;
  container.appendChild(msgRow);
  container.scrollTop = container.scrollHeight;
}

function appendBotMessage(data) {
  const container = document.getElementById("chat-messages");
  const msgRow = document.createElement("div");
  msgRow.className = "message-row bot";

  let confidenceClass = "confidence-pill";
  let confidenceLabel = `Confidence: ${(data.confidence * 100).toFixed(0)}%`;
  if (data.confidence < 0.25) {
    confidenceClass += " low";
  } else if (data.confidence < 0.45) {
    confidenceClass += " medium";
  }

  // Format links if any
  let linksHtml = "";
  if (data.links && data.links.length > 0) {
    linksHtml = `<div style="margin-top: 8px;"><strong>Helpful Links:</strong> ${data.links.map(l => `<a href="${l}" target="_blank" rel="noopener noreferrer">${l}</a>`).join(", ")}</div>`;
  }

  // Format escalation banner if needed
  let escalationHtml = "";
  if (data.needs_ticket) {
    escalationHtml = `
      <div class="escalate-banner">
        <span class="escalate-text">Low confidence match. Would you like a mentor to review this?</span>
        <button class="btn btn-primary" style="padding: 4px 10px; font-size: 11px;" onclick="openTicketModalWithQuery('${escapeAttr(data.query)}', '${escapeAttr(data.category)}')">
          Escalate as Ticket
        </button>
      </div>
    `;
  }

  // Format suggested follow-ups
  let followUpsHtml = "";
  if (data.suggested_questions && data.suggested_questions.length > 0) {
    followUpsHtml = `
      <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px;">
        <span style="font-size: 11px; color: var(--text-muted); width: 100%;">Related questions:</span>
        ${data.suggested_questions.map(q => `
          <button class="chip-btn" style="padding: 3px 10px; font-size: 11px;" onclick="sendPresetQuery('${escapeAttr(q)}')">${escapeHtml(q)}</button>
        `).join("")}
      </div>
    `;
  }

  // Markdown parsing for bold and bullet points
  let formattedAnswer = parseSimpleMarkdown(data.answer);

  msgRow.innerHTML = `
    <div class="bot-avatar">🤖</div>
    <div class="message-bubble">
      <div class="bubble-header">
        <span class="author">Internee.pk Bot</span>
        <span class="badge ${confidenceClass}">${confidenceLabel}</span>
      </div>
      <div class="bubble-content">
        ${formattedAnswer}
        ${linksHtml}
        ${escalationHtml}
        ${followUpsHtml}
      </div>
      <div class="bubble-footer">
        <span class="meta-source">Category: ${data.category || 'General'} • Source: ${data.source}</span>
        <div class="action-buttons">
          <button class="mini-btn" onclick="copyResponse(this)" title="Copy Answer">📋 Copy</button>
          <button class="mini-btn" onclick="rateHelpful(this, true)" title="Helpful">👍</button>
          <button class="mini-btn" onclick="rateHelpful(this, false)" title="Unhelpful">👎</button>
        </div>
      </div>
    </div>
  `;

  container.appendChild(msgRow);
  container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
  const container = document.getElementById("chat-messages");
  const id = "typing-" + Date.now();
  const msgRow = document.createElement("div");
  msgRow.className = "message-row bot";
  msgRow.id = id;
  msgRow.innerHTML = `
    <div class="bot-avatar">🤖</div>
    <div class="message-bubble" style="padding: 10px 16px;">
      <span style="font-size: 13px; color: var(--text-muted); font-style: italic;">Thinking & checking knowledge base...</span>
    </div>
  `;
  container.appendChild(msgRow);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendBotErrorMessage(msg) {
  const container = document.getElementById("chat-messages");
  const msgRow = document.createElement("div");
  msgRow.className = "message-row bot";
  msgRow.innerHTML = `
    <div class="bot-avatar">🤖</div>
    <div class="message-bubble">
      <div class="bubble-content" style="color: var(--accent-red);">
        <p>${msg}</p>
      </div>
    </div>
  `;
  container.appendChild(msgRow);
  container.scrollTop = container.scrollHeight;
}

// 2. SUGGESTIONS
async function loadSuggestions() {
  try {
    const res = await fetch("/api/suggestions");
    const data = await res.json();
    const container = document.getElementById("chips-container");
    container.innerHTML = "";
    data.suggestions.forEach(item => {
      const btn = document.createElement("button");
      btn.className = "chip-btn";
      btn.innerText = item;
      btn.onclick = () => sendPresetQuery(item);
      container.appendChild(btn);
    });
  } catch (e) {
    console.error("Failed to load suggestions", e);
  }
}

// 3. FAQS KNOWLEDGE BASE
async function loadFaqs() {
  try {
    const res = await fetch("/api/faqs");
    const data = await res.json();
    allFaqs = data.faqs;
    renderFaqCategoryFilters();
    renderFaqCards();
  } catch (e) {
    console.error("Failed to load faqs", e);
  }
}

function renderFaqCategoryFilters() {
  const categories = ["All", ...new Set(allFaqs.map(f => f.category))];
  const container = document.getElementById("faq-category-filters");
  container.innerHTML = "";

  categories.forEach(cat => {
    const pill = document.createElement("button");
    pill.className = `filter-pill ${cat === activeCategoryFilter ? 'active' : ''}`;
    pill.innerText = cat;
    pill.onclick = () => {
      activeCategoryFilter = cat;
      document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      renderFaqCards();
    };
    container.appendChild(pill);
  });
}

function renderFaqCards() {
  const container = document.getElementById("faq-cards-grid");
  const searchTerm = (document.getElementById("faq-search")?.value || "").toLowerCase();

  const filtered = allFaqs.filter(faq => {
    const matchesCat = activeCategoryFilter === "All" || faq.category === activeCategoryFilter;
    const matchesSearch = faq.question.toLowerCase().includes(searchTerm) || 
                          faq.answer.toLowerCase().includes(searchTerm);
    return matchesCat && matchesSearch;
  });

  container.innerHTML = filtered.map(faq => `
    <div class="faq-card">
      <span class="faq-cat-badge">${faq.category}</span>
      <h4>${escapeHtml(faq.question)}</h4>
      <p>${parseSimpleMarkdown(faq.answer)}</p>
      <div style="margin-top: auto; padding-top: 8px;">
        <button class="mini-btn" style="color: var(--accent-teal);" onclick="sendPresetQuery('${escapeAttr(faq.question)}')">Ask AI about this ↗</button>
      </div>
    </div>
  `).join("");
}

function filterFAQs() {
  renderFaqCards();
}

// 4. TICKETS
async function loadTickets() {
  try {
    const res = await fetch("/api/tickets");
    const data = await res.json();
    const tbody = document.getElementById("tickets-table-body");

    let openCount = 0;
    let resCount = 0;

    tbody.innerHTML = data.tickets.map(t => {
      if (t.status === "Open") openCount++;
      if (t.status === "Resolved") resCount++;

      const pClass = (t.priority || "Medium").toLowerCase();
      const sClass = (t.status || "Open").toLowerCase().replace(" ", "-");

      return `
        <tr>
          <td><strong style="font-family: 'JetBrains Mono', monospace; font-size: 12px;">${t.ticket_id}</strong></td>
          <td>${escapeHtml(t.category)}</td>
          <td>
            <div style="font-weight: 500;">${escapeHtml(t.query)}</div>
            ${t.notes ? `<div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">↳ ${escapeHtml(t.notes)}</div>` : ''}
          </td>
          <td><span class="priority-badge ${pClass}">${t.priority}</span></td>
          <td><span class="status-badge ${sClass}">${t.status}</span></td>
          <td>
            ${t.status !== 'Resolved' ? `
              <button class="mini-btn" style="color: var(--accent-green);" onclick="resolveTicket('${t.ticket_id}')">Mark Resolved</button>
            ` : `<span style="font-size: 11px; color: var(--text-muted);">Completed</span>`}
          </td>
        </tr>
      `;
    }).join("");

    document.getElementById("stat-total-tck").innerText = data.tickets.length;
    document.getElementById("stat-open-tck").innerText = openCount;
    document.getElementById("stat-res-tck").innerText = resCount;
    document.getElementById("active-ticket-count").innerText = openCount;
  } catch (e) {
    console.error("Failed to load tickets", e);
  }
}

async function resolveTicket(ticketId) {
  try {
    await fetch("/api/tickets/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticket_id: ticketId, status: "Resolved", notes: "Resolved by coordinator." })
    });
    loadTickets();
  } catch (e) {
    alert("Could not update ticket");
  }
}

// 5. TICKET MODAL
function openTicketModal() {
  document.getElementById("ticket-modal").classList.add("active");
}

function openTicketModalWithQuery(query, category) {
  document.getElementById("modal-query").value = query || "";
  if (category) {
    const sel = document.getElementById("modal-category");
    for (let opt of sel.options) {
      if (opt.value === category) {
        sel.value = category;
        break;
      }
    }
  }
  openTicketModal();
}

function closeTicketModal() {
  document.getElementById("ticket-modal").classList.remove("active");
}

async function handleTicketSubmit(e) {
  e.preventDefault();
  const name = document.getElementById("modal-intern-name").value;
  const email = document.getElementById("modal-intern-email").value;
  const category = document.getElementById("modal-category").value;
  const priority = document.getElementById("modal-priority").value;
  const query = document.getElementById("modal-query").value;

  try {
    const res = await fetch("/api/tickets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        category: category,
        intern_name: name,
        intern_email: email,
        priority: priority
      })
    });
    const data = await res.json();
    closeTicketModal();
    alert(`Success! Ticket #${data.ticket.ticket_id} submitted.`);
    loadTickets();
  } catch (err) {
    alert("Error submitting ticket.");
  }
}

// 6. ANALYTICS
async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    const data = await res.json();

    document.getElementById("metric-auto-rate").innerText = data.queries_stats.automated_resolution_rate;
    document.getElementById("metric-queries-count").innerText = data.queries_stats.total_queries_logged;

    // Activity feed
    const feed = document.getElementById("live-query-feed");
    const recents = data.queries_stats.recent_queries;
    if (recents && recents.length > 0) {
      feed.innerHTML = recents.map(q => `
        <div class="feed-item">
          <div>
            <div style="font-weight: 600;">${escapeHtml(q.query)}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${q.category} • Confidence ${(q.confidence * 100).toFixed(0)}%</div>
          </div>
          <span class="badge ${q.needs_ticket ? 'confidence-pill low' : 'confidence-pill'}">${q.needs_ticket ? 'Escalated' : 'Resolved'}</span>
        </div>
      `).join("");
    }

    // Topic bars
    const topicBars = document.getElementById("topic-bars");
    const catStats = data.tickets_stats.by_category || {};
    const maxVal = Math.max(...Object.values(catStats), 1);

    topicBars.innerHTML = Object.entries(catStats).map(([cat, count]) => {
      const pct = (count / maxVal) * 100;
      return `
        <div class="topic-bar-row">
          <div class="topic-bar-header">
            <span>${cat}</span>
            <span><strong>${count}</strong> tickets</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }).join("");
  } catch (e) {
    console.error("Failed to load analytics", e);
  }
}

// Helpers
function parseSimpleMarkdown(md) {
  if (!md) return "";
  let html = escapeHtml(md);
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/\n\n/g, "</p><p>");
  html = html.replace(/\n/g, "<br>");
  return `<p>${html}</p>`;
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>"']/g, m => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[m]);
}

function escapeAttr(str) {
  if (!str) return "";
  return str.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

function copyResponse(btn) {
  const text = btn.closest(".message-bubble").querySelector(".bubble-content").innerText;
  navigator.clipboard.writeText(text);
  btn.innerText = "✓ Copied";
  setTimeout(() => btn.innerText = "📋 Copy", 2000);
}

function rateHelpful(btn, isPositive) {
  btn.style.color = isPositive ? "var(--accent-green)" : "var(--accent-red)";
}
