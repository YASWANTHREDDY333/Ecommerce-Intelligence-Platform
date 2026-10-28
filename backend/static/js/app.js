/* ==========================================================================
   OmniPulse E-Commerce Intelligence Platform - Controller Logic
   ========================================================================== */

const API_BASE = "";
const charts = {};

// Toast Notification Utility
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i data-lucide="${type === 'success' ? 'check-circle' : 'info'}" style="width:18px;height:18px;color:${type === 'success' ? '#10b981' : '#6366f1'}"></i>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  lucide.createIcons();
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Chart.js Default Dark Theme Stying
Chart.defaults.color = "#94a3b8";
Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = "rgba(15, 23, 42, 0.95)";
Chart.defaults.plugins.tooltip.borderColor = "rgba(255, 255, 255, 0.1)";
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.legend.labels.usePointStyle = true;

// Tab Switching
document.querySelectorAll(".nav-tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach((p) => p.classList.remove("active"));

    btn.classList.add("active");
    const target = btn.getAttribute("data-tab");
    const pane = document.getElementById(target);
    if (pane) {
      pane.classList.add("active");
      // Trigger resize for Chart.js and Leaflet
      window.dispatchEvent(new Event("resize"));
      if (target === "tab-map") {
        loadGeospatialMap();
        setTimeout(() => { if (leafletMap) leafletMap.invalidateSize(); }, 250);
      }
      if (target === "tab-ai") {
        updateSimulation();
      }
    }
  });
});

// Format Currency
function formatCurrency(val) {
  if (val >= 1000000) return `$${(val / 1000000).toFixed(2)}M`;
  if (val >= 1000) return `$${(val / 1000).toFixed(1)}k`;
  return `$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Format Numbers
function formatNumber(val) {
  return Number(val).toLocaleString();
}

// ==========================================================================
// 1. Executive Overview Module
// ==========================================================================

async function loadOverview() {
  try {
    const res = await fetch(`${API_BASE}/api/overview`);
    const data = await res.json();

    document.getElementById("kpi-revenue").innerText = formatCurrency(data.total_revenue);
    document.getElementById("kpi-orders").innerText = formatNumber(data.total_orders);
    document.getElementById("kpi-customers").innerText = formatNumber(data.total_customers);
    document.getElementById("kpi-ontime").innerText = `${data.on_time_rate}%`;

    document.getElementById("kpi-aov").innerText = `$${data.average_order_value}`;
    document.getElementById("kpi-deliv-days").innerText = `${data.avg_delivery_days} days`;
    document.getElementById("kpi-csat").innerText = `${data.avg_review_score} / 5.0`;
    document.getElementById("kpi-alerts").innerText = `${formatNumber(data.critical_alerts_count + data.low_stock_alerts_count)}`;
    document.getElementById("badge-critical-alerts").innerText = `${formatNumber(data.critical_alerts_count)} Critical`;

    loadRevenueChart();
    loadDeliveryDoughnut(data.early_rate, data.on_time_rate, data.late_rate);
  } catch (err) {
    console.error("Failed to load overview KPIs", err);
  }
}

async function loadRevenueChart() {
  try {
    const res = await fetch(`${API_BASE}/api/sales/monthly`);
    const data = await res.json();

    const labels = data.map((d) => d.month);
    const revenues = data.map((d) => d.revenue);
    const orders = data.map((d) => d.orders);

    const ctx = document.getElementById("chart-revenue").getContext("2d");
    if (charts.revenue) charts.revenue.destroy();

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.45)");
    gradient.addColorStop(1, "rgba(99, 102, 241, 0.0)");

    charts.revenue = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Delivered Revenue ($)",
            data: revenues,
            borderColor: "#6366f1",
            backgroundColor: gradient,
            borderWidth: 3,
            fill: true,
            tension: 0.35,
            yAxisID: "y",
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: "#ffffff",
          },
          {
            label: "Delivered Orders",
            data: orders,
            type: "bar",
            backgroundColor: "rgba(6, 182, 212, 0.45)",
            borderColor: "#06b6d4",
            borderWidth: 1,
            borderRadius: 6,
            yAxisID: "y1",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
          y: {
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: {
              callback: (v) => `$${(v / 1000).toFixed(0)}k`,
            },
          },
          y1: {
            position: "right",
            grid: { display: false },
            ticks: { callback: (v) => v.toLocaleString() },
          },
        },
      },
    });
  } catch (err) {
    console.error("Failed to load revenue chart", err);
  }
}

function loadDeliveryDoughnut(early, ontime, late) {
  const ctx = document.getElementById("chart-delivery-sla").getContext("2d");
  if (charts.delivery) charts.delivery.destroy();

  charts.delivery = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Early Delivery", "On-Time", "Late Delivery"],
      datasets: [
        {
          data: [early, ontime, late],
          backgroundColor: ["#10b981", "#06b6d4", "#f43f5e"],
          borderWidth: 2,
          borderColor: "#0f172a",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "74%",
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });
}

// ==========================================================================
// 2. Sales & Categories Module
// ==========================================================================

async function loadSalesTab() {
  try {
    // Categories
    const resCat = await fetch(`${API_BASE}/api/sales/categories?limit=10`);
    const categories = await resCat.json();

    const catCtx = document.getElementById("chart-categories").getContext("2d");
    if (charts.categories) charts.categories.destroy();

    charts.categories = new Chart(catCtx, {
      type: "bar",
      data: {
        labels: categories.map((c) => c.category),
        datasets: [
          {
            label: "Revenue ($)",
            data: categories.map((c) => c.revenue),
            backgroundColor: "rgba(99, 102, 241, 0.75)",
            borderColor: "#818cf8",
            borderWidth: 1,
            borderRadius: 6,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` },
          },
          y: { grid: { display: false } },
        },
      },
    });

    // Payments
    const resPay = await fetch(`${API_BASE}/api/sales/payments`);
    const payments = await resPay.json();

    const payCtx = document.getElementById("chart-payments").getContext("2d");
    if (charts.payments) charts.payments.destroy();

    charts.payments = new Chart(payCtx, {
      type: "doughnut",
      data: {
        labels: payments.map((p) => p.payment_type),
        datasets: [
          {
            data: payments.map((p) => p.total_value),
            backgroundColor: ["#6366f1", "#06b6d4", "#f59e0b", "#10b981", "#8b5cf6"],
            borderWidth: 2,
            borderColor: "#0f172a",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
          legend: { position: "bottom" },
        },
      },
    });

    // Top Products Table
    const resProd = await fetch(`${API_BASE}/api/sales/top-products?limit=10`);
    const products = await resProd.json();
    const prodTable = document.getElementById("tbody-top-products");
    prodTable.innerHTML = products
      .map(
        (p, i) => `
      <tr>
        <td style="font-weight:700; color:var(--accent-indigo)">#${i + 1}</td>
        <td class="font-mono">${p.product_id.substring(0, 10)}...</td>
        <td>${p.category}</td>
        <td style="font-weight:700">${formatCurrency(p.revenue)}</td>
        <td>${formatNumber(p.items_sold)} units</td>
        <td>${p.current_stock}</td>
        <td>
          <span class="badge-pill ${
            p.stock_status === 'HEALTHY'
              ? 'badge-emerald'
              : p.stock_status === 'LOW'
              ? 'badge-amber'
              : 'badge-rose'
          }">${p.stock_status}</span>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load sales data", err);
  }
}

// ==========================================================================
// 3. Customer RFM Intelligence Module
// ==========================================================================

async function loadCustomersTab() {
  try {
    const res = await fetch(`${API_BASE}/api/customers/segments`);
    const segments = await res.json();

    // Segment Doughnut
    const segCtx = document.getElementById("chart-customer-segments").getContext("2d");
    if (charts.segments) charts.segments.destroy();

    charts.segments = new Chart(segCtx, {
      type: "doughnut",
      data: {
        labels: segments.map((s) => s.segment_name),
        datasets: [
          {
            data: segments.map((s) => s.customer_count),
            backgroundColor: ["#10b981", "#f43f5e", "#06b6d4", "#8b5cf6"],
            borderWidth: 2,
            borderColor: "#0f172a",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "70%",
        plugins: { legend: { position: "bottom" } },
      },
    });

    // Segment Total Value Bar Chart
    const valCtx = document.getElementById("chart-segment-value").getContext("2d");
    if (charts.segmentValue) charts.segmentValue.destroy();

    charts.segmentValue = new Chart(valCtx, {
      type: "bar",
      data: {
        labels: segments.map((s) => s.segment_name),
        datasets: [
          {
            label: "Total Segment Revenue ($)",
            data: segments.map((s) => s.total_revenue),
            backgroundColor: ["#10b981", "#f43f5e", "#06b6d4", "#8b5cf6"],
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: { callback: (v) => `$${(v / 1000000).toFixed(1)}M` },
          },
          x: { grid: { display: false } },
        },
      },
    });

    // Customer Segment Table
    const segTbody = document.getElementById("tbody-customer-segments");
    segTbody.innerHTML = segments
      .map(
        (s) => `
      <tr>
        <td style="font-weight:700">${s.segment_name}</td>
        <td>${formatNumber(s.customer_count)} (${s.percentage}%)</td>
        <td>${s.avg_recency} days</td>
        <td>${s.avg_frequency}</td>
        <td>$${s.avg_monetary}</td>
        <td style="font-weight:700; color:#38bdf8">${formatCurrency(s.total_revenue)}</td>
      </tr>
    `
      )
      .join("");

    // State Geography
    const resGeo = await fetch(`${API_BASE}/api/customers/geography`);
    const geoData = await resGeo.json();
    const topStates = geoData.slice(0, 8);

    const geoCtx = document.getElementById("chart-geography").getContext("2d");
    if (charts.geography) charts.geography.destroy();

    charts.geography = new Chart(geoCtx, {
      type: "bar",
      data: {
        labels: topStates.map((s) => s.state),
        datasets: [
          {
            label: "Revenue ($)",
            data: topStates.map((s) => s.total_revenue),
            backgroundColor: "rgba(6, 182, 212, 0.75)",
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` },
          },
          x: { grid: { display: false } },
        },
      },
    });
  } catch (err) {
    console.error("Failed to load customer segment data", err);
  }
}

// ==========================================================================
// 4. Smart Inventory & Stock Alert Center Module
// ==========================================================================

async function loadInventoryTab() {
  try {
    const resSum = await fetch(`${API_BASE}/api/inventory/summary`);
    const summary = await resSum.json();

    document.getElementById("inv-total-skus").innerText = formatNumber(summary.total_skus);
    document.getElementById("inv-critical-count").innerText = formatNumber(summary.critical_count);
    document.getElementById("inv-low-count").innerText = formatNumber(summary.low_stock_count);
    document.getElementById("inv-healthy-count").innerText = formatNumber(summary.healthy_count);

    loadInventoryAlerts();
    loadInventoryItems();
  } catch (err) {
    console.error("Failed to load inventory summary", err);
  }
}

async function loadInventoryAlerts() {
  try {
    const filter = document.getElementById("select-alert-filter").value;
    let url = `${API_BASE}/api/inventory/alerts?limit=15`;
    if (filter === "CRITICAL" || filter === "LOW_STOCK") url += `&alert_type=${filter}`;
    if (filter === "OPEN") url += `&alert_status=OPEN`;

    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById("tbody-inventory-alerts");

    tbody.innerHTML = data.alerts
      .map(
        (a) => `
      <tr>
        <td>
          <span class="badge-pill ${
            a.alert_type === 'CRITICAL' ? 'badge-rose' : 'badge-amber'
          }">${a.alert_type}</span>
        </td>
        <td class="font-mono">${a.product_id.substring(0, 10)}...</td>
        <td>${a.category}</td>
        <td style="font-weight:700; color:${a.alert_type === 'CRITICAL' ? '#fb7185' : '#fbbf24'}">${a.current_stock} units</td>
        <td>${a.reorder_level} units</td>
        <td style="font-weight:700; color:#38bdf8">+${a.recommended_reorder_quantity} units</td>
        <td>
          <span class="badge-pill ${
            a.alert_status === 'OPEN'
              ? 'badge-purple'
              : a.alert_status === 'ACKNOWLEDGED'
              ? 'badge-amber'
              : 'badge-emerald'
          }">${a.alert_status}</span>
        </td>
        <td>
          <button class="btn-table-action" onclick="openRestockModal('${a.product_id}', ${a.recommended_reorder_quantity})">
            <i data-lucide="package-plus" style="width:14px;height:14px"></i> Restock
          </button>
          ${
            a.alert_status === 'OPEN'
              ? `<button class="btn-table-action btn-ack" onclick="acknowledgeAlert(${a.alert_id})">
                   <i data-lucide="check" style="width:14px;height:14px"></i> Ack
                 </button>`
              : ""
          }
        </td>
      </tr>
    `
      )
      .join("");
    lucide.createIcons();
  } catch (err) {
    console.error("Failed to load inventory alerts", err);
  }
}

async function loadInventoryItems() {
  try {
    const search = document.getElementById("input-inv-search").value;
    const status = document.getElementById("select-inv-status").value;

    let url = `${API_BASE}/api/inventory/items?limit=15`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (status) url += `&stock_status=${status}`;

    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById("tbody-inventory-items");

    tbody.innerHTML = data.items
      .map(
        (item) => `
      <tr>
        <td class="font-mono">${item.product_id.substring(0, 12)}...</td>
        <td>${item.category}</td>
        <td style="font-weight:700">${item.current_stock}</td>
        <td>${item.reorder_level}</td>
        <td>${item.safety_stock}</td>
        <td>${item.average_daily_sales} / day</td>
        <td>${item.supplier_lead_time_days} days</td>
        <td>
          <span class="badge-pill ${
            item.stock_status === 'HEALTHY'
              ? 'badge-emerald'
              : item.stock_status === 'LOW'
              ? 'badge-amber'
              : 'badge-rose'
          }">${item.stock_status}</span>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load inventory items", err);
  }
}

// Acknowledge Alert Handler
async function acknowledgeAlert(alertId) {
  try {
    const res = await fetch(`${API_BASE}/api/inventory/alerts/${alertId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ alert_status: "ACKNOWLEDGED" }),
    });
    if (res.ok) {
      showToast(`Alert #${alertId} marked as Acknowledged`, "success");
      loadInventoryAlerts();
    }
  } catch (err) {
    showToast("Failed to acknowledge alert", "info");
  }
}

// Restock Modal Handlers
function openRestockModal(productId, qty) {
  document.getElementById("modal-restock-sku").innerText = productId;
  document.getElementById("modal-restock-qty").value = qty;
  document.getElementById("modal-restock-product-id").value = productId;
  document.getElementById("modal-restock").classList.add("open");
}

function closeRestockModal() {
  document.getElementById("modal-restock").classList.remove("open");
}

async function submitRestock() {
  const productId = document.getElementById("modal-restock-product-id").value;
  const qty = parseInt(document.getElementById("modal-restock-qty").value);

  if (!qty || qty <= 0) {
    showToast("Please enter a valid positive quantity", "info");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/inventory/restock`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: qty }),
    });
    if (res.ok) {
      showToast(`Successfully restocked ${qty} units for SKU ${productId.substring(0, 8)}!`, "success");
      closeRestockModal();
      loadInventoryTab();
      loadOverview();
    }
  } catch (err) {
    showToast("Restock operation failed", "info");
  }
}

// ==========================================================================
// 5. Logistics & Delivery Module
// ==========================================================================

async function loadLogisticsTab() {
  try {
    const res = await fetch(`${API_BASE}/api/logistics/summary`);
    const data = await res.json();

    document.getElementById("log-delivered").innerText = formatNumber(data.total_delivered);
    document.getElementById("log-early").innerText = `${data.early_percentage}%`;
    document.getElementById("log-ontime").innerText = `${data.on_time_percentage}%`;
    document.getElementById("log-late").innerText = `${data.late_percentage}%`;
    document.getElementById("log-avg-days").innerText = `${data.avg_delivery_days} days`;
    document.getElementById("log-avg-delay").innerText = `${data.avg_delay_days} days`;

    // State Shipping Table
    const resState = await fetch(`${API_BASE}/api/logistics/by-state`);
    const states = await resState.json();
    const tbody = document.getElementById("tbody-logistics-states");

    tbody.innerHTML = states
      .map(
        (s) => `
      <tr>
        <td style="font-weight:700">${s.state}</td>
        <td>${formatNumber(s.orders_count)}</td>
        <td>${formatCurrency(s.total_revenue)}</td>
        <td>${s.avg_delivery_days} days</td>
        <td style="font-weight:700; color:${s.late_rate > 10 ? '#fb7185' : '#34d399'}">${s.late_rate.toFixed(1)}%</td>
        <td>
          <span class="badge-pill ${s.late_rate > 10 ? 'badge-rose' : 'badge-emerald'}">
            ${s.late_rate > 10 ? 'Delayed Route' : 'Optimal SLA'}
          </span>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load logistics data", err);
  }
}

// ==========================================================================
// 6. Reviews & Customer CSAT Module
// ==========================================================================

async function loadReviewsTab() {
  try {
    const res = await fetch(`${API_BASE}/api/reviews/summary`);
    const data = await res.json();

    document.getElementById("rev-avg-score").innerText = `${data.average_score} / 5.0`;
    document.getElementById("rev-total-reviews").innerText = formatNumber(data.total_reviews);

    // Score distribution chart
    const distCtx = document.getElementById("chart-review-dist").getContext("2d");
    if (charts.reviewDist) charts.reviewDist.destroy();

    const labels = ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"];
    const counts = [
      data.score_distribution["1"] || 0,
      data.score_distribution["2"] || 0,
      data.score_distribution["3"] || 0,
      data.score_distribution["4"] || 0,
      data.score_distribution["5"] || 0,
    ];

    charts.reviewDist = new Chart(distCtx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Reviews Count",
            data: counts,
            backgroundColor: ["#f43f5e", "#fb923c", "#facc15", "#38bdf8", "#10b981"],
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
          x: { grid: { display: false } },
        },
      },
    });

    // Rating vs Delay
    const delayCtx = document.getElementById("chart-rating-delay").getContext("2d");
    if (charts.ratingDelay) charts.ratingDelay.destroy();

    charts.ratingDelay = new Chart(delayCtx, {
      type: "bar",
      data: {
        labels: data.delivery_delay_vs_rating.map((d) => d.status),
        datasets: [
          {
            label: "Average Review Score (out of 5)",
            data: data.delivery_delay_vs_rating.map((d) => d.avg_rating),
            backgroundColor: ["#10b981", "#06b6d4", "#f43f5e"],
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            min: 0,
            max: 5,
            grid: { color: "rgba(255, 255, 255, 0.05)" },
          },
          x: { grid: { display: false } },
        },
      },
    });
  } catch (err) {
    console.error("Failed to load reviews data", err);
  }
}

// ==========================================================================
// 7. AI Insights Module
// ==========================================================================

async function loadAIInsightsTab() {
  try {
    const res = await fetch(`${API_BASE}/api/ai-insights`);
    const insights = await res.json();

    const container = document.getElementById("ai-insights-container");
    container.innerHTML = insights
      .map(
        (ins) => `
      <div class="glass-card ai-insight-card impact-${ins.impact_level}">
        <div>
          <div class="ai-card-top">
            <span class="ai-card-cat">${ins.category}</span>
            <span class="badge-pill ${
              ins.impact_level === 'CRITICAL'
                ? 'badge-rose'
                : ins.impact_level === 'HIGH'
                ? 'badge-amber'
                : 'badge-emerald'
            }">${ins.impact_level}</span>
          </div>
          <h3 class="ai-card-title">${ins.title}</h3>
          <p class="ai-card-desc">${ins.description}</p>
          <div class="ai-action-box">
            <div class="ai-action-title">Recommended Action</div>
            <div class="ai-action-text">${ins.recommended_action}</div>
          </div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.75rem">
          <span style="font-size:0.8rem; font-weight:700; color:#38bdf8">${ins.metric}</span>
          <button class="btn-ai-action" onclick="showToast('Action logged: ${ins.title}', 'success')">
            <i data-lucide="sparkles" style="width:14px;height:14px"></i> Deploy Recommendation
          </button>
        </div>
      </div>
    `
      )
      .join("");
    lucide.createIcons();
  } catch (err) {
    console.error("Failed to load AI insights", err);
  }
}

// ==========================================================================
// 8. Geospatial Map Module (Leaflet)
// ==========================================================================

let leafletMap = null;
let geoMarkers = [];

async function loadGeospatialMap() {
  const mapElement = document.getElementById("map-container");
  if (!mapElement) return;

  if (!leafletMap) {
    leafletMap = L.map("map-container", {
      zoomControl: true,
      scrollWheelZoom: true,
    }).setView([-14.235, -51.925], 4);

    // 1. Esri Dark Canvas (Base + Reference Labels) - Free, Clean Dark Theme, No API Key Required
    const esriDarkBase = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
      {
        attribution: "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ",
        maxZoom: 18,
        maxNativeZoom: 16,
      }
    );
    const esriDarkRef = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
      {
        maxZoom: 18,
        maxNativeZoom: 16,
      }
    );
    const esriDarkGroup = L.layerGroup([esriDarkBase, esriDarkRef]);

    // 2. OpenStreetMap Standard (with Dark Theme CSS filter)
    const osmLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
      maxNativeZoom: 19,
      className: "osm-dark-tiles",
    });

    // 3. Esri Satellite Imagery with Reference Borders & Places
    const esriSatBase = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      {
        attribution: "Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics",
        maxZoom: 19,
        maxNativeZoom: 18,
      }
    );
    const esriSatRef = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      {
        maxZoom: 19,
        maxNativeZoom: 18,
      }
    );
    const esriSatGroup = L.layerGroup([esriSatBase, esriSatRef]);

    // Add Esri Dark Canvas as default active basemap
    esriDarkGroup.addTo(leafletMap);

    // Base Layer Switcher Control
    const baseLayers = {
      "🌙 Dark Canvas (Esri)": esriDarkGroup,
      "🗺️ OpenStreetMap": osmLayer,
      "🛰️ Satellite": esriSatGroup,
    };
    L.control.layers(baseLayers, null, { position: "topright" }).addTo(leafletMap);
  } else {
    setTimeout(() => {
      if (leafletMap) leafletMap.invalidateSize();
    }, 150);
  }

  try {
    const res = await fetch(`${API_BASE}/api/geography/map-data`);
    const states = await res.json();

    // Clear previous markers
    geoMarkers.forEach((m) => leafletMap.removeLayer(m));
    geoMarkers = [];

    states.forEach((s) => {
      const color =
        s.sla_status === "OPTIMAL"
          ? "#10b981"
          : s.sla_status === "STANDARD"
          ? "#06b6d4"
          : "#f43f5e";

      const radius = Math.max(8, Math.min(26, Math.sqrt(s.orders_count) * 0.18));

      const marker = L.circleMarker([s.lat, s.lng], {
        radius: radius,
        fillColor: color,
        color: "#ffffff",
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.75,
      }).addTo(leafletMap);

      const popupHtml = `
        <div style="min-width:180px;">
          <div class="map-popup-title">${s.state} — State Hub</div>
          <div class="map-popup-row"><span>Delivered Orders:</span> <strong>${formatNumber(s.orders_count)}</strong></div>
          <div class="map-popup-row"><span>Total Revenue:</span> <strong>${formatCurrency(s.total_revenue)}</strong></div>
          <div class="map-popup-row"><span>Avg Transit Days:</span> <strong>${s.avg_delivery_days} days</strong></div>
          <div class="map-popup-row"><span>Late Delivery Rate:</span> <strong style="color:${color}">${s.late_rate.toFixed(1)}%</strong></div>
          <div class="map-popup-row"><span>SLA Status:</span> <span class="badge-pill" style="background:${color}22; color:${color}; font-weight:700">${s.sla_status}</span></div>
        </div>
      `;
      marker.bindPopup(popupHtml);
      geoMarkers.push(marker);
    });
  } catch (err) {
    console.error("Failed to load map data", err);
  }
}

// ==========================================================================
// 9. What-If Scenario Simulator
// ==========================================================================

let simDebounceTimer = null;

async function updateSimulation() {
  const delayDays = parseFloat(document.getElementById("slider-delay").value);
  const churnRate = parseFloat(document.getElementById("slider-churn").value);
  const stockoutRate = parseFloat(document.getElementById("slider-stockout").value);
  const freightDiscount = parseFloat(document.getElementById("slider-freight").value);

  document.getElementById("val-delay-reduction").innerText = `${delayDays.toFixed(1)} days`;
  document.getElementById("val-churn-winback").innerText = `${churnRate.toFixed(0)}%`;
  document.getElementById("val-stockout-prevention").innerText = `${stockoutRate.toFixed(0)}%`;
  document.getElementById("val-freight-subsidy").innerText = `${freightDiscount.toFixed(0)}%`;

  clearTimeout(simDebounceTimer);
  simDebounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/simulator/project`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          delivery_delay_reduction_days: delayDays,
          churn_winback_rate: churnRate,
          stockout_prevention_rate: stockoutRate,
          freight_subsidy_pct: freightDiscount,
        }),
      });
      const data = await res.json();

      document.getElementById("sim-growth-usd").innerText = `+${formatCurrency(data.projected_revenue_growth_usd)}`;
      document.getElementById("sim-growth-pct").innerText = `+${data.projected_revenue_growth_pct}%`;
      document.getElementById("sim-recovered-churn").innerText = `+${formatCurrency(data.recovered_churn_revenue)}`;
      document.getElementById("sim-protected-stockout").innerText = `+${formatCurrency(data.protected_stockout_revenue)}`;
      document.getElementById("sim-csat").innerText = `${data.projected_csat.toFixed(2)}`;
      document.getElementById("sim-csat-delta").innerText = `+${data.csat_delta.toFixed(2)}★`;
    } catch (err) {
      console.error("Simulation request failed", err);
    }
  }, 150);
}

function resetSimulator() {
  document.getElementById("slider-delay").value = 2.0;
  document.getElementById("slider-churn").value = 10;
  document.getElementById("slider-stockout").value = 50;
  document.getElementById("slider-freight").value = 5;
  updateSimulation();
  showToast("Simulator parameters reset to baseline recommendations", "info");
}

// ==========================================================================
// 10. Floating AI Assistant & Chat Drawer
// ==========================================================================

function toggleAIChat() {
  const drawer = document.getElementById("ai-chat-drawer");
  drawer.classList.toggle("open");
  if (drawer.classList.contains("open")) {
    document.getElementById("input-ai-chat").focus();
  }
}

function askAIChat(query) {
  const input = document.getElementById("input-ai-chat");
  input.value = query;
  sendAIChatMessage();
}

async function sendAIChatMessage() {
  const input = document.getElementById("input-ai-chat");
  const query = input.value.trim();
  if (!query) return;

  const messagesContainer = document.getElementById("ai-chat-messages");

  // Append user bubble
  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble bubble-user";
  userBubble.innerText = query;
  messagesContainer.appendChild(userBubble);
  input.value = "";

  // Append temporary typing bubble
  const typingBubble = document.createElement("div");
  typingBubble.className = "chat-bubble bubble-ai";
  typingBubble.innerHTML = `<span style="color:var(--text-dim);font-style:italic">OmniPulse AI is querying live intelligence data...</span>`;
  messagesContainer.appendChild(typingBubble);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  try {
    const res = await fetch(`${API_BASE}/api/ai-chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query }),
    });
    const data = await res.json();

    // Format Markdown bold to HTML
    let formattedAnswer = data.answer.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    formattedAnswer = formattedAnswer.replace(/\n\n/g, "<br><br>").replace(/•/g, "&bull;");

    // Action chips HTML
    const chipsHtml = (data.action_chips || [])
      .map((chip) => `<span class="action-chip" onclick="askAIChat('${chip.replace(/'/g, "\\'")}')">${chip}</span>`)
      .join("");

    typingBubble.innerHTML = `
      <div>${formattedAnswer}</div>
      ${
        data.suggested_tab
          ? `<div style="margin-top:0.6rem">
               <button class="btn-table-action" onclick="document.querySelector('[data-tab=${data.suggested_tab}]').click(); toggleAIChat();">
                 <i data-lucide="external-link" style="width:13px;height:13px"></i> View on Dashboard
               </button>
             </div>`
          : ""
      }
      <div class="action-chips-container">${chipsHtml}</div>
    `;
    lucide.createIcons();
  } catch (err) {
    typingBubble.innerHTML = `<span style="color:#fb7185">Unable to connect to OmniPulse AI. Please try again.</span>`;
  }
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Global Refresh Handler
function refreshAllData() {
  const btn = document.getElementById("btn-refresh");
  btn.classList.add("spinning");
  showToast("Refreshing intelligence data...", "info");

  Promise.all([
    loadOverview(),
    loadSalesTab(),
    loadCustomersTab(),
    loadInventoryTab(),
    loadLogisticsTab(),
    loadGeospatialMap(),
    loadReviewsTab(),
    loadAIInsightsTab(),
  ]).then(() => {
    btn.classList.remove("spinning");
    showToast("All metrics updated successfully!", "success");
  });
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  loadOverview();
  loadSalesTab();
  loadCustomersTab();
  loadInventoryTab();
  loadLogisticsTab();
  loadReviewsTab();
  loadAIInsightsTab();
  updateSimulation();
});

