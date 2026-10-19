/* Subpáginas: lógica del banner de consentimiento GA4 (misma que el home). */
(function () {
  var KEY = 'ga_consent_status';
  function init() {
    var banner = document.getElementById('consent-banner');
    var accept = document.getElementById('consent-accept');
    var decline = document.getElementById('consent-decline');
    if (!banner || !accept || !decline) return;
    var status = null;
    try { status = localStorage.getItem(KEY); } catch (e) {}
    if (status) { banner.classList.add('hidden'); return; }
    banner.classList.remove('hidden');
    accept.addEventListener('click', function () {
      try { localStorage.setItem(KEY, 'accepted'); } catch (e) {}
      if (typeof gtag === 'function') {
        gtag('consent', 'update', { analytics_storage: 'granted', ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted' });
        gtag('config', 'G-143N31NN8J', { allow_google_signals: true, anonymize_ip: true });
      }
      banner.classList.add('hidden');
    });
    decline.addEventListener('click', function () {
      try { localStorage.setItem(KEY, 'declined'); } catch (e) {}
      banner.classList.add('hidden');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
