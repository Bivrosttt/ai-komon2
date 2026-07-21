(function () {
  'use strict';

  var items = document.querySelectorAll('.reveal');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduceMotion || !('IntersectionObserver' in window)) {
    items.forEach(function (item) { item.classList.add('is-visible'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });

    items.forEach(function (item) { observer.observe(item); });
  }

  var mobileCta = document.getElementById('mobileCta');
  var finalCta = document.querySelector('.final-cta');
  if (!mobileCta) return;

  function updateMobileCta() {
    var isPastHero = window.scrollY > 480;
    var isNearFinal = finalCta && finalCta.getBoundingClientRect().top < window.innerHeight * 0.8;
    mobileCta.classList.toggle('is-visible', isPastHero && !isNearFinal);
  }

  window.addEventListener('scroll', updateMobileCta, { passive: true });
  updateMobileCta();
}());
