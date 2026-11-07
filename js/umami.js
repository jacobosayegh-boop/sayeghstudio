/* ═══════════════════════════════════════════════════════════════════════════════
   ── UMAMI · MEDICIÓN DE FUENTES SIN COOKIES ──
   Umami (código abierto, licencia MIT) en un servidor propio de Sayegh Studio.
   No usa cookies ni guarda datos personales: cuenta visitas, de qué fuente llegan
   (utm_source, buscador, red social) y los clics hacia la Auditoría de Viabilidad.
   Respeta el banner: si el visitante pulsa "Rechazar" (ga_consent_status = declined)
   o su navegador manda Global Privacy Control / Do Not Track, no se envía nada,
   ni siquiera durante la visita en curso. Mientras no haya respuesta en el banner,
   mide sin cookies (Umami no deja nada en el navegador).
   Inerte hasta que UMAMI_HOST y UMAMI_SITIO tengan valor.
   ═════════════════════════════════════════════════════════════════════════════ */
(function () {
  var UMAMI_HOST = '';    // https://<pod>.pikapod.net (sin / final)
  var UMAMI_SITIO = '';   // id del sitio sayeghstudio.com en Umami
  var DOMINIOS = 'sayeghstudio.com,www.sayeghstudio.com';
  var CLAVE_BANNER = 'ga_consent_status';
  var HOST_VIA = 'via.sayeghstudio.com';

  if (window.__sayeghUmami) return;
  window.__sayeghUmami = true;
  if (!UMAMI_HOST || !UMAMI_SITIO) return;

  function rechazo() {
    try { if (localStorage.getItem(CLAVE_BANNER) === 'declined') return true; } catch (e) { /* sin acceso */ }
    try { if (navigator.globalPrivacyControl === true) return true; } catch (e) { /* nada */ }
    return false;
  }
  // Umami llama a esta función antes de cada envío: si el visitante rechazó, no sale nada
  window.sayeghUmamiAntes = function (tipo, datos) { return rechazo() ? null : datos; };
  if (rechazo()) return;

  var s = document.createElement('script');
  s.defer = true;
  s.src = UMAMI_HOST + '/script.js';
  s.setAttribute('data-website-id', UMAMI_SITIO);
  s.setAttribute('data-host-url', UMAMI_HOST);
  s.setAttribute('data-domains', DOMINIOS);
  s.setAttribute('data-do-not-track', 'true');
  s.setAttribute('data-before-send', 'sayeghUmamiAntes');
  (document.head || document.documentElement).appendChild(s);

  var limpiar = function (v) { return String(v == null ? '' : v).replace(/[^A-Za-z0-9_.\-]/g, '').slice(0, 60); };
  // Fuente del visitante: la que guardó la atribución de main.js (sessionStorage sayegh_utm), la del enlace o "directo"
  function fuente(u) {
    try { var o = JSON.parse(sessionStorage.getItem('sayegh_utm') || 'null'); if (o && o.utm_source) return limpiar(o.utm_source); } catch (e) { /* nada */ }
    try { var p = new URLSearchParams(location.search).get('utm_source'); if (p) return limpiar(p); } catch (e) { /* nada */ }
    try { var d = u && u.searchParams.get('utm_source'); if (d && d !== 'sayeghstudio') return limpiar(d); } catch (e) { /* nada */ }
    return 'directo';
  }
  function esAuditoria(u) {
    if (u.hostname.toLowerCase() === HOST_VIA) return true;
    return u.origin === location.origin && /^\/(auditoria|viabilidad)\/?$/i.test(u.pathname);
  }
  // clic_auditoria: un evento por clic hacia VIA, /auditoria o /viabilidad, con su fuente y la página de origen
  document.addEventListener('click', function (e) {
    try {
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if (!a) return;
      var u = new URL(a.getAttribute('href'), location.href);
      if (!esAuditoria(u)) return;
      if (!window.umami || typeof window.umami.track !== 'function') return;
      window.umami.track('clic_auditoria', { fuente: fuente(u), pagina: limpiar(location.pathname.replace(/^\/+|\/+$/g, '').replace(/\//g, '_')) || 'inicio' });
    } catch (err) { /* nunca romper la página */ }
  }, true);
})();
