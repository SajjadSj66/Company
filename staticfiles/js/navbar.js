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