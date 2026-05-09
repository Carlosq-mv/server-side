document
  .querySelector('[data-tab="history"]')
  .addEventListener("click", handleSearchHistory);

document.querySelectorAll("#tabs button").forEach((btn) => {
  btn.addEventListener("click", () => showTab(btn.dataset.tab));
});

document.getElementById("clear-btn").addEventListener("click", () => {
  document.getElementById("results-container").hidden = true;
  document.getElementById("error-message").hidden = true;
  document.getElementById("ticker-input").value = "";
  // document.getElementById("ticker-input").focus();
});

function showTab(tabName) {
  document
    .querySelectorAll(".tab-panel")
    .forEach((panel) => (panel.hidden = true));
  document.getElementById(`tab-${tabName}`).hidden = false;
  // Highlight the active tab button
  document.querySelectorAll("#tabs button").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tabName);
  });
  console.log(`Now showing the ${tabName} tab`);
}

async function handleSearchHistory() {
  try {
    const data = await getSearchHistory();
    populateSearchHistory(data);
  } catch (e) {
    setErrorMessage(e.message || "Could not load history");
  }
}

function handleSearch() {
  const searchForm = document.getElementById("search-form");

  searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const ticker = getTickerInput();
    if (!ticker) {
      return;
    }

    let data, cache;
    try {
      ({ data, cache } = await searchTicker(ticker));
    } catch (e) {
      setErrorMessage(e.message || "Unexpected error occured");
      document.getElementById("cache-message").innerText = "";
      return;
    }

    // upon successful data retrieval, hide any previous error messages
    document.getElementById("error-message").hidden = true;

    document.getElementById("results-container").hidden = false;
    document.getElementById("tab-outlook").hidden = false;

    // make sure that other tabs stay hidden
    document.getElementById("tab-summary").hidden = true;
    document.getElementById("tab-history").hidden = true;

    // set the cache message if cache HIT
    setCacheMessage(cache);

    // set the Company Outlook tab button to active
    showTab("outlook");

    // populate the Company Outlook and Stock Summary tab
    populateCompanyTab(data.company);
    populateSummaryTab(data.summary);
  });
}

async function searchTicker(ticker) {
  const response = await fetch(`/stock/${encodeURIComponent(ticker)}`);
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error);
  }
  return {
    data: body,
    cache: response.headers.get("X-Cache"),
  };
}

async function getSearchHistory() {
  const response = await fetch("/history");
  const body = await response.json();

  if (!response.ok) {
    throw new Error(body.error);
  }
  return body;
}

function getTickerInput() {
  const ticker = document.getElementById("ticker-input").value.trim();
  if (!ticker) {
    setErrorMessage("Please enter a valid ticker symbol");
    return;
  }

  return ticker;
}

function setErrorMessage(errorMessage) {
  const errorDiv = document.getElementById("error-message");
  errorDiv.hidden = false;
  errorDiv.innerText = errorMessage;
  // hide any previous correct results if there are any
  const resultsContainer = document.getElementById("results-container");
  if (!resultsContainer.hidden) {
    resultsContainer.hidden = true;
  }
  // hide any cache messages if present
  setCacheMessage("");
}

function setCacheMessage(cache) {
  const cacheDiv = document.getElementById("cache-message");

  if (cache && cache === "HIT") {
    cacheDiv.innerText = "Data served from cache";
  } else {
    cacheDiv.innerText = "";
  }
}

function populateCompanyTab(data) {
  document.getElementById("company-name").textContent = data.name;
  document.getElementById("ticker-symbol").textContent = data.ticker;
  document.getElementById("exchange-code").textContent = data.exchange_code;
  document.getElementById("start-date").textContent = data.start_date;
  document.getElementById("description").textContent = data.description;
}

function populateSummaryTab(data) {
  const downArrowSrc = "/static/images/RedArrowDown.png";
  const upArrowSrc = "/static/images/GreenArrowUP.png";

  const changeImg = document.getElementById("summary-change-img");
  const percentImg = document.getElementById("summary-change-percent-img");

  document.getElementById("summary-ticker").textContent = data.ticker;
  document.getElementById("summary-date").textContent = data.date;
  document.getElementById("summary-prev-close").textContent =
    data.prev_close ?? "N/A";
  document.getElementById("summary-open").textContent = data.open;
  document.getElementById("summary-high").textContent = data.high;
  document.getElementById("summary-low").textContent = data.low;
  document.getElementById("summary-last").textContent =
    data.last_price ?? "N/A";

  document.getElementById("summary-change").innerHTML = data.change ?? "N/A";

  if (data.change < 0) {
    changeImg.src = downArrowSrc;
    changeImg.alt = "down arrow";
  } else if (data.change > 0) {
    changeImg.src = upArrowSrc;
    changeImg.alt = "up arrow";
  } else {
    changeImg.src = "";
    changeImg.alt = "";
  }

  document.getElementById("summary-change-percent").textContent =
    data.change_percent ?? "N/A";

  if (data.change_percent < 0) {
    percentImg.src = downArrowSrc;
    percentImg.alt = "down arrow";
  } else if (data.change_percent > 0) {
    percentImg.src = upArrowSrc;
    percentImg.alt = "up arrow";
  } else {
    percentImg.src = "";
    percentImg.alt = "";
  }

  document.getElementById("summary-volume").textContent = data.volume;
}

function populateSearchHistory(rows) {
  const tableBody = document.getElementById("history-body");
  tableBody.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const td1 = document.createElement("td");
    const td2 = document.createElement("td");
    td1.textContent = row.ticker;
    td2.textContent = row.timestamp;
    tr.appendChild(td1);
    tr.appendChild(td2);
    tableBody.appendChild(tr);
  });
}

handleSearch();
