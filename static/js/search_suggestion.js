(function () {
  var searchInput = document.getElementById("custom-search-input");
  var suggestionBox = document.getElementById("search-suggestions-box");

  if (!searchInput || !suggestionBox) {
    return;
  }

  var searchUrl = searchInput.dataset.searchUrl;
  var placeholderImage = searchInput.dataset.placeholderImage || "";
  if (!searchUrl) {
    return;
  }

  var debounceTimer = null;
  var currentSuggestions = [];
  var activeIndex = -1;
  var currentQuery = "";
  var pendingController = null;
  var requestId = 0;
  var cachedResults = {};

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function escapeRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function formatPrice(price) {
    var numeric = Number(price);
    if (Number.isNaN(numeric)) {
      return escapeHtml(price) + " VNĐ";
    }
    return numeric.toLocaleString("vi-VN") + " VNĐ";
  }

  function hideBox() {
    suggestionBox.classList.add("d-none");
    suggestionBox.innerHTML = "";
    currentSuggestions = [];
    activeIndex = -1;
  }

  function showBox() {
    suggestionBox.classList.remove("d-none");
  }

  function renderLoading() {
    suggestionBox.innerHTML =
      '<div class="list-group list-group-flush">' +
      '<div class="list-group-item text-muted text-center small">' +
      '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' +
      "Đang tìm kiếm..." +
      "</div></div>";
    showBox();
  }

  function highlightKeyword(text, keyword) {
    var escapedText = escapeHtml(text);
    if (!keyword) {
      return escapedText;
    }

    var regex = new RegExp("(" + escapeRegExp(keyword) + ")", "ig");
    return escapedText.replace(regex, "<strong>$1</strong>");
  }

  function renderEmptyState(keyword) {
    suggestionBox.innerHTML =
      '<div class="list-group list-group-flush">' +
      '<div class="list-group-item text-muted text-center small">' +
      'Khong tim thay san pham phu hop voi tu khoa: "' +
      escapeHtml(keyword) +
      '"' +
      "</div></div>";
    showBox();
  }

  function renderSuggestions(items, keyword) {
    currentSuggestions = items;
    activeIndex = -1;

    var html = '<div class="list-group list-group-flush">';
    items.forEach(function (item, index) {
      var imageSrc = item.image || placeholderImage;
      var imageHtml = imageSrc
        ? '<img src="' +
          escapeHtml(imageSrc) +
          '" alt="' +
          escapeHtml(item.name) +
          '" class="rounded" style="width: 42px; height: 42px; object-fit: cover;">'
        : '<div class="bg-light rounded d-flex align-items-center justify-content-center text-muted" style="width: 42px; height: 42px;">' +
          '<i class="fa fa-image"></i></div>';

      html +=
        '<button type="button" class="list-group-item list-group-item-action js-suggestion-item" data-index="' +
        index +
        '">' +
        '<div class="d-flex align-items-center gap-2">' +
        imageHtml +
        '<div class="flex-grow-1 text-start">' +
        '<div class="fw-semibold small">' +
        highlightKeyword(item.name, keyword) +
        "</div>" +
        '<div class="text-muted small">' +
        escapeHtml(item.brand || item.category || "") +
        "</div>" +
        '<div class="text-danger small">' +
        formatPrice(item.price) +
        "</div>" +
        "</div></div></button>";
    });
    html += "</div>";

    suggestionBox.innerHTML = html;
    showBox();
  }

  function updateActiveItem(nextIndex) {
    var elements = suggestionBox.querySelectorAll(".js-suggestion-item");
    if (!elements.length) {
      activeIndex = -1;
      return;
    }

    if (nextIndex < 0) {
      nextIndex = elements.length - 1;
    } else if (nextIndex >= elements.length) {
      nextIndex = 0;
    }

    elements.forEach(function (el) {
      el.classList.remove("active");
    });
    elements[nextIndex].classList.add("active");
    elements[nextIndex].scrollIntoView({ block: "nearest" });
    activeIndex = nextIndex;
  }

  function selectSuggestion(index) {
    var item = currentSuggestions[index];
    if (!item) {
      return;
    }

    if (item.url) {
      window.location.href = item.url;
      return;
    }

    searchInput.value = item.name;
    hideBox();

    var form = searchInput.closest("form");
    if (form) {
      form.submit();
    }
  }

  function submitSearchForm() {
    var form = searchInput.closest("form");
    if (!form) {
      return;
    }
    form.submit();
  }

  function fetchSuggestions(query) {
    if (cachedResults[query]) {
      var cached = cachedResults[query];
      if (!cached.length) {
        renderEmptyState(query);
        return;
      }
      renderSuggestions(cached, query);
      return;
    }

    if (pendingController) {
      pendingController.abort();
    }
    pendingController = new AbortController();

    requestId += 1;
    var currentRequestId = requestId;
    currentQuery = query;
    renderLoading();

    fetch(searchUrl + "?q=" + encodeURIComponent(query), {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" },
      signal: pendingController.signal,
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Fetch failed");
        }
        return response.json();
      })
      .then(function (data) {
        if (currentRequestId !== requestId) {
          return;
        }

        var items = Array.isArray(data.suggestions) ? data.suggestions : [];
        cachedResults[query] = items;
        if (!items.length) {
          renderEmptyState(currentQuery);
          return;
        }
        renderSuggestions(items, currentQuery);
      })
      .catch(function (error) {
        if (error.name === "AbortError") {
          return;
        }
        renderEmptyState(currentQuery);
      });
  }

  searchInput.addEventListener("input", function (event) {
    var query = event.target.value.trim();
    currentQuery = query;

    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    if (query.length < 2) {
      if (pendingController) {
        pendingController.abort();
      }
      hideBox();
      return;
    }

    debounceTimer = setTimeout(function () {
      fetchSuggestions(query);
    }, 300);
  });

  searchInput.addEventListener("keydown", function (event) {
    var isVisible = !suggestionBox.classList.contains("d-none");
    if (!isVisible || !currentSuggestions.length) {
      if (event.key === "Enter") {
        event.preventDefault();
        submitSearchForm();
      }
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      updateActiveItem(activeIndex + 1);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      updateActiveItem(activeIndex - 1);
      return;
    }

    if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      selectSuggestion(activeIndex);
      return;
    }

    if (event.key === "Enter") {
      event.preventDefault();
      submitSearchForm();
    }
  });

  suggestionBox.addEventListener("click", function (event) {
    var button = event.target.closest(".js-suggestion-item");
    if (!button) {
      return;
    }
    var index = Number(button.dataset.index);
    if (!Number.isNaN(index)) {
      selectSuggestion(index);
    }
  });

  suggestionBox.addEventListener("mousemove", function (event) {
    var button = event.target.closest(".js-suggestion-item");
    if (!button) {
      return;
    }
    var index = Number(button.dataset.index);
    if (!Number.isNaN(index) && index !== activeIndex) {
      updateActiveItem(index);
    }
  });

  document.addEventListener("click", function (event) {
    if (!searchInput.contains(event.target) && !suggestionBox.contains(event.target)) {
      hideBox();
    }
  });
})();
