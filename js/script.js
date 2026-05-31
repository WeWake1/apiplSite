/* ============================================================
   AMBICA PATTERNS — site interactions (no external JS deps)
   ============================================================ */
(function () {
  "use strict";

  /* ---------- Sticky header + scroll progress + back-to-top ---------- */
  const header = document.querySelector(".site-header");
  const progress = document.querySelector(".scroll-progress");
  const toTop = document.querySelector(".back-to-top");

  function onScroll() {
    const y = window.scrollY;
    if (header) header.classList.toggle("scrolled", y > 30);
    if (progress) {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (h > 0 ? (y / h) * 100 : 0) + "%";
    }
    if (toTop) toTop.classList.toggle("show", y > 500);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener("click", () =>
      window.scrollTo({ top: 0, behavior: "smooth" })
    );
  }

  /* ---------- Mobile navigation ---------- */
  const hamburger = document.querySelector(".hamburger");
  const nav = document.querySelector(".nav");
  if (hamburger && nav) {
    const toggle = (force) => {
      const isOpen =
        typeof force === "boolean"
          ? force
          : !nav.classList.contains("mobile-open");
      nav.classList.toggle("mobile-open", isOpen);
      hamburger.classList.toggle("open", isOpen);
      document.body.style.overflow = isOpen ? "hidden" : "";
      hamburger.setAttribute("aria-expanded", String(isOpen));
    };
    hamburger.addEventListener("click", () => toggle());
    nav.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => toggle(false))
    );
  }

  /* ---------- Scroll reveal (IntersectionObserver) ---------- */
  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("in"));
  }

  /* ---------- Animated counters ---------- */
  const counters = document.querySelectorAll("[data-count]");
  const animateCount = (el) => {
    const target = parseFloat(el.dataset.count);
    const dur = 1600;
    const start = performance.now();
    const step = (now) => {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased).toLocaleString();
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString();
    };
    requestAnimationFrame(step);
  };
  if ("IntersectionObserver" in window && counters.length) {
    const cio = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            animateCount(e.target);
            cio.unobserve(e.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    counters.forEach((c) => cio.observe(c));
  } else {
    counters.forEach((c) => (c.textContent = c.dataset.count));
  }

  /* ---------- Lazy-load <model-viewer> only when near viewport ---------- */
  const stages = document.querySelectorAll("[data-model-stage]");
  if (stages.length) {
    let loaded = false;
    const loadMV = () => {
      if (loaded) return;
      loaded = true;
      const s = document.createElement("script");
      s.type = "module";
      s.src =
        "https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js";
      document.head.appendChild(s);
    };
    if ("IntersectionObserver" in window) {
      const mio = new IntersectionObserver(
        (entries) => {
          if (entries.some((e) => e.isIntersecting)) {
            loadMV();
            mio.disconnect();
          }
        },
        { rootMargin: "400px" }
      );
      stages.forEach((s) => mio.observe(s));
    } else {
      loadMV();
    }
  }

  /* ---------- Product tabs ---------- */
  const tabBtns = document.querySelectorAll(".tab-btn");
  const panels = document.querySelectorAll(".tab-panel");
  if (tabBtns.length && panels.length) {
    const activate = (id) => {
      if (!document.getElementById(id)) return;
      tabBtns.forEach((b) => b.classList.toggle("active", b.dataset.tab === id));
      panels.forEach((p) => p.classList.toggle("active", p.id === id));
    };
    tabBtns.forEach((b) =>
      b.addEventListener("click", () => activate(b.dataset.tab))
    );
    const hash = window.location.hash.replace("#", "");
    if (hash) activate(hash);
  }

  /* ---------- Contact form (graceful fallback to mailto) ---------- */
  const form = document.querySelector("[data-contact-form]");
  if (form) {
    form.addEventListener("submit", (e) => {
      const action = form.getAttribute("action") || "";
      if (action.includes("your-form-id") || action === "") {
        e.preventDefault();
        const fd = new FormData(form);
        const subject = encodeURIComponent(
          "Pallet enquiry — " + (fd.get("name") || "Website")
        );
        const body = encodeURIComponent(
          `Name: ${fd.get("name") || ""}\nCompany: ${fd.get("company") || ""}\n` +
            `Email: ${fd.get("email") || ""}\nPhone: ${fd.get("phone") || ""}\n` +
            `Product: ${fd.get("product") || ""}\n\n${fd.get("message") || ""}`
        );
        window.location.href = `mailto:sales@ambicapatterns.in?subject=${subject}&body=${body}`;
        const btn = form.querySelector('[type="submit"]');
        if (btn) {
          const t = btn.textContent;
          btn.textContent = "Opening your email…";
          setTimeout(() => (btn.textContent = t), 3000);
        }
      }
    });
  }

  /* ---------- Year in footer ---------- */
  document.querySelectorAll("[data-year]").forEach(
    (el) => (el.textContent = new Date().getFullYear())
  );
})();
