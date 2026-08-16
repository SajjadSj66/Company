		// ============================================================
		// تابع باز و بسته کردن دراپ‌منو
		// ============================================================
		function toggleDropdown(triggerId, dropdownId, name) {
			var trigger = document.getElementById(triggerId);
			var dropdown = document.getElementById(dropdownId);

			if (trigger && dropdown) {
				trigger.addEventListener("click", function (e) {
					e.stopPropagation();

					// بستن همه دراپ‌منوهای دیگر
					document.querySelectorAll('.dropdown-content').forEach(function (el) {
						if (el.id !== dropdownId) {
							el.style.display = 'none';
						}
					});

					// باز و بسته کردن دراپ‌منو فعلی
					if (dropdown.style.display === 'flex') {
						dropdown.style.display = 'none';

						// ریست کردن متن backBtnSpan هنگام بستن دراپ‌منو
						var backBtnSpan = document.getElementById('mobileBackBtnSpan');
						if (backBtnSpan) {
							backBtnSpan.textContent = 'بازگشت به منو';
						}

						// نمایش لوگو و مخفی کردن دکمه بازگشت
						var logoDiv = document.getElementById('sidebar-logo-div');
						var backBtn = document.getElementById('mobileBackBtn');
						if (logoDiv) logoDiv.style.display = 'flex';
						if (backBtn) backBtn.style.display = 'none';
					} else {
						dropdown.style.display = 'flex';
						// تغییر متن backBtnSpan به نام ساب‌منو
						var backBtnSpan = document.getElementById('mobileBackBtnSpan');
						if (backBtnSpan && name) {
							backBtnSpan.textContent = name;
						}

						// مخفی کردن لوگو و نمایش دکمه بازگشت
						var logoDiv = document.getElementById('sidebar-logo-div');
						var backBtn = document.getElementById('mobileBackBtn');
						if (logoDiv) logoDiv.style.display = 'none';
						if (backBtn) backBtn.style.display = 'flex';
					}
				});
			}
		}

		// بستن دراپ‌منو با کلیک خارج از آن
		document.addEventListener("click", function () {
			document.querySelectorAll('.dropdown-content').forEach(function (el) {
				el.style.display = 'none';
			});
			// ریست کردن متن backBtnSpan
			var backBtnSpan = document.getElementById('mobileBackBtnSpan');
			if (backBtnSpan) {
				backBtnSpan.textContent = 'بازگشت به منو';
			}

			// نمایش لوگو و مخفی کردن دکمه بازگشت
			var logoDiv = document.getElementById('sidebar-logo-div');
			var backBtn = document.getElementById('mobileBackBtn');
			if (logoDiv) logoDiv.style.display = 'flex';
			if (backBtn) backBtn.style.display = 'none';
		});

		// جلوگیری از بسته شدن دراپ‌منو با کلیک روی خودش
		document.querySelectorAll('.dropdown-content').forEach(function (el) {
			el.addEventListener("click", function (e) {
				e.stopPropagation();
			});
		});

		// راه‌اندازی دراپ‌منوها با نام‌های مناسب
		toggleDropdown('frameContainer1', 'academyDropdown', 'آکادمی');
		toggleDropdown('frameContainer2', 'servicesDropdown', 'خدمات ما');

		// ============================================================
		// کاروسل (بدون تغییر)
		// ============================================================
		(function () {
			const carousel = document.getElementById("carousel-unique");
			if (!carousel) return;

			const prevBtn = document.getElementById("prevBtn-unique");
			const nextBtn = document.getElementById("nextBtn-unique");

			function getStep() {
				const card = carousel.querySelector(".project-card-unique");
				if (!card) return 400;
				const cardWidth = card.getBoundingClientRect().width;
				const gap = 22;
				return cardWidth + gap;
			}

			if (nextBtn) {
				nextBtn.addEventListener("click", () => {
					carousel.scrollBy({ left: -getStep(), behavior: "smooth" });
				});
			}

			if (prevBtn) {
				prevBtn.addEventListener("click", () => {
					carousel.scrollBy({ left: getStep(), behavior: "smooth" });
				});
			}

			let isDown = false;
			let startX = 0;
			let startScroll = 0;
			let moved = false;

			carousel.addEventListener("mousedown", (e) => {
				isDown = true;
				moved = false;
				startX = e.pageX;
				startScroll = carousel.scrollLeft;
				carousel.classList.add("dragging");
			});

			window.addEventListener("mouseup", () => {
				isDown = false;
				carousel.classList.remove("dragging");
			});

			window.addEventListener("mousemove", (e) => {
				if (!isDown) return;
				e.preventDefault();
				const dx = e.pageX - startX;
				if (Math.abs(dx) > 3) moved = true;
				carousel.scrollLeft = startScroll - dx;
			});

			carousel.addEventListener(
				"click",
				(e) => {
					if (moved) {
						e.preventDefault();
						e.stopPropagation();
					}
				},
				true,
			);
		})();

		// ============================================================
		// FAQ آکاردئون
		// ============================================================
		function handleAccordionToggle(headerRow) {
			const currentItem = headerRow.closest('.accordion-item');
			const allItems = document.querySelectorAll('.accordion-item');
			const isCurrentlyOpen = currentItem.classList.contains('open');

			// اول همه آیتم‌ها رو می‌بندیم
			allItems.forEach(item => {
				item.classList.remove('open');
				item.classList.add('closed');
				item.dataset.open = 'false';
				const symbol = item.querySelector('.toggle-symbol');
				if (symbol) {
					symbol.textContent = '+';
				}
			});

			// اگر آیتم کلیک‌شده قبلاً بسته بود، بازش می‌کنیم
			if (!isCurrentlyOpen) {
				currentItem.classList.remove('closed');
				currentItem.classList.add('open');
				currentItem.dataset.open = 'true';
				const symbol = currentItem.querySelector('.toggle-symbol');
				if (symbol) {
					symbol.textContent = '−';
				}
			}
		}

		// ============================================================
		// نویگیشن موبایل — با قابلیت تغییر متن backBtn و نمایش/مخفی کردن
		// ============================================================
		(function () {
			var bar = document.getElementById('mobileNavbar');
			if (!bar) return;

			var hamburger = document.getElementById('mobileHamburger');
			var overlay = document.getElementById('mobileOverlay');
			var sidebar = document.getElementById('mobileSidebar');
			var backBtn = document.getElementById('mobileBackBtn');
			var backBtnSpan = document.getElementById('mobileBackBtnSpan');
			var logoDiv = document.getElementById('sidebar-logo-div');
			var triggers = bar.querySelectorAll('[data-mobile-trigger]');

			// در ابتدا دکمه بازگشت مخفی و لوگو نمایش داده شود
			if (logoDiv) logoDiv.style.display = 'flex';
			if (backBtn) backBtn.style.display = 'none';

			function openSidebar() {
				sidebar.classList.add('is-open');
				overlay.classList.add('is-active');
				if (hamburger) {
					hamburger.classList.add('is-active');
					hamburger.setAttribute('aria-expanded', 'true');
				}
				document.body.classList.add('mobile-nav-lock');

				// در حالت عادی (زیرمنو بسته) لوگو نمایش داده شود
				if (logoDiv) logoDiv.style.display = 'flex';
				if (backBtn) backBtn.style.display = 'none';
			}

			function closeSidebar() {
				sidebar.classList.remove('is-open');
				overlay.classList.remove('is-active');
				if (hamburger) {
					hamburger.classList.remove('is-active');
					hamburger.setAttribute('aria-expanded', 'false');
				}
				document.body.classList.remove('mobile-nav-lock');
				closeSubmenu();
				// ریست کردن متن backBtnSpan
				if (backBtnSpan) {
					backBtnSpan.textContent = 'بازگشت به منو';
				}
				// نمایش لوگو و مخفی کردن دکمه بازگشت
				if (logoDiv) logoDiv.style.display = 'flex';
				if (backBtn) backBtn.style.display = 'none';
			}

			function toggleSidebar() {
				if (sidebar.classList.contains('is-open')) {
					closeSidebar();
				} else {
					openSidebar();
				}
			}

			function closeSubmenu() {
				sidebar.classList.remove('has-submenu-open');
				bar.querySelectorAll('.mobile-navbar__submenu').forEach(function (s) {
					s.classList.remove('is-open');
				});
				// ریست کردن متن backBtnSpan
				if (backBtnSpan) {
					backBtnSpan.textContent = 'بازگشت به منو';
				}
				// نمایش لوگو و مخفی کردن دکمه بازگشت
				if (logoDiv) logoDiv.style.display = 'flex';
				if (backBtn) backBtn.style.display = 'none';
			}

			function openSubmenu(key) {
				// پیدا کردن نام ساب‌منو از المان trigger
				var triggerElement = bar.querySelector('[data-mobile-trigger="' + key + '"]');
				var menuName = 'بازگشت به منو';

				if (triggerElement) {
					// گرفتن متن از span داخل trigger
					var spanElement = triggerElement.querySelector('span');
					if (spanElement) {
						menuName = spanElement.textContent.trim();
					}
				}

				bar.querySelectorAll('.mobile-navbar__submenu').forEach(function (s) {
					s.classList.toggle('is-open', s.getAttribute('data-mobile-submenu') === key);
				});
				sidebar.classList.add('has-submenu-open');

				// تغییر متن backBtnSpan به نام ساب‌منو
				if (backBtnSpan) {
					backBtnSpan.textContent = menuName;
				}

				// مخفی کردن لوگو و نمایش دکمه بازگشت
				if (logoDiv) logoDiv.style.display = 'none';
				if (backBtn) backBtn.style.display = 'flex';
			}

			// رویدادها
			if (hamburger) hamburger.addEventListener('click', toggleSidebar);
			if (overlay) overlay.addEventListener('click', closeSidebar);
			if (backBtn) {
				backBtn.addEventListener('click', function (e) {
					e.stopPropagation();
					closeSubmenu();
				});
			}

			triggers.forEach(function (trigger) {
				trigger.addEventListener('click', function (e) {
					e.stopPropagation();
					var key = trigger.getAttribute('data-mobile-trigger');
					openSubmenu(key);
				});
			});

			// بستن سایدبار با کلیک روی آیتم‌های منو
			bar.querySelectorAll('.mobile-navbar__item:not([data-mobile-trigger]), .mobile-navbar__submenu-item').forEach(function (link) {
				link.addEventListener('click', function (e) {
					// اگر لینک واقعی است و href دارد
					if (this.getAttribute('href')) {
						closeSidebar();
					} else {
						closeSidebar();
					}
				});
			});

			// بستن با کلید Escape
			document.addEventListener('keydown', function (e) {
				if (e.key === 'Escape') closeSidebar();
			});

			// بستن سایدبار هنگام تغییر اندازه پنجره به دسکتاپ
			window.addEventListener('resize', function () {
				if (window.innerWidth > 1330) {
					closeSidebar();
				}
			});

			// جلوگیری از بسته شدن هنگام کلیک داخل سایدبار
			if (sidebar) {
				sidebar.addEventListener('click', function (e) {
					e.stopPropagation();
				});
			}

		})();