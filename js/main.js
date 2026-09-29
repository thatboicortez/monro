(function () {
  "use strict";

  /* ---------- Taal ---------- */
  var is404 = document.body.getAttribute("data-page") === "404";
  // Laatst bekeken taal onthouden, zodat de 404-pagina in dezelfde taal verschijnt.
  if (!is404) {
    try { localStorage.setItem("monro-lang", document.documentElement.lang); } catch (e) {}
  }
  document.querySelectorAll(".lang__link").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var target = a.getAttribute("data-switch-lang");
      if (target) {
        // 404: zelfde pagina, andere taal (404.html kiest de taal bij het laden)
        e.preventDefault();
        try { sessionStorage.setItem("monro-404:" + location.pathname, target); } catch (err) {}
        location.reload();
      } else if (location.search || location.hash) {
        // Gekozen behandeling (?behandeling=...) en anker (#...) meenemen naar de andere taal
        e.preventDefault();
        location.href = a.getAttribute("href") + location.search + location.hash;
      }
    });
  });

  /* ---------- Header: rand zodra de pagina gescrold is ---------- */
  var header = document.getElementById("header");
  var sentinel = document.querySelector(".header-sentinel");
  if (header && sentinel && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      header.classList.toggle("is-scrolled", !entries[0].isIntersecting);
    }).observe(sentinel);
  }

  /* ---------- Canvas-kleur: donker zodra de footer zichtbaar is ---------- */
  var footer = document.querySelector(".footer");
  if (footer && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      document.documentElement.classList.toggle("at-footer", entries[0].isIntersecting);
    }).observe(footer);
  }

  /* ---------- Mobiel menu ---------- */
  var burger = document.getElementById("burger");
  var menu = document.getElementById("mobile-menu");
  function setMenu(open) {
    if (!burger || !menu) return;
    burger.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(function () { menu.classList.add("is-open"); });
    } else {
      menu.classList.remove("is-open");
      setTimeout(function () { if (!menu.classList.contains("is-open")) menu.hidden = true; }, 350);
    }
  }
  if (burger) {
    burger.addEventListener("click", function () { setMenu(burger.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    window.matchMedia("(min-width: 1081px)").addEventListener("change", function (m) { if (m.matches) setMenu(false); });
  }

  /* ---------- Reveal bij scrollen ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        var siblings = Array.prototype.filter.call(el.parentNode.children, function (c) { return c.classList.contains("reveal"); });
        el.style.transitionDelay = Math.min(siblings.indexOf(el), 4) * 70 + "ms";
        el.classList.add("is-in");
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -40px 0px", threshold: 0.01 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Afspraakformulier ----------
   * Geen backend: de aanvraag opent als kant-en-klaar bericht in WhatsApp
   * (of, zonder WhatsApp-nummer, in het e-mailprogramma). De klant verstuurt zelf.
   */
  var form = document.getElementById("booking-form");
  if (!form) return;

  var select = form.elements.service;
  var pre = new URLSearchParams(location.search).get("behandeling");
  if (pre && select.querySelector('option[value="' + pre + '"]')) select.value = pre;

  var errorEl = document.getElementById("form-error");

  function label(name) {
    var el = form.querySelector('label[for="f-' + name + '"]');
    return el ? el.textContent : name;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var f = form.elements;
    var name = f.name.value.trim();
    var phone = f.phone.value.trim();

    // Telefoon is optioneel: via WhatsApp ziet Tetiana het nummer toch al.
    form.querySelectorAll(".is-invalid").forEach(function (el) { el.classList.remove("is-invalid"); });
    var ok = true;
    if (!name) { f.name.closest(".field").classList.add("is-invalid"); ok = false; }
    if (!f.consent.checked) { f.consent.closest(".check").classList.add("is-invalid"); ok = false; }
    errorEl.hidden = ok;
    if (!ok) return;

    var subject = form.getAttribute("data-subject");
    var lines = [
      subject,
      "",
      label("name") + ": " + name,
      phone ? label("phone") + ": " + phone : null,
      label("service") + ": " + select.options[select.selectedIndex].text,
      f.message.value.trim() ? "\n" + f.message.value.trim() : null
    ].filter(function (l) { return l !== null; });
    var body = lines.join("\n");

    var wa = form.getAttribute("data-whatsapp");
    if (wa) {
      // Gewone navigatie i.p.v. window.open: popupblokkers en in-app browsers (Instagram) laten dit altijd toe.
      location.href = "https://wa.me/" + wa + "?text=" + encodeURIComponent(body);
    } else {
      location.href = "mailto:" + form.getAttribute("data-email") + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    }
  });
})();
