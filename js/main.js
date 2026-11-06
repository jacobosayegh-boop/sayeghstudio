/* =====================================================
   SAYEGH STUDIO — LANDING INMERSIVA — JS MODULAR
   ===================================================== */

/* ── HERO VIDEO AUTOPLAY (some mobile webviews ignore the autoplay attribute) ── */
const heroVideo = document.querySelector('.hero-video');
if (heroVideo) {
  const tryPlayHeroVideo = () => heroVideo.play().catch(() => {});
  tryPlayHeroVideo();
  ['click', 'touchstart', 'scroll'].forEach((evt) => {
    document.addEventListener(evt, tryPlayHeroVideo, { once: true, passive: true });
  });
}

/* ── MANIFIESTO VIDEO AUTOPLAY (same mobile webview caveat as the hero video) ── */
const manifiestoVideoEl = document.querySelector('.manifiesto-video-media');
if (manifiestoVideoEl) {
  const tryPlayManifiestoVideo = () => manifiestoVideoEl.play().catch(() => {});
  tryPlayManifiestoVideo();
  ['click', 'touchstart', 'scroll'].forEach((evt) => {
    document.addEventListener(evt, tryPlayManifiestoVideo, { once: true, passive: true });
  });
}

/* ── NAV SCROLL (batched via rAF) ── */
const nav = document.querySelector('.nav');
const heroMediaEl = document.querySelector('.hero-media');
let scrollTicking = false;

function onScrollFrame() {
  const scrollY = window.scrollY;
  nav?.classList.toggle('scrolled', scrollY > 40);
  if (heroMediaEl && scrollY < window.innerHeight) {
    heroMediaEl.style.transform = `translateY(${scrollY * 0.3}px)`;
  }
  scrollTicking = false;
}

window.addEventListener('scroll', () => {
  if (!scrollTicking) {
    requestAnimationFrame(onScrollFrame);
    scrollTicking = true;
  }
}, { passive: true });

/* ── REVEAL ON SCROLL (IntersectionObserver) ── */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -48px 0px' });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

/* ── COUNTER ANIMATION ── */
function animateCounter(el, target, suffix = '', duration = 1800) {
  const start = performance.now();
  const update = (now) => {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(eased * target) + suffix;
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.target, 10);
      const suffix = el.dataset.suffix || '';
      animateCounter(el, target, suffix);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-counter]').forEach(el => counterObserver.observe(el));

/* ── AUDIENCIAS TABS ── */
const tabs = document.querySelectorAll('.audiencia-tab');
const panels = document.querySelectorAll('.audiencia-panel');

tabs.forEach((tab, i) => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    panels.forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    panels[i]?.classList.add('active');
  });
});

/* ── OBRAS EN EXPANSIÓN (módulo dinámico, data-driven) ── */
const progressObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const bar = entry.target.querySelector('.expansion-progress-bar');
      if (bar) {
        const width = bar.dataset.width || '50%';
        setTimeout(() => { bar.style.width = width; }, 200);
      }
      progressObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

const expansionGrid = document.getElementById('expansion-grid');
if (expansionGrid) {
  fetch(expansionGrid.dataset.source)
    .then(res => res.json())
    .then(proyectos => {
      expansionGrid.innerHTML = proyectos.map((p, i) => `
        <div class="expansion-card reveal reveal-delay-${Math.min(i + 1, 4)}">
          <div class="expansion-status"><span class="expansion-dot"></span>${p.status}</div>
          <h4>${p.title}</h4>
          <p>${p.description}</p>
          <div class="expansion-progress"><div class="expansion-progress-bar" data-width="${p.progress}%" style="width:0%"></div></div>
          <p style="font-size:12px;color:var(--muted);margin-top:8px;margin-bottom:0;">${p.note}</p>
        </div>
      `).join('');
      expansionGrid.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
      expansionGrid.querySelectorAll('.expansion-card').forEach(el => progressObserver.observe(el));
    })
    .catch(() => {
      expansionGrid.innerHTML = `<p style="color:var(--muted);">No se pudieron cargar los proyectos en expansión. <a href="https://via.sayeghstudio.com" style="color:var(--brass);">Consultar directamente</a>.</p>`;
    });
}

/* ── MOBILE HAMBURGER + FOCUS TRAP ── */
const hamburger = document.querySelector('.nav-hamburger');
const mobileMenu = document.querySelector('.nav-links');
let menuOpen = false;
let pendingClickListenerRAF = null; // Track rAF handle to prevent race condition

function getFocusableElements(container) {
  const focusableSelectors = 'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])';
  return Array.from(container.querySelectorAll(focusableSelectors))
    .filter(el => el.offsetParent !== null && !el.disabled);
}

function initMenuFocusTrap(overlay) {
  const focusableElements = getFocusableElements(overlay);
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  if (firstElement) {
    firstElement.focus();
  }

  const closeMenu = () => {
    overlay.remove();
    menuOpen = false;
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.focus();
    document.body.style.overflow = '';
    // Cancel pending rAF if close happens before click listener registers
    if (pendingClickListenerRAF !== null) {
      cancelAnimationFrame(pendingClickListenerRAF);
      pendingClickListenerRAF = null;
    }
    document.removeEventListener('keydown', handleKeyDown);
    document.removeEventListener('click', handleClickOutside);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    } else if (e.key === 'Escape') {
      closeMenu();
    }
  };

  const handleClickOutside = (e) => {
    if (!overlay.contains(e.target) && !e.target?.closest('.nav-hamburger')) {
      closeMenu();
    }
  };

  document.addEventListener('keydown', handleKeyDown);
  // Defer click listener registration past the opening click dispatch to avoid immediate re-trigger
  // Store rAF handle to allow cancellation if menu closes before rAF fires
  pendingClickListenerRAF = requestAnimationFrame(() => {
    document.addEventListener('click', handleClickOutside);
    pendingClickListenerRAF = null;
  });
}

hamburger?.addEventListener('click', () => {
  menuOpen = !menuOpen;
  hamburger.classList.toggle('open', menuOpen);
  hamburger.setAttribute('aria-expanded', String(menuOpen));
  if (menuOpen) {
    const overlay = document.createElement('div');
    overlay.id = 'mobile-nav-overlay';
    overlay.style.cssText = `
      position:fixed;inset:0;top:64px;background:var(--overlay-crema);
      backdrop-filter:blur(16px);z-index:99;display:flex;flex-direction:column;
      align-items:center;justify-content:center;gap:24px;
    `;
    const links = document.querySelectorAll('.nav-links a');
    links.forEach(link => {
      const a = link.cloneNode(true);
      a.style.cssText = 'font-family:var(--font-display);font-size:20px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;color:var(--ink);';
      a.addEventListener('click', () => {
        overlay.remove();
        menuOpen = false;
        hamburger.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        // Ensure overflow is restored and listeners are cleaned (same as closeMenu in trap)
        document.body.style.overflow = '';
        if (pendingClickListenerRAF !== null) {
          cancelAnimationFrame(pendingClickListenerRAF);
          pendingClickListenerRAF = null;
        }
      });
      overlay.appendChild(a);
    });
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
    initMenuFocusTrap(overlay);
  } else {
    document.getElementById('mobile-nav-overlay')?.remove();
    document.body.style.overflow = '';
  }
});

/* ── SMOOTH ANCHOR SCROLL ── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const id = anchor.getAttribute('href');
    if (!id || id === '#') return;
    const target = document.querySelector(id);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

/* ── LEGAL MODALS (Aviso de Privacidad / Términos y Condiciones) ── */
const modalHandlers = new WeakMap(); // Use WeakMap to track handlers and auto-GC when modal is removed
const modalOpeners = new WeakMap(); // Track which button opened each modal

function closeLegalModal(modal, triggerElement) {
  modal.classList.remove('open');
  modal.removeAttribute('aria-hidden');
  document.body.style.overflow = '';

  // Clean up event listeners for this modal
  if (modalHandlers.has(modal)) {
    const { keydownHandler, clickHandler } = modalHandlers.get(modal);
    document.removeEventListener('keydown', keydownHandler);
    modal.removeEventListener('mousedown', clickHandler.mousedownHandler);
    modal.removeEventListener('click', clickHandler.clickHandler);
    modalHandlers.delete(modal);
  }

  if (triggerElement && typeof triggerElement.focus === 'function') {
    triggerElement.focus();
  }
}

function initModalFocusTrap(modal, triggerElement) {
  // Prevent re-entrant opens from accumulating handlers
  if (modalHandlers.has(modal)) return;

  // If modal was externally closed before init, skip (guard against external DOM manipulation)
  if (!modal.classList.contains('open')) return;

  const focusableSelectors = 'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])';
  const focusableElements = Array.from(modal.querySelectorAll(focusableSelectors))
    .filter(el => el.offsetParent !== null && !el.disabled);

  if (focusableElements.length === 0) return;

  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];
  const contentContainer = modal.querySelector('.legal-modal-content');

  // Focus content container if present (makes scrollable content accessible), else first element
  if (contentContainer) {
    contentContainer.setAttribute('tabindex', '-1');
    contentContainer.focus();
  } else if (firstElement && typeof firstElement.focus === 'function') {
    firstElement.focus();
  }

  const handleModalKeydown = (e) => {
    // Only process if modal is still open
    if (!modal.classList.contains('open')) {
      return;
    }

    if (e.key === 'Tab' && !e.isComposing) {
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          if (lastElement && typeof lastElement.focus === 'function') {
            lastElement.focus();
          }
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          if (firstElement && typeof firstElement.focus === 'function') {
            firstElement.focus();
          }
        }
      }
    } else if (e.key === 'Escape' && !e.isComposing) {
      e.preventDefault();
      closeLegalModal(modal, triggerElement);
    }
  };

  // Track backdrop click vs text selection: only close on pure backdrop click
  let backdropArmed = false;
  const handleModalMousedown = (e) => {
    if (!modal.classList.contains('open')) return;
    backdropArmed = e.target === modal;
  };

  const handleModalClick = (e) => {
    if (!modal.classList.contains('open')) return;
    // Close only if mousedown and mouseup both happened on the backdrop
    if (backdropArmed && e.target === modal) {
      closeLegalModal(modal, triggerElement);
    }
    backdropArmed = false;
  };

  // Store handlers for cleanup
  modalHandlers.set(modal, {
    keydownHandler: handleModalKeydown,
    clickHandler: { mousedownHandler: handleModalMousedown, clickHandler: handleModalClick }
  });

  document.addEventListener('keydown', handleModalKeydown);
  modal.addEventListener('mousedown', handleModalMousedown);
  modal.addEventListener('click', handleModalClick);
}

document.querySelectorAll('[data-modal-trigger]').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    const modalId = `modal-${btn.dataset.modalTrigger}`;
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      modalOpeners.set(modal, btn); // Store the actual trigger button
      initModalFocusTrap(modal, btn);
    }
  });
});

document.querySelectorAll('.legal-modal').forEach(modal => {
  const closeBtn = modal.querySelector('.legal-modal-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      // Prefer the stored opener from modalOpeners (set on open)
      // Fallback only if modal was externally manipulated before being opened
      const triggerBtn = modalOpeners.get(modal);
      closeLegalModal(modal, triggerBtn);
    });
  }
});

/* ═══════════════════════════════════════════════════════════════════════════════
   ── GA4 CONVERSION TRACKING (PHASE 5: MARKETING TRACK 3.1) ──
   Events: form_submit, cta_click, zone_visit, blog_read
   ═════════════════════════════════════════════════════════════════════════════ */

// Initialize GA4 tracking module
const GA4_Tracking = (() => {
  // Check if gtag is available (loaded from GTM script)
  if (typeof gtag === 'undefined') {
    return null;
  }

  const config = {
    measurement_id: 'G-143N31NN8J',
    cross_domain_url: 'via.sayeghstudio.com'
  };

  // Track zone visits (pages under /zonas-landing/*)
  const trackZoneVisit = () => {
    const path = window.location.pathname;
    if (path.includes('/zonas-landing/')) {
      const zoneName = path.split('/').filter(Boolean)[1] || 'unknown';
      gtag('event', 'zone_visit', {
        'event_category': 'conversion',
        'zone_name': zoneName,
        'page_path': path,
        'page_title': document.title,
        'timestamp': new Date().toISOString()
      });
    }
  };

  // Track CTA clicks (links to via.sayeghstudio.com)
  const trackCtaClick = () => {
    const ctaLinks = document.querySelectorAll('a[href*="via.sayeghstudio.com"]');
    ctaLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        const eventLabel = (link.textContent?.trim() || link.dataset.eventLabel || 'CTA button').slice(0, 100);
        const buttonType = link.classList.contains('btn-primary') ? 'primary' :
                          link.classList.contains('btn-brass') ? 'brass' :
                          link.classList.contains('btn-outline') ? 'outline' : 'default';

        gtag('event', 'cta_click', {
          'event_category': 'conversion',
          'event_label': eventLabel,
          'button_type': buttonType,
          'page_path': window.location.pathname,
          'page_title': document.title,
          'timestamp': new Date().toISOString()
        });
      });
    });
  };

  // Track blog read time (>30s on article pages)
  const trackBlogRead = () => {
    const isArticle = document.querySelector('article') !== null;
    if (!isArticle) return;

    let timeOnPage = 0;
    let blogReadTracked = false;
    const READ_THRESHOLD = 30; // seconds

    const trackTime = () => {
      timeOnPage += 1;

      if (timeOnPage === READ_THRESHOLD && !blogReadTracked) {
        blogReadTracked = true;
        const articleTitle = document.querySelector('article h1')?.textContent?.trim() || document.title;

        gtag('event', 'blog_read', {
          'event_category': 'content_engagement',
          'article_title': articleTitle,
          'article_url': window.location.href,
          'time_on_page': timeOnPage,
          'page_title': document.title,
          'timestamp': new Date().toISOString()
        });
      }
    };

    // Track time spent on page (max 5 min, then stop)
    const interval = setInterval(() => {
      if (timeOnPage >= 300) {
        clearInterval(interval);
      } else {
        trackTime();
      }
    }, 1000);

    // Clean up interval on page unload
    window.addEventListener('beforeunload', () => clearInterval(interval));
  };

  // Track form submissions (contact forms on main site)
  const trackFormSubmit = () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        const formId = form.id || 'contact-form';
        const formName = form.name || 'contact-form';

        gtag('event', 'form_submit', {
          'event_category': 'conversion',
          'form_id': formId,
          'form_name': formName,
          'page_path': window.location.pathname,
          'page_title': document.title,
          'timestamp': new Date().toISOString()
        });
      });
    });
  };

  // Initialize all tracking
  const init = () => {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        trackZoneVisit();
        trackCtaClick();
        trackBlogRead();
        trackFormSubmit();
      });
    } else {
      trackZoneVisit();
      trackCtaClick();
      trackBlogRead();
      trackFormSubmit();
    }
  };

  return { init };
})();

// Initialize GA4 tracking when DOM is ready
if (GA4_Tracking) {
  GA4_Tracking.init();
}

/* ═══════════════════════════════════════════════════════════════════════════════
   ── ATRIBUCIÓN HACIA LA AUDITORÍA ──
   Lleva los parámetros utm_* (o el origen detectado por referrer) a todo enlace
   hacia via.sayeghstudio.com, /auditoria y /viabilidad, para que el formulario
   de la Auditoría registre de dónde llegó el prospecto (Pinterest, buscadores…).
   Sin cookies, sin datos personales, sin llamadas de red. Solo sessionStorage.
   ═════════════════════════════════════════════════════════════════════════════ */
(() => {
  const CLAVE = 'sayegh_utm';
  const CAMPOS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  const HOST_VIA = 'via.sayeghstudio.com';
  let enMemoria = null; // respaldo si sessionStorage no está disponible

  // Solo [A-Za-z0-9_.-], máximo n caracteres
  const limpiar = (v, n) => String(v == null ? '' : v).replace(/[^A-Za-z0-9_.\-]/g, '').slice(0, n || 60);

  const leer = () => {
    try {
      const raw = sessionStorage.getItem(CLAVE);
      if (raw) { const o = JSON.parse(raw); if (o && typeof o === 'object') return o; }
    } catch (e) { /* sin acceso a sessionStorage */ }
    return enMemoria;
  };

  const guardar = (obj) => {
    enMemoria = obj;
    try { sessionStorage.setItem(CLAVE, JSON.stringify(obj)); } catch (e) { /* se queda en memoria */ }
  };

  const slugPagina = () => {
    const s = limpiar(String(location.pathname || '').replace(/^\/+|\/+$/g, '').replace(/\//g, '_'), 40);
    return s || 'inicio';
  };

  const desdeReferrer = (ref) => {
    let host;
    try { host = new URL(ref).hostname.toLowerCase().replace(/^www\./, ''); } catch (e) { return null; }
    if (!host) return null;
    let propio = '';
    try { propio = location.hostname.toLowerCase().replace(/^www\./, ''); } catch (e) { /* nada */ }
    if (host === propio || host === 'sayeghstudio.com' || host.endsWith('.sayeghstudio.com')) return null;
    const contenido = 'ref-' + slugPagina();
    const es = (re) => re.test(host);
    if (es(/(^|\.)pinterest\.[a-z.]+$/) || host === 'pin.it') {
      return { utm_source: 'pinterest', utm_medium: 'organic_pin', utm_campaign: 'conversion_auditoria', utm_content: contenido };
    }
    const buscadores = { google: /(^|\.)google\.[a-z.]+$/, bing: /(^|\.)bing\.com$/, duckduckgo: /(^|\.)duckduckgo\.com$/, yahoo: /(^|\.)yahoo\.[a-z.]+$/, ecosia: /(^|\.)ecosia\.org$/ };
    for (const k in buscadores) {
      if (es(buscadores[k])) return { utm_source: k, utm_medium: 'organic', utm_campaign: 'seo', utm_content: contenido };
    }
    const redes = { instagram: /(^|\.)instagram\.com$/, facebook: /(^|\.)facebook\.com$/, tiktok: /(^|\.)tiktok\.com$/, linkedin: /(^|\.)linkedin\.com$|^lnkd\.in$/, twitter: /^t\.co$/, threads: /(^|\.)threads\.(net|com)$/ };
    for (const k in redes) {
      if (es(redes[k])) return { utm_source: k, utm_medium: 'social', utm_campaign: 'referral', utm_content: contenido };
    }
    return { utm_source: limpiar(host, 60) || 'desconocido', utm_medium: 'referral', utm_campaign: 'referral', utm_content: contenido };
  };

  const capturar = () => {
    try {
      const p = new URLSearchParams(location.search);
      const o = {};
      let hay = false;
      CAMPOS.forEach((c) => {
        if (p.has(c)) { const v = limpiar(p.get(c)); if (v) { o[c] = v; hay = true; } }
      });
      if (hay) { guardar(o); return; }
      if (leer()) return;
      if (document.referrer) {
        const r = desdeReferrer(document.referrer);
        if (r) guardar(r);
      }
    } catch (e) { /* nunca romper la página */ }
  };

  const esDestino = (u) => {
    if (u.hostname.toLowerCase() === HOST_VIA) return true;
    if (u.origin !== location.origin) return false;
    return /^\/(auditoria|viabilidad)\/?$/i.test(u.pathname);
  };

  const decorar = (a) => {
    try {
      const href = a && a.getAttribute && a.getAttribute('href');
      if (!href) return;
      const u = new URL(href, location.href);
      if (u.protocol !== 'http:' && u.protocol !== 'https:') return;
      if (!esDestino(u)) return;
      let datos = leer();
      if (!datos || !Object.keys(datos).length) {
        datos = { utm_source: 'sayeghstudio', utm_medium: 'sitio', utm_campaign: 'cta', utm_content: slugPagina() };
      }
      let cambio = false;
      CAMPOS.forEach((c) => {
        if (datos[c] && !u.searchParams.has(c)) { u.searchParams.set(c, datos[c]); cambio = true; }
      });
      if (cambio) a.setAttribute('href', u.toString());
    } catch (e) { /* href raro: se deja intacto */ }
  };

  const decorarTodos = () => {
    try { document.querySelectorAll('a[href]').forEach(decorar); } catch (e) { /* nada */ }
  };

  const alInteractuar = (e) => {
    try {
      const t = e.target;
      const a = t && t.closest ? t.closest('a[href]') : null;
      if (a) decorar(a);
    } catch (err) { /* nada */ }
  };

  capturar();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', decorarTodos);
  else decorarTodos();
  ['click', 'auxclick', 'contextmenu'].forEach((ev) => document.addEventListener(ev, alInteractuar, true));
})();
/* ── FIN ATRIBUCIÓN HACIA LA AUDITORÍA ── */

/* ═══════════════════════════════════════════════════════════════════════════════
   ── PINTEREST TAG ──
   Solo se carga con consentimiento aceptado (misma clave que GA: ga_consent_status).
   Eventos: pagevisit al cargar, lead al clic hacia via.sayeghstudio.com.
   ═════════════════════════════════════════════════════════════════════════════ */
const PinterestTag = (() => {
  const TAG_ID = '2614257025875';
  const CONSENT_KEY = 'ga_consent_status';
  let cargado = false;

  const hayConsentimiento = () => {
    try { return localStorage.getItem(CONSENT_KEY) === 'accepted'; } catch (e) { return false; }
  };

  // Código base oficial de Pinterest
  const cargar = () => {
    if (cargado || !hayConsentimiento()) return;
    cargado = true;
    !function(e){if(!window.pintrk){window.pintrk=function(){window.pintrk.queue.push(Array.prototype.slice.call(arguments))};var n=window.pintrk;n.queue=[],n.version="3.0";var t=document.createElement("script");t.async=!0,t.src=e;var r=document.getElementsByTagName("script")[0];r.parentNode.insertBefore(t,r)}}("https://s.pinimg.com/ct/core.js");
    window.pintrk('load', TAG_ID);
    window.pintrk('page');
    window.pintrk('track', 'pagevisit');
  };

  // Al cargar la página, si ya había consentimiento
  cargar();

  // En el momento en que el usuario acepta (el banner guarda la clave en su propio listener)
  document.addEventListener('click', (e) => {
    if (e.target.closest && e.target.closest('#consent-accept')) cargar();
  });

  // Lead: mismo clic que dispara cta_click en GA4
  document.addEventListener('click', (e) => {
    if (!cargado || typeof window.pintrk !== 'function') return;
    if (e.target.closest && e.target.closest('a[href*="via.sayeghstudio.com"]')) {
      window.pintrk('track', 'lead', { lead_type: 'Auditoría de Viabilidad' });
    }
  });

  return { cargar };
})();

/* ── MANIFIESTO VIDEO SOUND TOGGLE ── */
const manifiestoVideo = document.querySelector('.manifiesto-video-media');
const manifiestoSoundBtn = document.getElementById('manifiesto-sound-toggle');
if (manifiestoVideo && manifiestoSoundBtn) {
  manifiestoSoundBtn.addEventListener('click', () => {
    manifiestoVideo.muted = !manifiestoVideo.muted;
    const soundOn = !manifiestoVideo.muted;
    manifiestoSoundBtn.textContent = soundOn ? '🔊' : '🔇';
    manifiestoSoundBtn.setAttribute('aria-pressed', String(soundOn));
    manifiestoSoundBtn.setAttribute('aria-label', soundOn ? 'Silenciar el video del manifiesto' : 'Activar sonido del video del manifiesto');
  });
}

/* ── AMBIENT BACKGROUND MUSIC TOGGLE ── */
const ambientAudio = document.getElementById('ambient-audio');
const ambientToggleBtn = document.getElementById('ambient-audio-toggle');
if (ambientAudio && ambientToggleBtn) {
  ambientAudio.volume = 0.35;
  ambientToggleBtn.addEventListener('click', () => {
    const icon = ambientToggleBtn.querySelector('.ambient-audio-icon');
    if (ambientAudio.paused) {
      ambientAudio.play().then(() => {
        if (icon) icon.textContent = '🔊';
        ambientToggleBtn.setAttribute('aria-pressed', 'true');
        ambientToggleBtn.setAttribute('aria-label', 'Silenciar música ambiental');
      }).catch(() => {});
    } else {
      ambientAudio.pause();
      if (icon) icon.textContent = '🔈';
      ambientToggleBtn.setAttribute('aria-pressed', 'false');
      ambientToggleBtn.setAttribute('aria-label', 'Activar música ambiental');
    }
  });
}
