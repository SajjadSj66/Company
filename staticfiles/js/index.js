// تابع باز و بسته کردن دراپ‌منو
    		function toggleDropdown(triggerId, dropdownId) {
      			var trigger = document.getElementById(triggerId);
      			var dropdown = document.getElementById(dropdownId);
      			
      			if(trigger && dropdown) {
        				trigger.addEventListener("click", function(e) {
          					e.stopPropagation();
          					
          					// بستن همه دراپ‌منوهای دیگر
          					document.querySelectorAll('.dropdown-content').forEach(function(el) {
            						if(el.id !== dropdownId) {
              							el.style.display = 'none';
            						}
          					});
          					
          					// باز و بسته کردن دراپ‌منو فعلی
          					if(dropdown.style.display === 'flex') {
            						dropdown.style.display = 'none';
          					} else {
            						dropdown.style.display = 'flex';
          					}
        				});
      			}
    		}
    		
    		// بستن دراپ‌منو با کلیک خارج از آن
    		document.addEventListener("click", function() {
      			document.querySelectorAll('.dropdown-content').forEach(function(el) {
        				el.style.display = 'none';
      			});
    		});
    		
    		// جلوگیری از بسته شدن دراپ‌منو با کلیک روی خودش
    		document.querySelectorAll('.dropdown-content').forEach(function(el) {
      			el.addEventListener("click", function(e) {
        				e.stopPropagation();
      			});
    		});
    		
    		// راه‌اندازی دراپ‌منوها
    		toggleDropdown('frameContainer', 'blogDropdown');
    		toggleDropdown('frameContainer1', 'academyDropdown');
    		toggleDropdown('frameContainer2', 'servicesDropdown');


 		// saghar js
      (function () {
        const carousel = document.getElementById("carousel-unique");
        const prevBtn = document.getElementById("prevBtn-unique");
        const nextBtn = document.getElementById("nextBtn-unique");

        function getStep() {
          const card = carousel.querySelector(".project-card-unique");
          if (!card) return 400;
          const cardWidth = card.getBoundingClientRect().width;
          const gap = 22;
          return cardWidth + gap;
        }

        nextBtn.addEventListener("click", () => {
          carousel.scrollBy({ left: -getStep(), behavior: "smooth" });
        });

        prevBtn.addEventListener("click", () => {
          carousel.scrollBy({ left: getStep(), behavior: "smooth" });
        });

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



	//   salma js faq
        // تابع مدیریت آکاردئون با قابلیت بستن آیتم‌های دیگر
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
            // اگر باز بود که با بسته شدن همه آیتم‌ها، خودش هم بسته میشه
        }