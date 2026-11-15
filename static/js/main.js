/* LoadImpact – UI interactions & animations (no dependencies besides Bootstrap) */
(function () {
  "use strict";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("no-anim");

  /* ---------- Preloader ---------- */
  window.addEventListener("load", function () {
    const pre = document.querySelector(".preloader");
    if (pre) setTimeout(() => pre.classList.add("hide"), 250);
  });
  // Safety net in case some external asset is slow
  setTimeout(() => { const pre = document.querySelector(".preloader"); if (pre) pre.classList.add("hide"); }, 3000);

  document.addEventListener("DOMContentLoaded", function () {
    const nav = document.querySelector(".navbar-li");
    const progress = document.querySelector(".scroll-progress");
    const toTop = document.querySelector(".back-to-top");

    /* ---------- Navbar, progress bar, back-to-top ---------- */
    function setNavHeight() {
      if (nav) document.documentElement.style.setProperty("--nav-h", nav.offsetHeight + "px");
    }
    if (nav) nav.addEventListener("transitionend", setNavHeight);
    window.addEventListener("resize", setNavHeight);

    function onScroll() {
      const y = window.scrollY;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? (y / max) * 100 : 0;
      if (nav && !nav.classList.contains("solid")) nav.classList.toggle("scrolled", y > 40);
      setNavHeight();
      if (progress) progress.style.width = pct + "%";
      if (toTop) {
        toTop.classList.toggle("show", y > 500);
        toTop.style.setProperty("--scroll", pct.toFixed(1));
      }
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    if (toTop) toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

    /* ---------- Scroll reveal ---------- */
    const revealEls = document.querySelectorAll("[data-reveal]");
    revealEls.forEach((el) => { if (el.dataset.delay) el.style.setProperty("--d", el.dataset.delay + "s"); });
    if ("IntersectionObserver" in window && !reduceMotion) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { e.target.classList.add("revealed"); io.unobserve(e.target); }
        });
      }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
      revealEls.forEach((el) => io.observe(el));
    } else {
      revealEls.forEach((el) => el.classList.add("revealed"));
    }

    /* ---------- Animated counters ---------- */
    function animateCount(el) {
      const raw = el.dataset.count !== undefined ? el.dataset.count : el.textContent;
      const match = String(raw).replace(/,/g, "").match(/-?\d+(\.\d+)?/);
      if (!match) return;
      const target = parseFloat(match[0]);
      const decimals = (match[1] || "").length ? match[1].length - 1 : 0;
      const original = el.textContent.trim();
      const prefix = el.dataset.prefix !== undefined ? el.dataset.prefix : original.match(/^[^\d]*/)[0];
      const suffix = el.dataset.suffix !== undefined ? el.dataset.suffix : original.match(/[^\d]*$/)[0];
      const duration = 1600;
      const start = performance.now();
      function frame(now) {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 4);
        const val = target * eased;
        el.textContent = prefix + val.toLocaleString("en-IN", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;
        if (t < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }
    const counters = document.querySelectorAll("[data-count], .count-up");
    if ("IntersectionObserver" in window && !reduceMotion) {
      const cio = new IntersectionObserver((entries) => {
        entries.forEach((e) => { if (e.isIntersecting) { animateCount(e.target); cio.unobserve(e.target); } });
      }, { threshold: 0.4 });
      counters.forEach((c) => cio.observe(c));
    }

    /* ---------- Rotating hero words (typewriter) ---------- */
    document.querySelectorAll("[data-rotate]").forEach((el) => {
      const words = el.dataset.rotate.split("|");
      if (reduceMotion || words.length < 2) return;
      let w = 0, i = words[0].length, deleting = true;
      function tick() {
        const word = words[w];
        el.textContent = word.slice(0, i);
        if (deleting) {
          i--;
          if (i < 0) { deleting = false; w = (w + 1) % words.length; i = 0; return setTimeout(tick, 300); }
          return setTimeout(tick, 55);
        }
        i++;
        if (i > words[w].length) { deleting = true; i = words[w].length; return setTimeout(tick, 2200); }
        setTimeout(tick, 95);
      }
      setTimeout(tick, 2500);
    });

    /* ---------- 3D tilt on hover ---------- */
    if (!reduceMotion && window.matchMedia("(hover: hover)").matches) {
      document.querySelectorAll("[data-tilt]").forEach((card) => {
        card.addEventListener("mousemove", (e) => {
          const r = card.getBoundingClientRect();
          const x = (e.clientX - r.left) / r.width - 0.5;
          const y = (e.clientY - r.top) / r.height - 0.5;
          card.style.transform = `perspective(900px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) translateY(-6px)`;
        });
        card.addEventListener("mouseleave", () => { card.style.transform = ""; });
      });

      /* Parallax for hero visual */
      const parallax = document.querySelectorAll("[data-parallax]");
      if (parallax.length) {
        window.addEventListener("mousemove", (e) => {
          const x = e.clientX / window.innerWidth - 0.5;
          const y = e.clientY / window.innerHeight - 0.5;
          parallax.forEach((el) => {
            const depth = parseFloat(el.dataset.parallax) || 20;
            el.style.translate = `${x * depth}px ${y * depth}px`;
          });
        });
      }
    }

    /* ---------- Progress rings & bars animate in ---------- */
    setTimeout(() => {
      document.querySelectorAll(".ring[data-p]").forEach((r) => r.style.setProperty("--p", r.dataset.p));
      document.querySelectorAll(".progress-bar[data-width]").forEach((b) => (b.style.width = b.dataset.width + "%"));
    }, 400);

    /* ---------- BMI calculator ---------- */
    const bmiForm = document.getElementById("bmiForm");
    if (bmiForm) {
      bmiForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const h = parseFloat(bmiForm.height.value) / 100;
        const w = parseFloat(bmiForm.weight.value);
        const out = document.getElementById("bmiValue");
        const cat = document.getElementById("bmiCategory");
        const tip = document.getElementById("bmiTip");
        const pointer = document.getElementById("bmiPointer");
        if (!h || !w || h <= 0) { cat.textContent = "Please enter a valid height and weight."; return; }
        const bmi = w / (h * h);
        let label, advice, color;
        if (bmi < 18.5) { label = "Underweight"; color = "#3b82f6"; advice = "Our strength & nutrition coaching can help you build healthy mass."; }
        else if (bmi < 25) { label = "Healthy weight"; color = "#22c55e"; advice = "Great! Keep it up with a balanced mix of strength and cardio."; }
        else if (bmi < 30) { label = "Overweight"; color = "#eab308"; advice = "HIIT, Zumba and a guided plan can help you reach your goal faster."; }
        else { label = "Obese"; color = "#ef4444"; advice = "Start safely with a personal trainer and a structured program."; }
        out.textContent = bmi.toFixed(1);
        out.style.color = color;
        cat.textContent = label;
        tip.textContent = advice;
        const pct = Math.max(0, Math.min(100, ((bmi - 15) / (40 - 15)) * 100));
        pointer.style.left = pct + "%";
      });
    }

    /* ---------- Schedule: open today's tab ---------- */
    const todayTab = document.querySelector("[data-today-tab]");
    if (todayTab && window.bootstrap) bootstrap.Tab.getOrCreateInstance(todayTab).show();

    /* ---------- Password show/hide ---------- */
    document.querySelectorAll('input[type="password"]').forEach((input) => {
      const wrap = document.createElement("div");
      wrap.className = "pw-wrap";
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pw-toggle";
      btn.setAttribute("aria-label", "Show password");
      btn.innerHTML = '<i class="bi bi-eye"></i>';
      btn.addEventListener("click", () => {
        const show = input.type === "password";
        input.type = show ? "text" : "password";
        btn.innerHTML = show ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
      });
      wrap.appendChild(btn);
    });

    /* ---------- Flash messages auto-hide ---------- */
    document.querySelectorAll(".alert-dismissible.auto-hide").forEach((el) => {
      setTimeout(() => { if (window.bootstrap) bootstrap.Alert.getOrCreateInstance(el).close(); }, 5000);
    });

    /* ---------- Confirm dialogs ---------- */
    document.querySelectorAll("form[data-confirm]").forEach((form) => {
      form.addEventListener("submit", (e) => { if (!window.confirm(form.dataset.confirm)) e.preventDefault(); });
    });

    /* ---------- Close mobile menu after clicking a link ---------- */
    document.querySelectorAll(".navbar-collapse .nav-link").forEach((link) => {
      link.addEventListener("click", () => {
        const menu = document.querySelector(".navbar-collapse.show");
        if (menu && window.bootstrap) bootstrap.Collapse.getOrCreateInstance(menu).hide();
      });
    });
  });
})();
