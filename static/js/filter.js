// CONSOLIDATED PRODUCT FILTER FUNCTIONALITY
document.addEventListener('DOMContentLoaded', function() {
    initializeFilter();
    initializePriceRange();
    updateActiveFilters();
    initializeNewFilter();
    initializeFilterFromURL();
});

// Handle price range dropdown change
function handlePriceRangeChange(value) {
    const customPriceRange = document.getElementById('customPriceRange');
    
    if (value === 'custom') {
        customPriceRange.style.display = 'block';
    } else {
        customPriceRange.style.display = 'none';
        
        // Parse and set price range with validation
        if (value && value.includes('-')) {
            const [min, max] = value.split('-').map(Number);
            if (!isNaN(min) && !isNaN(max)) {
                setPriceRange(min, max);
            }
        }
    }
}

// OLD FILTER DESIGN FUNCTIONALITY
function initializeFilter() {
    // Handle form submission
    const filterForm = document.getElementById('mainFilterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', handleFilterSubmit);
    }

    // Handle checkbox changes
    const checkboxes = document.querySelectorAll('.filter-checkbox input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateActiveFilters);
    });

    // Handle sort select change
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', updateActiveFilters);
    }

    // Handle price input changes
    const priceInputs = document.querySelectorAll('.price-input');
    priceInputs.forEach(input => {
        input.addEventListener('input', updateActiveFilters);
    });
}

// Initialize price range slider
function initializePriceRange() {
    const priceRange = document.getElementById('priceRange');
    const minPriceInput = document.getElementById('minPrice');
    const maxPriceInput = document.getElementById('maxPrice');

    if (!priceRange) return;

    let isDragging = false;
    let currentRange = { min: 0, max: 50000000 }; // Default max price 50M VND

    // Create range handles
    const minHandle = document.createElement('div');
    minHandle.className = 'range-handle min-handle';
    const maxHandle = document.createElement('div');
    maxHandle.className = 'range-handle max-handle';
    const rangeProgress = document.createElement('div');
    rangeProgress.className = 'range-progress';

    priceRange.appendChild(rangeProgress);
    priceRange.appendChild(minHandle);
    priceRange.appendChild(maxHandle);

    // Add styles for range slider
    const style = document.createElement('style');
    style.textContent = `
        .price-range {
            position: relative;
            height: 6px;
            background: #e4e7ed;
            border-radius: 3px;
            margin: 20px 0;
        }
        .range-progress {
            position: absolute;
            height: 100%;
            background: #d10024;
            border-radius: 3px;
            left: 0%;
            right: 0%;
        }
        .range-handle {
            position: absolute;
            width: 16px;
            height: 16px;
            background: #d10024;
            border: 2px solid #fff;
            border-radius: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 2;
        }
        .range-handle:hover {
            transform: translate(-50%, -50%) scale(1.1);
        }
        .min-handle {
            left: 0%;
        }
        .max-handle {
            right: 0%;
        }
    `;
    document.head.appendChild(style);

    // Handle dragging
    function handleMouseMove(e, handle) {
        if (!isDragging) return;

        const rect = priceRange.getBoundingClientRect();
        const percent = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
        const value = Math.round((percent / 100) * currentRange.max);

        if (handle.classList.contains('min-handle')) {
            currentRange.min = Math.min(value, currentRange.max - 1000000);
            minHandle.style.left = (currentRange.min / currentRange.max) * 100 + '%';
            minPriceInput.value = currentRange.min;
        } else {
            currentRange.max = Math.max(value, currentRange.min + 1000000);
            maxHandle.style.right = ((currentRange.max - value) / currentRange.max) * 100 + '%';
            maxPriceInput.value = currentRange.max;
        }

        updateRangeProgress();
        updateActiveFilters();
    }

    function handleMouseUp() {
        isDragging = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    }

    function updateRangeProgress() {
        const minPercent = (currentRange.min / currentRange.max) * 100;
        const maxPercent = (currentRange.max / currentRange.max) * 100;
        rangeProgress.style.left = minPercent + '%';
        rangeProgress.style.right = (100 - maxPercent) + '%';
    }

    // Add event listeners
    minHandle.addEventListener('mousedown', function(e) {
        isDragging = true;
        document.addEventListener('mousemove', function(e) { handleMouseMove(e, minHandle); });
        document.addEventListener('mouseup', handleMouseUp);
    });

    maxHandle.addEventListener('mousedown', function(e) {
        isDragging = true;
        document.addEventListener('mousemove', function(e) { handleMouseMove(e, maxHandle); });
        document.addEventListener('mouseup', handleMouseUp);
    });

    // Handle input changes
    minPriceInput.addEventListener('input', function() {
        currentRange.min = parseInt(this.value) || 0;
        minHandle.style.left = (currentRange.min / currentRange.max) * 100 + '%';
        updateRangeProgress();
    });

    maxPriceInput.addEventListener('input', function() {
        currentRange.max = parseInt(this.value) || currentRange.max;
        maxHandle.style.right = ((currentRange.max - currentRange.max) / currentRange.max) * 100 + '%';
        updateRangeProgress();
    });
}

// Toggle filter section
function toggleFilterSection() {
    const filterContent = document.getElementById('filterContent');
    const toggleIcon = document.getElementById('filterToggleIcon');
    const toggleBtn = document.querySelector('.filter-toggle-btn');

    if (filterContent.classList.contains('collapsed')) {
        filterContent.classList.remove('collapsed');
        toggleIcon.className = 'fa fa-chevron-up';
        toggleBtn.classList.remove('collapsed');
    } else {
        filterContent.classList.add('collapsed');
        toggleIcon.className = 'fa fa-chevron-down';
        toggleBtn.classList.add('collapsed');
    }
}

// Handle filter form submission
function handleFilterSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const params = new URLSearchParams();

    // Collect all filter parameters
    for (let [key, value] of formData.entries()) {
        if (value) {
            params.append(key, value);
        }
    }

    // Add loading state
    const filterSection = document.getElementById('product-filter');
    if (filterSection) {
        filterSection.classList.add('filter-loading');
    }

    // Redirect to filtered page
    const url = form.action + '?' + params.toString();
    window.location.href = url;
}

// Clear all filters
function clearFilters() {
    const form = document.getElementById('mainFilterForm');
    if (!form) return;

    // Reset all checkboxes
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    // Reset price inputs
    const priceInputs = form.querySelectorAll('.price-input');
    priceInputs.forEach(input => {
        input.value = '';
    });

    // Reset sort select
    const sortSelect = form.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.value = '';
    }

    // Update active filters display
    updateActiveFilters();

    // Submit form to clear filters
    setTimeout(() => {
        form.submit();
    }, 100);
}

// NEW FILTER DESIGN FUNCTIONALITY
function initializeNewFilter() {
    // Handle form submission
    const sidebarFilterForm = document.getElementById('sidebarFilterForm');
    if (sidebarFilterForm) {
        sidebarFilterForm.addEventListener('submit', handleNewFilterSubmit);
    }

    // Handle checkbox changes
    const checkboxes = document.querySelectorAll('.filter-checkbox-new input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateActiveFiltersNew);
    });

    // Handle price input changes with validation
    const priceInputs = document.querySelectorAll('.price-input-new');
    priceInputs.forEach(input => {
        input.addEventListener('input', function() {
            handlePriceInputChange(this);
        });
        input.addEventListener('blur', function() {
            handlePriceInputChange(this);
        });
    });

    // Initialize section collapse states
    initializeSectionCollapse();
}

// Initialize section collapse functionality
function initializeSectionCollapse() {
    const sectionTitles = document.querySelectorAll('.filter-section-title');
    sectionTitles.forEach(title => {
        title.addEventListener('click', function() {
            const sectionId = this.querySelector('.collapse-btn').getAttribute('onclick').match(/'([^']+)'/)[1];
            toggleSection(sectionId);
        });
    });
}

// Toggle filter section
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const collapseBtn = document.querySelector(`.collapse-btn[onclick*="${sectionId}"]`);
    const icon = collapseBtn.querySelector('i');
    
    if (section.classList.contains('collapsed')) {
        section.classList.remove('collapsed');
        icon.className = 'fa fa-minus';
    } else {
        section.classList.add('collapsed');
        icon.className = 'fa fa-plus';
    }
}

// Toggle entire filter section
function toggleFilterNew() {
    const filterContent = document.getElementById('filterContentNew');
    const toggleIcon = document.getElementById('filterToggleIconNew');
    
    if (filterContent.style.display === 'none') {
        filterContent.style.display = 'block';
        toggleIcon.className = 'fa fa-chevron-up';
    } else {
        filterContent.style.display = 'none';
        toggleIcon.className = 'fa fa-chevron-down';
    }
}

// Set price range from quick select buttons
function setPriceRange(min, max) {
    const minPriceInput = document.getElementById('minPriceNew');
    const maxPriceInput = document.getElementById('maxPriceNew');
    
    if (minPriceInput) minPriceInput.value = min;
    if (maxPriceInput) maxPriceInput.value = max;
    
    // Update active filters
    updateActiveFiltersNew();
    
    // Auto-submit after setting price range
    setTimeout(() => {
        applyFilters();
    }, 300);
}

// Validate and handle price input changes
function handlePriceInputChange(input) {
    let value = parseFloat(input.value) || 0;
    
    // Remove negative values
    if (value < 0) {
        input.value = '';
        return;
    }
    
    // Format to reasonable number (no decimals for VND)
    if (value > 0) {
        input.value = Math.round(value);
    }
    
    // Update active filters display
    updateActiveFiltersNew();
}

// Handle new filter form submission
function handleNewFilterSubmit(e) {
    e.preventDefault();
    applyFilters();
}

// Apply filters
function applyFilters() {
    const form = document.getElementById('sidebarFilterForm');
    if (!form) return;

    // Validate price range
    const minPriceInput = form.querySelector('#minPriceNew');
    const maxPriceInput = form.querySelector('#maxPriceNew');
    
    if (minPriceInput && maxPriceInput) {
        const minPrice = parseFloat(minPriceInput.value) || 0;
        const maxPrice = parseFloat(maxPriceInput.value) || 0;
        
        // Validate price range logic
        if (minPrice > 0 && maxPrice > 0 && minPrice > maxPrice) {
            alert('Giá t i thi u khng th ln hn gi t i a. Vui lng kim tra lai!');
            return;
        }
        
        // Clear invalid price values
        if (minPrice < 0) minPriceInput.value = '';
        if (maxPrice < 0) maxPriceInput.value = '';
    }

    // Add loading state
    const productsArea = document.querySelector('.filter-products-area');
    if (productsArea) {
        productsArea.classList.add('filter-loading-new');
    }

    // Collect form data with proper handling of multiple checkboxes
    const formData = new FormData(form);
    const params = new URLSearchParams();
    const seenParams = new Set(); // Track to avoid duplicates

    for (let [key, value] of formData.entries()) {
        if (value && !seenParams.has(`${key}=${value}`)) {
            params.append(key, value);
            seenParams.add(`${key}=${value}`);
        }
    }

    // Redirect to filtered page
    const url = form.action + '?' + params.toString();
    window.location.href = url;
}

// Clear all filters (new design)
function clearFiltersNew() {
    const form = document.getElementById('sidebarFilterForm');
    if (!form) return;

    // Reset all checkboxes
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    // Reset price inputs
    const priceInputs = form.querySelectorAll('.price-input-new');
    priceInputs.forEach(input => {
        input.value = '';
    });

    // Update active filters display
    updateActiveFiltersNew();

    // Submit form to clear filters
    setTimeout(() => {
        window.location.href = form.action;
    }, 100);
}

// Update active filters display (old design)
function updateActiveFilters() {
    const activeFiltersContainer = document.getElementById('activeFilters');
    if (!activeFiltersContainer) return;

    const form = document.getElementById('mainFilterForm');
    if (!form) return;

    const activeFilters = [];

    // Check price filters
    const minPrice = form.querySelector('#minPrice').value;
    const maxPrice = form.querySelector('#maxPrice').value;
    if (minPrice || maxPrice) {
        activeFilters.push({
            type: 'price',
            label: `Giá: ${minPrice ? formatPrice(minPrice) : '0'} - ${maxPrice ? formatPrice(maxPrice) : 'Vô cùng'}`,
            value: { min: minPrice, max: maxPrice }
        });
    }

    // Check category filters
    const checkedCategories = form.querySelectorAll('input[name="category"]:checked');
    checkedCategories.forEach(checkbox => {
        activeFilters.push({
            type: 'category',
            label: `Danh muc: ${checkbox.nextElementSibling.nextElementSibling.textContent}`,
            value: checkbox.value
        });
    });

    // Check brand filters
    const checkedBrands = form.querySelectorAll('input[name="brand"]:checked');
    checkedBrands.forEach(checkbox => {
        activeFilters.push({
            type: 'brand',
            label: `Thng hiu: ${checkbox.nextElementSibling.nextElementSibling.textContent}`,
            value: checkbox.value
        });
    });

    // Check additional filters
    const additionalFilters = ['sale', 'new', 'hot'];
    additionalFilters.forEach(filterType => {
        const checkbox = form.querySelector(`input[name="${filterType}"]:checked`);
        if (checkbox) {
            const labels = {
                'sale': 'ang gi m',
                'new': 'Sn phm mi',
                'hot': 'Hot Deal'
            };
            activeFilters.push({
                type: filterType,
                label: labels[filterType],
                value: checkbox.value
            });
        }
    });

    // Check sort filter
    const sortSelect = form.querySelector('#sortSelect');
    if (sortSelect && sortSelect.value) {
        const sortLabels = {
            'price_asc': 'Gi t thp',
            'price_desc': 'Gi cao thp',
            'name_az': 'Tn A-Z',
            'name_za': 'Tn Z-A',
            'newest': 'Mi nh'
        };
        activeFilters.push({
            type: 'sort',
            label: `S p: ${sortLabels[sortSelect.value] || sortSelect.value}`,
            value: sortSelect.value
        });
    }

    // Display active filters
    displayActiveFilters(activeFilters);
}

// Update active filters display (new design)
function updateActiveFiltersNew() {
    const activeFiltersContainer = document.getElementById('activeFiltersNew');
    if (!activeFiltersContainer) return;

    const form = document.getElementById('sidebarFilterForm');
    if (!form) return;

    const activeFilters = [];

    // Check price filters
    const minPrice = form.querySelector('#minPriceNew').value;
    const maxPrice = form.querySelector('#maxPriceNew').value;
    if (minPrice || maxPrice) {
        activeFilters.push({
            type: 'price',
            label: `Giá: ${minPrice ? formatPrice(minPrice) : '0'} - ${maxPrice ? formatPrice(maxPrice) : 'Vô cùng'}`,
            value: { min: minPrice, max: maxPrice }
        });
    }

    // Check category filters
    const checkedCategories = form.querySelectorAll('input[name="category"]:checked');
    checkedCategories.forEach(checkbox => {
        const label = checkbox.nextElementSibling.nextElementSibling.textContent;
        activeFilters.push({
            type: 'category',
            label: `Loài: ${label}`,
            value: checkbox.value
        });
    });

    // Check brand filters
    const checkedBrands = form.querySelectorAll('input[name="brand"]:checked');
    checkedBrands.forEach(checkbox => {
        const label = checkbox.nextElementSibling.nextElementSibling.textContent;
        activeFilters.push({
            type: 'brand',
            label: `Hãng: ${label}`,
            value: checkbox.value
        });
    });

    // Check additional filters
    const additionalFilters = ['sale', 'new', 'hot'];
    additionalFilters.forEach(filterType => {
        const checkbox = form.querySelector(`input[name="${filterType}"]:checked`);
        if (checkbox) {
            const labels = {
                'sale': 'ang Gi M',
                'new': 'Sán Ph M M i',
                'hot': 'Hot Deal'
            };
            activeFilters.push({
                type: filterType,
                label: labels[filterType],
                value: checkbox.value
            });
        }
    });

    // Display active filters
    displayActiveFiltersNew(activeFilters);
}

// Display active filters (old design)
function displayActiveFilters(filters) {
    const container = document.getElementById('activeFilters');
    if (!container) return;

    container.innerHTML = '';

    if (filters.length === 0) {
        container.innerHTML = '<span style="color: #8d99ae; font-size: 14px;">Chua c b lc no</span>';
        return;
    }

    filters.forEach(filter => {
        const filterTag = document.createElement('div');
        filterTag.className = 'active-filter-tag';
        filterTag.innerHTML = `
            ${filter.label}
            <span class="remove-filter" onclick="removeFilter('${filter.type}', '${filter.value}')">&times;</span>
        `;
        container.appendChild(filterTag);
    });
}

// Display active filters (new design)
function displayActiveFiltersNew(filters) {
    const container = document.getElementById('activeFiltersNew');
    if (!container) return;

    container.innerHTML = '';

    if (filters.length === 0) {
        container.innerHTML = '<span style="color: #8d99ae; font-size: 12px;">Chưa có bộ lọc nào</span>';
        return;
    }

    filters.forEach(filter => {
        const filterTag = document.createElement('div');
        filterTag.className = 'active-filter-tag-new';
        
        // Handle price filter differently since value is an object
        let removeValue = filter.value;
        if (filter.type === 'price' && typeof filter.value === 'object') {
            removeValue = JSON.stringify(filter.value);
        }
        
        filterTag.innerHTML = `
            ${filter.label}
            <span class="remove-filter-new" onclick="removeFilterNew('${filter.type}', '${removeValue}')">&times;</span>
        `;
        container.appendChild(filterTag);
    });
}

// Remove individual filter (old design)
function removeFilter(type, value) {
    const form = document.getElementById('mainFilterForm');
    if (!form) return;

    switch (type) {
        case 'price':
            form.querySelector('#minPrice').value = '';
            form.querySelector('#maxPrice').value = '';
            break;
        case 'category':
        case 'brand':
        case 'sale':
        case 'new':
        case 'hot':
            const checkbox = form.querySelector(`input[name="${type}"][value="${value}"]`);
            if (checkbox) checkbox.checked = false;
            break;
        case 'sort':
            const sortSelect = form.querySelector('#sortSelect');
            if (sortSelect) sortSelect.value = '';
            break;
    }

    updateActiveFilters();
    
    // Auto-submit after removing filter
    setTimeout(() => {
        form.submit();
    }, 100);
}

// Remove individual filter (new design)
function removeFilterNew(type, value) {
    const form = document.getElementById('sidebarFilterForm');
    if (!form) return;

    switch (type) {
        case 'price':
            const minInput = form.querySelector('#minPriceNew');
            const maxInput = form.querySelector('#maxPriceNew');
            if (minInput) minInput.value = '';
            if (maxInput) maxInput.value = '';
            break;
        case 'category':
        case 'brand':
        case 'sale':
        case 'new':
        case 'hot':
            const checkbox = form.querySelector(`input[name="${type}"][value="${value}"]`);
            if (checkbox) checkbox.checked = false;
            break;
    }

    updateActiveFiltersNew();
    
    // Auto-submit after removing filter
    setTimeout(() => {
        applyFilters();
    }, 100);
}

// Apply sorting (new design)
function applySorting() {
    const sortSelect = document.getElementById('sortSelectNew');
    if (!sortSelect) return;

    const form = document.getElementById('sidebarFilterForm');
    if (!form) return;

    // Create a hidden input for sort if it doesn't exist
    let sortInput = form.querySelector('input[name="sort"]');
    if (!sortInput) {
        sortInput = document.createElement('input');
        sortInput.type = 'hidden';
        sortInput.name = 'sort';
        form.appendChild(sortInput);
    }

    sortInput.value = sortSelect.value;

    // Update active filters display
    updateActiveFiltersNew();
    
    // Apply filters with sorting
    setTimeout(() => {
        applyFilters();
    }, 100);
}

// Set view mode (grid/list)
function setViewMode(mode) {
    const productsGrid = document.getElementById('filteredProducts');
    const viewButtons = document.querySelectorAll('.view-btn');
    
    if (!productsGrid) return;

    // Update button states
    viewButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Set active button
    const activeBtn = document.querySelector(`.view-btn[onclick="setViewMode('${mode}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    // Update grid class
    if (mode === 'list') {
        productsGrid.classList.add('list-view');
    } else {
        productsGrid.classList.remove('list-view');
    }

    // Save preference to localStorage
    localStorage.setItem('filterViewMode', mode);
}

// Format price for display
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN').format(price) + ' VN';
}

// Get URL parameter
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Initialize filters from URL parameters
function initializeFilterFromURL() {
    // Initialize old design filters
    const oldForm = document.getElementById('mainFilterForm');
    if (oldForm) {
        // Set price filters
        const minPrice = getUrlParameter('min_price');
        const maxPrice = getUrlParameter('max_price');
        if (minPrice) {
            const minInput = oldForm.querySelector('#minPrice');
            if (minInput) minInput.value = minPrice;
        }
        if (maxPrice) {
            const maxInput = oldForm.querySelector('#maxPrice');
            if (maxInput) maxInput.value = maxPrice;
        }

        // Set checkbox filters
        const checkboxParams = ['category', 'brand', 'sale', 'new', 'hot'];
        checkboxParams.forEach(param => {
            const values = getUrlParameter(param);
            if (values) {
                const valueArray = values.split(',');
                valueArray.forEach(value => {
                    const checkbox = oldForm.querySelector(`input[name="${param}"][value="${value}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            }
        });

        // Set sort filter
        const sort = getUrlParameter('sort');
        if (sort) {
            const sortSelect = oldForm.querySelector('#sortSelect');
            if (sortSelect) sortSelect.value = sort;
        }

        updateActiveFilters();
    }

    // Initialize new design filters
    const newForm = document.getElementById('sidebarFilterForm');
    if (newForm) {
        // Set price filters
        const minPrice = getUrlParameter('min_price');
        const maxPrice = getUrlParameter('max_price');
        if (minPrice) {
            const minInput = newForm.querySelector('#minPriceNew');
            if (minInput) minInput.value = minPrice;
        }
        if (maxPrice) {
            const maxInput = newForm.querySelector('#maxPriceNew');
            if (maxInput) maxInput.value = maxPrice;
        }

        // Set checkbox filters
        const checkboxParams = ['category', 'brand', 'sale', 'new', 'hot'];
        checkboxParams.forEach(param => {
            const values = getUrlParameter(param);
            if (values) {
                const valueArray = values.split(',');
                valueArray.forEach(value => {
                    const checkbox = newForm.querySelector(`input[name="${param}"][value="${value}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            }
        });

        // Set sort filter
        const sort = getUrlParameter('sort');
        if (sort) {
            const sortSelect = document.getElementById('sortSelectNew');
            if (sortSelect) sortSelect.value = sort;
        }

        // Update active filters display
        updateActiveFiltersNew();

        // Initialize view mode
        const savedViewMode = localStorage.getItem('filterViewMode');
        if (savedViewMode) {
            setViewMode(savedViewMode);
        }

        // Update product count
        updateProductCount();
    }
}

// Update product count with actual data
function updateProductCount() {
    const countElement = document.getElementById('filteredCount');
    if (countElement) {
        // Count actual products displayed on page
        const productItems = document.querySelectorAll('.filtered-products-grid .product-item');
        countElement.textContent = productItems.length;
    }
}

// Handle pagination
function goToPage(page) {
    const form = document.getElementById('sidebarFilterForm');
    if (!form) return;

    // Create or update page input
    let pageInput = form.querySelector('input[name="page"]');
    if (!pageInput) {
        pageInput = document.createElement('input');
        pageInput.type = 'hidden';
        pageInput.name = 'page';
        form.appendChild(pageInput);
    }

    pageInput.value = page;
    applyFilters();
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const minPriceInput = document.getElementById('minPriceNew');
        if (minPriceInput) minPriceInput.focus();
    }

    // Escape to clear filters
    if (e.key === 'Escape') {
        clearFiltersNew();
    }
});

// Mobile responsiveness
function handleMobileFilter() {
    const filterSection = document.getElementById('product-filter-new');
    const filterToggle = document.querySelector('.filter-toggle-btn-new');
    
    if (window.innerWidth <= 767) {
        // Auto-collapse on mobile
        if (filterSection && filterToggle) {
            const filterContent = document.getElementById('filterContentNew');
            if (filterContent && filterContent.style.display !== 'none') {
                toggleFilterNew();
            }
        }
    } else {
        // Auto-expand on desktop
        if (filterSection && filterToggle) {
            const filterContent = document.getElementById('filterContentNew');
            if (filterContent && filterContent.style.display === 'none') {
                toggleFilterNew();
            }
        }
    }
}

// Initialize mobile handling
window.addEventListener('resize', handleMobileFilter);
handleMobileFilter();

// Initialize filter functionality
function initializeFilter() {
    // Handle form submission
    const filterForm = document.getElementById('mainFilterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', handleFilterSubmit);
    }

    // Handle checkbox changes
    const checkboxes = document.querySelectorAll('.filter-checkbox input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateActiveFilters);
    });

    // Handle sort select change
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', updateActiveFilters);
    }

    // Handle price input changes
    const priceInputs = document.querySelectorAll('.price-input');
    priceInputs.forEach(input => {
        input.addEventListener('input', updateActiveFilters);
    });
}

// Initialize price range slider
function initializePriceRange() {
    const priceRange = document.getElementById('priceRange');
    const minPriceInput = document.getElementById('minPrice');
    const maxPriceInput = document.getElementById('maxPrice');

    if (!priceRange) return;

    let isDragging = false;
    let currentRange = { min: 0, max: 50000000 }; // Default max price 50M VND

    // Create range handles
    const minHandle = document.createElement('div');
    minHandle.className = 'range-handle min-handle';
    const maxHandle = document.createElement('div');
    maxHandle.className = 'range-handle max-handle';
    const rangeProgress = document.createElement('div');
    rangeProgress.className = 'range-progress';

    priceRange.appendChild(rangeProgress);
    priceRange.appendChild(minHandle);
    priceRange.appendChild(maxHandle);

    // Add styles for range slider
    const style = document.createElement('style');
    style.textContent = `
        .price-range {
            position: relative;
            height: 6px;
            background: #e4e7ed;
            border-radius: 3px;
            margin: 20px 0;
        }
        .range-progress {
            position: absolute;
            height: 100%;
            background: #d10024;
            border-radius: 3px;
            left: 0%;
            right: 0%;
        }
        .range-handle {
            position: absolute;
            width: 16px;
            height: 16px;
            background: #d10024;
            border: 2px solid #fff;
            border-radius: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 2;
        }
        .range-handle:hover {
            transform: translate(-50%, -50%) scale(1.1);
        }
        .min-handle {
            left: 0%;
        }
        .max-handle {
            right: 0%;
        }
    `;
    document.head.appendChild(style);

    // Handle dragging
    function handleMouseMove(e, handle) {
        if (!isDragging) return;

        const rect = priceRange.getBoundingClientRect();
        const percent = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
        const value = Math.round((percent / 100) * currentRange.max);

        if (handle.classList.contains('min-handle')) {
            currentRange.min = Math.min(value, currentRange.max - 1000000);
            minHandle.style.left = (currentRange.min / currentRange.max) * 100 + '%';
            minPriceInput.value = currentRange.min;
        } else {
            currentRange.max = Math.max(value, currentRange.min + 1000000);
            maxHandle.style.right = ((currentRange.max - value) / currentRange.max) * 100 + '%';
            maxPriceInput.value = currentRange.max;
        }

        updateRangeProgress();
        updateActiveFilters();
    }

    function handleMouseUp() {
        isDragging = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    }

    function updateRangeProgress() {
        const minPercent = (currentRange.min / currentRange.max) * 100;
        const maxPercent = (currentRange.max / currentRange.max) * 100;
        rangeProgress.style.left = minPercent + '%';
        rangeProgress.style.right = (100 - maxPercent) + '%';
    }

    // Add event listeners
    minHandle.addEventListener('mousedown', function(e) {
        isDragging = true;
        document.addEventListener('mousemove', function(e) { handleMouseMove(e, minHandle); });
        document.addEventListener('mouseup', handleMouseUp);
    });

    maxHandle.addEventListener('mousedown', function(e) {
        isDragging = true;
        document.addEventListener('mousemove', function(e) { handleMouseMove(e, maxHandle); });
        document.addEventListener('mouseup', handleMouseUp);
    });

    // Handle input changes
    minPriceInput.addEventListener('input', function() {
        currentRange.min = parseInt(this.value) || 0;
        minHandle.style.left = (currentRange.min / currentRange.max) * 100 + '%';
        updateRangeProgress();
    });

    maxPriceInput.addEventListener('input', function() {
        currentRange.max = parseInt(this.value) || currentRange.max;
        maxHandle.style.right = ((currentRange.max - currentRange.max) / currentRange.max) * 100 + '%';
        updateRangeProgress();
    });
}

// Toggle filter section
function toggleFilterSection() {
    const filterContent = document.getElementById('filterContent');
    const toggleIcon = document.getElementById('filterToggleIcon');
    const toggleBtn = document.querySelector('.filter-toggle-btn');

    if (filterContent.classList.contains('collapsed')) {
        filterContent.classList.remove('collapsed');
        toggleIcon.className = 'fa fa-chevron-up';
        toggleBtn.classList.remove('collapsed');
    } else {
        filterContent.classList.add('collapsed');
        toggleIcon.className = 'fa fa-chevron-down';
        toggleBtn.classList.add('collapsed');
    }
}

// Handle filter form submission
function handleFilterSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const params = new URLSearchParams();

    // Collect all filter parameters
    for (let [key, value] of formData.entries()) {
        if (value) {
            params.append(key, value);
        }
    }

    // Add loading state
    const filterSection = document.getElementById('product-filter');
    filterSection.classList.add('filter-loading');

    // Redirect to filtered page
    const url = form.action + '?' + params.toString();
    window.location.href = url;
}

// Clear all filters
function clearFilters() {
    const form = document.getElementById('mainFilterForm');
    if (!form) return;

    // Reset all checkboxes
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    // Reset price inputs
    const priceInputs = form.querySelectorAll('.price-input');
    priceInputs.forEach(input => {
        input.value = '';
    });

    // Reset sort select
    const sortSelect = form.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.value = '';
    }

    // Update active filters display
    updateActiveFilters();

    // Submit form to clear filters
    setTimeout(() => {
        form.submit();
    }, 100);
}

// Update active filters display
function updateActiveFilters() {
    const activeFiltersContainer = document.getElementById('activeFilters');
    if (!activeFiltersContainer) return;

    const form = document.getElementById('mainFilterForm');
    if (!form) return;

    const activeFilters = [];

    // Check price filters
    const minPrice = form.querySelector('#minPrice').value;
    const maxPrice = form.querySelector('#maxPrice').value;
    if (minPrice || maxPrice) {
        activeFilters.push({
            type: 'price',
            label: `Giá: ${minPrice ? formatPrice(minPrice) : '0'} - ${maxPrice ? formatPrice(maxPrice) : 'Vô cùng'}`,
            value: { min: minPrice, max: maxPrice }
        });
    }

    // Check category filters
    const checkedCategories = form.querySelectorAll('input[name="category"]:checked');
    checkedCategories.forEach(checkbox => {
        activeFilters.push({
            type: 'category',
            label: `Danh muc: ${checkbox.nextElementSibling.nextElementSibling.textContent}`,
            value: checkbox.value
        });
    });

    // Check brand filters
    const checkedBrands = form.querySelectorAll('input[name="brand"]:checked');
    checkedBrands.forEach(checkbox => {
        activeFilters.push({
            type: 'brand',
            label: `Thng hiu: ${checkbox.nextElementSibling.nextElementSibling.textContent}`,
            value: checkbox.value
        });
    });

    // Check additional filters
    const additionalFilters = ['sale', 'new', 'hot'];
    additionalFilters.forEach(filterType => {
        const checkbox = form.querySelector(`input[name="${filterType}"]:checked`);
        if (checkbox) {
            const labels = {
                'sale': 'ang gi m',
                'new': 'Sn phm mi',
                'hot': 'Hot Deal'
            };
            activeFilters.push({
                type: filterType,
                label: labels[filterType],
                value: checkbox.value
            });
        }
    });

    // Check sort filter
    const sortSelect = form.querySelector('#sortSelect');
    if (sortSelect && sortSelect.value) {
        const sortLabels = {
            'price_asc': 'Gi t thp',
            'price_desc': 'Gi cao thp',
            'name_az': 'Tn A-Z',
            'name_za': 'Tn Z-A',
            'newest': 'Mi nh'
        };
        activeFilters.push({
            type: 'sort',
            label: `S p: ${sortLabels[sortSelect.value] || sortSelect.value}`,
            value: sortSelect.value
        });
    }

    // Display active filters
    displayActiveFilters(activeFilters);
}

// Display active filters
function displayActiveFilters(filters) {
    const container = document.getElementById('activeFilters');
    if (!container) return;

    container.innerHTML = '';

    if (filters.length === 0) {
        container.innerHTML = '<span style="color: #8d99ae; font-size: 14px;">Chua c b lc no</span>';
        return;
    }

    filters.forEach(filter => {
        const filterTag = document.createElement('div');
        filterTag.className = 'active-filter-tag';
        filterTag.innerHTML = `
            ${filter.label}
            <span class="remove-filter" onclick="removeFilter('${filter.type}', '${filter.value}')">&times;</span>
        `;
        container.appendChild(filterTag);
    });
}

// Remove individual filter
function removeFilter(type, value) {
    const form = document.getElementById('mainFilterForm');
    if (!form) return;

    switch (type) {
        case 'price':
            form.querySelector('#minPrice').value = '';
            form.querySelector('#maxPrice').value = '';
            break;
        case 'category':
        case 'brand':
        case 'sale':
        case 'new':
        case 'hot':
            const checkbox = form.querySelector(`input[name="${type}"][value="${value}"]`);
            if (checkbox) checkbox.checked = false;
            break;
        case 'sort':
            const sortSelect = form.querySelector('#sortSelect');
            if (sortSelect) sortSelect.value = '';
            break;
    }

    updateActiveFilters();
    
    // Auto-submit after removing filter
    setTimeout(() => {
        form.submit();
    }, 100);
}

// Format price for display
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN').format(price) + ' VN';
}

// URL parameter handling
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Initialize filters from URL parameters
function initializeFiltersFromUrl() {
    const form = document.getElementById('mainFilterForm');
    if (!form) return;

    // Set price filters
    const minPrice = getUrlParameter('min_price');
    const maxPrice = getUrlParameter('max_price');
    if (minPrice) form.querySelector('#minPrice').value = minPrice;
    if (maxPrice) form.querySelector('#maxPrice').value = maxPrice;

    // Set checkbox filters
    const checkboxParams = ['category', 'brand', 'sale', 'new', 'hot'];
    checkboxParams.forEach(param => {
        const values = getUrlParameter(param);
        if (values) {
            const valueArray = values.split(',');
            valueArray.forEach(value => {
                const checkbox = form.querySelector(`input[name="${param}"][value="${value}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
    });

    // Set sort filter
    const sort = getUrlParameter('sort');
    if (sort) {
        const sortSelect = form.querySelector('#sortSelect');
        if (sortSelect) sortSelect.value = sort;
    }

    updateActiveFilters();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeFiltersFromUrl();
});
