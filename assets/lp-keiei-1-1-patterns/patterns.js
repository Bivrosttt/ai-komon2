(function () {
  'use strict';

  var items = document.querySelectorAll('.js-reveal');
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    Array.prototype.forEach.call(items, function (item) { item.classList.add('is-on'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-on');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    Array.prototype.forEach.call(items, function (item) { observer.observe(item); });
  }

  var bar = document.querySelector('.sticky-cta');
  var hero = document.querySelector('[data-hero]');
  if (!bar || !hero) return;
  function updateBar() {
    bar.classList.toggle('is-visible', window.scrollY > 420);
  }
  window.addEventListener('scroll', updateBar, { passive: true });
  updateBar();
}());
