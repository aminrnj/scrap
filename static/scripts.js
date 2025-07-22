// static/scripts.js

document.addEventListener("DOMContentLoaded", function () {
  // تعریف متغیرهای سراسری
  const columnTitles = {
    category: "دسته‌بندی",
    color: "رنگ",
    hamrahtel_price: "همراه تل",
    farnaa_price: "فرنا",
    aasood_price: "اسود",
    technobusiness_price: "تکنو",
    kasrapars_price: "کسری",
    min_price: "کمترین قیمت",
    date: "بروزرسانی"
  };

  const percentLabels = [
    { percent: 3, label: "1%" },
    { percent: 4, label: "2%" },
    { percent: 5, label: "3%" },
    { percent: 7, label: "5%" },
    { percent: 11.5, label: "داریک" },
    { percent: 1.5, label: "رست این" },
  ];

  window.priceChartInstance = null;

  // توابع کمکی
  function showToastMessage(message, isSuccess = true) {
    const toast = document.getElementById("toast-message");
    toast.textContent = message;
    toast.style.backgroundColor = isSuccess ? "#28a745" : "#dc3545";
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 10000);
  }

  function parseNumber(str) {
    if (typeof str !== "string") return Number(str) || 0;
    const cleaned = str.replace(/,/g, "");
    return isNaN(cleaned) ? 0 : parseInt(cleaned, 10);
  }

  function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  // دریافت و نمایش محصولات
  function fetchProducts(query = "") {
    fetch(`/api/products?search=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        const productCardsContainer = document.getElementById("product-cards");
        productCardsContainer.innerHTML = "";
        if (data.length === 0) {
          productCardsContainer.innerHTML = "<p>نتیجه‌ای یافت نشد.</p>";
          return;
        }
        data.forEach((product) => {
          const card = document.createElement("div");
          card.classList.add("col-md-4", "product-card");

          // آیکون چارت (همانند قبل)
          const chartIconHTML = `
            <div class="chart-icon" data-model="${product.model}" data-color="${product.color}">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-bar-chart-line" viewBox="0 0 16 16">
                <path d="M11 0a1 1 0 0 1 1 1v12a1 1 0 0 1-2 0V1a1 1 0 0 1 1-1z"/>
                <path d="M6 4a1 1 0 0 1 1 1v9a1 1 0 0 1-2 0V5a1 1 0 0 1 1-1z"/>
                <path d="M1 8a1 1 0 0 1 1 1v5a1 1 0 0 1-2 0v-5a1 1 0 0 1 1-1z"/>
                <path d="M14 13a1 1 0 0 1 1 1v2a1 1 0 0 1-2 0v-2a1 1 0 0 1 1-1z"/>
              </svg>
            </div>
          `;

          // استفاده از شیء productLinks که در فایل product_links.js تعریف شده است
          const links = productLinks[product.model] || { digikala: "#", kalatic: "#" };
          const digikalaLink = links.digikala;
          const kalaticLink = links.kalatic;
          const linkIconsHTML = `
            <div class="link-icons">
              <a href="${digikalaLink}" target="_blank">
                <img src="/static/img/digi.png" alt="دیجیکالا">
              </a>
              <a href="${kalaticLink}" target="_blank">
                <img src="/static/img/kalatic.png" alt="کالاتیک">
              </a>
            </div>
          `;

          let cardContent = chartIconHTML + linkIconsHTML;
          cardContent += `<h5>${product.model || "بدون عنوان"}</h5>`;

          for (const [key, title] of Object.entries(columnTitles)) {
            if (product[key] !== undefined) {
              let value = product[key] || "ناموجود";
              if (key === "min_price") {
                const prices = [
                  parseNumber(product.hamrahtel_price || "0"),
                  parseNumber(product.farnaa_price || "0"),
                  parseNumber(product.aasood_price || "0"),
                  parseNumber(product.technobusiness_price || "0"),
                  parseNumber(product.kasrapars_price || "0")
                ].filter((p) => p > 0);
                cardContent += `
                  <p><strong>${title}:</strong>
                    <select class="price-selector">
                      ${prices.map((price) => `<option value="${price}">${formatNumber(price)}</option>`).join("")}
                    </select>
                  </p>`;
                if (window.canViewPredefinedPercent) {
                  cardContent += `<div class="percent-results"></div>`;
                }
                if (window.canUseCustomPercent) {
                  cardContent += `
                    <div class="custom-percent-calculation mt-2">
                      <input type="number" class="form-control custom-percent-input" placeholder="درصد سفارشی:" style="width:80px; display:inline-block;">
                      <span class="custom-percent-result ms-2"></span>
                    </div>`;
                }
              } else if (key === "color") {
                cardContent += `
                  <p><strong>${title}:</strong>
                    <span class="color-box" style="background-color: ${value.toLowerCase()};"></span>
                    ${value}
                  </p>`;
              } else if (key === "date") {
                cardContent += `<p><strong>${title}:</strong> ${moment(value).fromNow()}</p>`;
              } else {
                cardContent += `<p><strong>${title}:</strong> ${formatNumber(value)}</p>`;
              }
            }
          }
          card.innerHTML = cardContent;
          productCardsContainer.appendChild(card);

          const priceSelector = card.querySelector(".price-selector");
          const chartIcon = card.querySelector(".chart-icon");
          if (chartIcon) {
            chartIcon.addEventListener("click", function () {
              const productModel = this.getAttribute("data-model");
              const productColor = this.getAttribute("data-color");
              document.getElementById('priceChartModalLabel').textContent = "چارت قیمت - " + productModel + " (" + productColor + ")";
              fetch(`/api/product-history/${productModel}`)
                .then(response => response.json())
                .then(data => {
                  const labels = data.map(item => moment(item.date).format('jYYYY/jMM/jDD'));
                  const hamrahtelPrices = data.map(item => parseNumber(item.hamrahtel_price || "0"));
                  const farnaaPrices = data.map(item => parseNumber(item.farnaa_price || "0"));
                  const aasoodPrices = data.map(item => parseNumber(item.aasood_price || "0"));
                  const technobusinessPrices = data.map(item => parseNumber(item.technobusiness_price || "0"));
                  const kasraparsPrices = data.map(item => parseNumber(item.kasrapars_price || "0"));

                  const ctx = document.getElementById('priceChartCanvas').getContext('2d');
                  if (window.priceChartInstance) {
                    window.priceChartInstance.destroy();
                  }
                  window.priceChartInstance = new Chart(ctx, {
                    type: 'line',
                    data: {
                      labels: labels,
                      datasets: [
                        {
                          label: 'همراه تل',
                          data: hamrahtelPrices,
                          borderColor: 'rgba(54, 162, 235, 1)',
                          backgroundColor: 'rgba(54, 162, 235, 0.2)',
                          tension: 0.3,
                          fill: false,
                          pointRadius: 0
                        },
                        {
                          label: 'فرنا',
                          data: farnaaPrices,
                          borderColor: 'rgba(255, 159, 64, 1)',
                          backgroundColor: 'rgba(255, 159, 64, 0.2)',
                          tension: 0.3,
                          fill: false,
                          pointRadius: 0
                        },
                        {
                          label: 'اسود',
                          data: aasoodPrices,
                          borderColor: 'rgba(75, 192, 192, 1)',
                          backgroundColor: 'rgba(75, 192, 192, 0.2)',
                          tension: 0.3,
                          fill: false,
                          pointRadius: 0
                        },
                        {
                          label: 'تکنو',
                          data: technobusinessPrices,
                          borderColor: 'rgba(153, 102, 255, 1)',
                          backgroundColor: 'rgba(153, 102, 255, 0.2)',
                          tension: 0.3,
                          fill: false,
                          pointRadius: 0
                        },
                        {
                          label: 'کسری',
                          data: kasraparsPrices,
                          borderColor: 'rgba(255, 99, 132, 1)',
                          backgroundColor: 'rgba(255, 99, 132, 0.2)',
                          tension: 0.3,
                          fill: false,
                          pointRadius: 0
                        }
                      ]
                    },
                    options: {
                      responsive: true,
                      maintainAspectRatio: false,
                      interaction: {
                        mode: 'index',
                        intersect: false,
                      },
                      scales: {
                        x: {
                          display: true,
                          grid: { display: false },
                          ticks: { font: { size: 14, family: "'Tahoma', sans-serif" } }
                        },
                        y: {
                          display: true,
                          grid: { display: true, color: '#e0e0e0' },
                          ticks: {
                            font: { size: 14, family: "'Tahoma', sans-serif" },
                            beginAtZero: true,
                          }
                        }
                      },
                      plugins: {
                        legend: { display: false },
                        tooltip: {
                          enabled: true,
                          backgroundColor: '#333',
                          titleFont: { size: 16, family: "'Tahoma', sans-serif" },
                          bodyFont: { size: 14, family: "'Tahoma', sans-serif" }
                        },
                        title: {
                          display: true,
                          text: 'روند قیمت محصول ' + productModel,
                          font: { size: 20, family: "'Tahoma', sans-serif" }
                        }
                      }
                    }
                  });

                  function generateCustomLegend(chart) {
                    let text = ['<ul class="chart-legend-list list-unstyled d-flex">'];
                    chart.data.datasets.forEach((dataset, i) => {
                      text.push('<li class="me-2">');
                      text.push('<input type="checkbox" data-datasetindex="' + i + '" checked style="vertical-align: middle; margin-right: 5px;">');
                      text.push('<span style="vertical-align: middle;">' + dataset.label + '</span>');
                      text.push('</li>');
                    });
                    text.push('</ul>');
                    return text.join("");
                  }

                  const legendContainer = document.getElementById('chart-legend');
                  legendContainer.innerHTML = generateCustomLegend(window.priceChartInstance);
                  legendContainer.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
                    checkbox.addEventListener('change', function () {
                      const index = this.getAttribute('data-datasetindex');
                      const meta = window.priceChartInstance.getDatasetMeta(index);
                      meta.hidden = !this.checked;
                      window.priceChartInstance.update();
                    });
                  });

                  const myModal = new bootstrap.Modal(document.getElementById('priceChartModal'));
                  myModal.show();
                })
                .catch(error => console.error('Error fetching product history:', error));
            });
          }

          if (card.querySelector(".percent-results")) {
            const percentResults = card.querySelector(".percent-results");
            priceSelector.addEventListener("change", function () {
              let percentContent = "<h6>محاسبات درصدی:</h6>";
              percentLabels.forEach(({ percent, label }) => {
                const percentValue = Math.round(parseNumber(priceSelector.value) * (1 + percent / 100));
                percentContent += `
                  <p>
                    ${label}: 
                    <span class="copyable" data-value="${percentValue}">
                      ${formatNumber(percentValue)}
                    </span>
                  </p>`;
              });
              percentResults.innerHTML = percentContent;
              const copyableElements = percentResults.querySelectorAll(".copyable");
              copyableElements.forEach((element) => {
                element.addEventListener("click", function () {
                  const valueToCopy = this.getAttribute("data-value");
                  navigator.clipboard.writeText(valueToCopy).then(() => {
                    const successMessage = document.createElement("span");
                    successMessage.textContent = "کپی شد!";
                    successMessage.classList.add("copy-success");
                    this.appendChild(successMessage);
                    setTimeout(() => {
                      successMessage.remove();
                    }, 2000);
                  });
                });
              });
            });
            priceSelector.dispatchEvent(new Event("change"));
          }

          if (card.querySelector(".custom-percent-calculation")) {
            const customInputField = card.querySelector(".custom-percent-input");
            function animateCounter(element, start, end, duration) {
              let startTime = null;
              function step(timestamp) {
                if (!startTime) startTime = timestamp;
                const progress = timestamp - startTime;
                const progressRatio = Math.min(progress / duration, 1);
                const current = Math.floor(start + (end - start) * progressRatio);
                element.textContent = formatNumber(current);
                if (progress < duration) {
                  window.requestAnimationFrame(step);
                }
              }
              window.requestAnimationFrame(step);
            }
            function updateCustomCalculation() {
              const selectedPrice = parseNumber(priceSelector.value);
              const customInput = card.querySelector(".custom-percent-input");
              const customResult = card.querySelector(".custom-percent-result");
              const customPercent = parseFloat(customInput.value) || 0;
              const newPrice = Math.round(selectedPrice * (1 + customPercent / 100));
              let previous = parseInt(customResult.getAttribute("data-prev")) || 0;
              animateCounter(customResult, previous, newPrice, 1000);
              customResult.setAttribute("data-prev", newPrice);
            }
            customInputField.addEventListener("input", updateCustomCalculation);
            priceSelector.addEventListener("change", updateCustomCalculation);
          }
        });
      })
      .catch(error => {
        console.error("خطا در دریافت داده‌ها:", error);
        document.getElementById("product-cards").innerHTML = "<p>خطا در بارگذاری اطلاعات.</p>";
      });
  }

  // دریافت دسته‌بندی‌ها و ایجاد دکمه‌های فیلتر
  function fetchCategories() {
    fetch('/api/categories')
      .then(response => response.json())
      .then(categories => {
        const categoryFilterDiv = document.getElementById("category-filter");
        if (categoryFilterDiv) {
          categoryFilterDiv.innerHTML = '';
          const allBtn = document.createElement("button");
          allBtn.classList.add("btn", "btn-outline-secondary", "category-btn", "active");
          allBtn.textContent = "همه";
          allBtn.dataset.category = "";
          categoryFilterDiv.appendChild(allBtn);
          categories.forEach(category => {
            const btn = document.createElement("button");
            btn.classList.add("btn", "btn-outline-secondary", "category-btn");
            btn.textContent = category;
            btn.dataset.category = category;
            btn.style.marginRight = "5px";
            categoryFilterDiv.appendChild(btn);
          });
          const buttons = document.querySelectorAll(".category-btn");
          buttons.forEach(btn => {
            btn.addEventListener("click", function () {
              buttons.forEach(b => b.classList.remove("active"));
              this.classList.add("active");
              const selectedCategory = this.dataset.category;
              fetchProducts(selectedCategory);
            });
          });
        }
      })
      .catch(error => console.error("Error fetching categories:", error));
  }

  // تنظیم جستجو و بروزرسانی
  const searchInput = document.getElementById("search-input");
  const updateButton = document.querySelector(".btn-primary");
  if (searchInput) {
    searchInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        const query = searchInput.value.trim();
        fetchProducts(query);
      }
    });
  }
  if (updateButton) {
    updateButton.addEventListener("click", function () {
      document.getElementById("loading-overlay").style.display = "flex";
      fetch("/update", { method: "POST" })
        .then(response => response.json())
        .then(data => {
          showToastMessage(data.message, data.status === "success");
          if (data.status === "success") {
            fetchProducts();
          }
        })
        .catch(error => {
          console.error("خطا در بروزرسانی:", error);
          showToastMessage("بروزرسانی با خطا مواجه شد!", false);
        })
        .finally(() => {
          document.getElementById("loading-overlay").style.display = "none";
        });
    });
  }

  // به‌روزرسانی قیمت دلار
  function updateDollarPrice() {
    fetch('/api/dollar-price')
      .then(response => response.json())
      .then(data => {
        const priceContainer = document.getElementById('dollar-price');
        if (data.price) {
          let lastStoredPrice = localStorage.getItem("lastDollarPrice");
          let priceChangeDirection = localStorage.getItem("priceChangeDirection");
          if (lastStoredPrice) {
            if (parseInt(data.price) > parseInt(lastStoredPrice)) {
              priceChangeDirection = "up";
              localStorage.setItem("priceChangeDirection", "up");
            } else if (parseInt(data.price) < parseInt(lastStoredPrice)) {
              priceChangeDirection = "down";
              localStorage.setItem("priceChangeDirection", "down");
            }
          } else {
            priceChangeDirection = null;
            localStorage.removeItem("priceChangeDirection");
          }
          localStorage.setItem("lastDollarPrice", data.price);
          let arrowIcon = "";
          if (priceChangeDirection === "up") {
            arrowIcon = '<span style="color: red;">⬆️</span>';
          } else if (priceChangeDirection === "down") {
            arrowIcon = '<span style="color: green;">⬇️</span>';
          }
          priceContainer.innerHTML = parseInt(data.price).toLocaleString() + " تومان " + arrowIcon;
        } else {
          priceContainer.textContent = "خطا در دریافت";
        }
      })
      .catch(error => {
        console.error('خطا در دریافت قیمت دلار:', error);
        document.getElementById('dollar-price').textContent = "خطا";
      });
  }

  updateDollarPrice();
  setInterval(updateDollarPrice, 60000);
  fetchCategories();
  fetchProducts();

  // تنظیم ماشین حساب popover
  const calculatorToggle = document.getElementById('calculator-toggle');
  const calculatorPopover = document.getElementById('calculator-popover');
  const calculatorClose = document.getElementById('calculator-close');
  function updateCalculator() {
    const price = parseFloat(document.getElementById('calc-price').value);
    const percent = parseFloat(document.getElementById('calc-percent').value);
    const resultElem = document.getElementById('calc-result');
    if (isNaN(price) || isNaN(percent)) {
      resultElem.innerText = "";
      return;
    }
    const finalPrice = price * (1 + percent / 100);
    resultElem.innerText = "نتیجه: " + finalPrice.toLocaleString() + " تومان";
  }
  calculatorToggle.addEventListener('click', function(){
    if (calculatorPopover.style.display === "none" || calculatorPopover.style.display === "") {
      calculatorPopover.style.display = "block";
      setTimeout(() => {
        calculatorPopover.style.bottom = "90px";
      }, 10);
    } else {
      calculatorPopover.style.bottom = "-300px";
      setTimeout(() => {
        calculatorPopover.style.display = "none";
      }, 300);
    }
  });
  calculatorClose.addEventListener('click', function(){
    calculatorPopover.style.bottom = "-300px";
    setTimeout(() => {
      calculatorPopover.style.display = "none";
    }, 300);
  });
  document.getElementById('calc-price').addEventListener('input', updateCalculator);
  document.getElementById('calc-percent').addEventListener('input', updateCalculator);

  // دریافت و رندر آمار هفته گذشته در مدال با طراحی بهبود یافته
  function fetchWeeklyStats() {
    fetch('/api/weekly-stats')
      .then(response => response.json())
      .then(data => {
        const updateList = (listId, items, valueField, formatFunc, suffix) => {
          const listEl = document.getElementById(listId);
          listEl.innerHTML = '';
          items.forEach(item => {
            let value = item[valueField];
            if (formatFunc) {
              value = formatFunc(value);
            }
            const li = document.createElement("li");
            li.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
            li.innerHTML = `<span>${item.model}</span><span class="badge bg-secondary">${value} ${suffix || ""}</span>`;
            listEl.appendChild(li);
          });
        };
        updateList("increase-list", data.increase, "delta", (val) => (val > 0 ? "+" + formatNumber(val) : formatNumber(val)), "تومان");
        updateList("decrease-list", data.decrease, "delta", (val) => formatNumber(val), "تومان");
        updateList("volatility-list", data.volatility, "volatility", (val) => formatNumber(val), "تومان");
        updateList("max-avail-list", data.max_availability, "availability", (val) => formatNumber(val), "فروشگاه");
        updateList("min-avail-list", data.min_availability, "availability", (val) => formatNumber(val), "فروشگاه");
      })
      .catch(error => {
        console.error("خطا در دریافت آمار هفتگی:", error);
      });
  }
  const weeklyStatsModal = document.getElementById('weeklyStatsModal');
  weeklyStatsModal.addEventListener('shown.bs.modal', fetchWeeklyStats);

  // تنظیم تاریخ روز با moment
  moment.loadPersian({usePersianDigits: true, dialect: 'persian-modern'});
  const currentDateElem = document.getElementById("current-date");
  if (currentDateElem) {
    currentDateElem.textContent = moment().format('dddd - jD jMMMM jYYYY');
  }
});
