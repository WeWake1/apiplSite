// In script.js

// --- Part 5: Lenis Smooth Scrolling ---
const lenis = new Lenis({
    lerp: 0.07,
    duration: 1.2,
});

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}
requestAnimationFrame(raf);

// --- Part 11: Hamburger Menu Logic ---
const hamburger = document.querySelector('.hamburger-menu');
const nav = document.querySelector('nav');

hamburger.addEventListener('click', () => {
    nav.classList.toggle('is-open');
    hamburger.classList.toggle('is-active');
    document.body.classList.toggle('body-no-scroll');
});

// --- Part 7: On-Scroll Animation Initialization ---
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: false,
    offset: 100,
});

// --- Back to Top Button Logic ---
const backToTopButton = document.getElementById('back-to-top-button');
if (backToTopButton) {
    backToTopButton.addEventListener('click', (e) => {
        e.preventDefault();
        lenis.scrollTo(0, { duration: 1.5 });
    });
}

// --- AOS Refresh on Load ---
window.addEventListener('load', () => {
  AOS.refresh();
});

// --- Products Page Functionality (FINAL, BULLETPROOF VERSION) ---
const productsMain = document.querySelector('.products-main');
if (productsMain) {
    const navItems = document.querySelectorAll('.products-nav-item');
    const indicator = document.querySelector('.products-nav-indicator');
    const swiperContainer = document.querySelector('.products-swiper');

    function updateSwiperHeight(swiperInstance) {
        const activeSlide = swiperInstance.slides[swiperInstance.activeIndex];
        const content = activeSlide ? activeSlide.querySelector('.category-content') : null;
        if (content) {
            swiperContainer.style.height = `${content.scrollHeight}px`;
        }
    }

    function updateIndicator(activeItem) {
        if (!indicator || !activeItem) return;
        indicator.style.left = `${activeItem.offsetLeft}px`;
        indicator.style.width = `${activeItem.offsetWidth}px`;
    }

    function updateNavigation(activeIndex) {
        navItems.forEach(item => item.classList.remove('active'));
        const activeItem = navItems[activeIndex];
        if (activeItem) {
            activeItem.classList.add('active');
            updateIndicator(activeItem);
        }
    }

    const productsSwiper = new Swiper('.products-swiper', {
        speed: 500,
        resistanceRatio: 0.3,
        threshold: 20,
        on: {
            init: function () {
                updateSwiperHeight(this);
            },
            slideChangeTransitionStart: function () {
                updateNavigation(this.activeIndex);
                updateSwiperHeight(this);
            },
        }
    });

    navItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            productsSwiper.slideTo(index);
        });
    });

    // THE DEFINITIVE FIX: Wait for the entire window to be loaded before positioning.
    window.addEventListener('load', () => {
        updateNavigation(productsSwiper.activeIndex);
        // Also re-check height after images are loaded.
        updateSwiperHeight(productsSwiper);
    });

    window.addEventListener('resize', () => {
        updateNavigation(productsSwiper.activeIndex);
    });
}