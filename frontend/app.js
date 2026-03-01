const API_URL = "https://ptshsjmunj.execute-api.us-east-1.amazonaws.com/prod/movers";

// DOM references
const loading = document.getElementById("loading");
const error = document.getElementById("error");
const table = document.getElementById("stock-table");
const tbody = document.getElementById("table-body");
const lastUpdated = document.getElementById("last-updated");

async function loadStockData() {
    try {
        console.log("Fetching stock data from API...");
        showLoading();

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const stocks = await response.json();
        console.log("Stock data received:", stocks);

        displayStocks(stocks);
        showLastUpdated();

    } catch (err) {
        console.error("Error fetching stock data:", err);
        showError();
    }
}

function showLoading() {
    loading.style.display = "block";
    error.style.display = "none";
    table.style.display = "none";
    lastUpdated.style.display = "none";
}

function showError() {
    error.style.display = "block";
    loading.style.display = "none";
    table.style.display = "none";
    lastUpdated.style.display = "none";
}

function showTable() {
    table.style.display = "table";
    loading.style.display = "none";
    error.style.display = "none";
    lastUpdated.style.display = "block";
}


function displayStocks(stocks) {
    tbody.innerHTML = "";

    stocks.forEach(stock => {
        const row = document.createElement("tr");

        const isPositive = stock.percentChange >= 0;
        const changeClass = isPositive ? "positive" : "negative";
        const arrow = isPositive ? "&#9650;" : "&#9660;";   // ▲ or ▼
        const sign = isPositive ? "+" : "";
        const pct = `${sign}${parseFloat(stock.percentChange).toFixed(2)}%`;
        const price = formatPrice(stock.closePrice);
        const dateStr = formatDate(stock.date);

        row.innerHTML = `
            <td class="date">${dateStr}</td>
            <td class="ticker">${stock.ticker}</td>
            <td style="text-align:right">
                <span class="percent-change ${changeClass}">
                    <span class="arrow">${arrow}</span>${pct}
                </span>
            </td>
            <td class="price">${price}</td>
        `;

        tbody.appendChild(row);
    });

    showTable();
}

// "2025-02-27" → "02/27"
function formatDate(dateStr) {
    const [year, month, day] = dateStr.split("-");
    return `${month}/${day}`;
}

// 264.18 → "$264.18"
function formatPrice(price) {
    return `$${parseFloat(price).toFixed(2)}`;
}

function showLastUpdated() {
    const now = new Date();
    const formatted = now.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true
    });
    lastUpdated.textContent = `Last updated: ${formatted}`;
}


// run page on load
document.addEventListener("DOMContentLoaded", loadStockData);
