// WPBRC — shared interactions
(function(){
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var links  = document.querySelector('.nav-links');
  if(toggle && links){
    toggle.addEventListener('click', function(){
      links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', links.classList.contains('open'));
    });
  }

  // Neighborhood directory live filter
  var search = document.getElementById('dir-search');
  if(search){
    search.addEventListener('input', function(){
      var q = this.value.trim().toLowerCase();
      document.querySelectorAll('table.dir tbody tr').forEach(function(row){
        row.style.display = row.textContent.toLowerCase().indexOf(q) > -1 ? '' : 'none';
      });
    });
  }

  // Simple form guard (no backend wired yet)
  document.querySelectorAll('form[data-demo]').forEach(function(f){
    f.addEventListener('submit', function(e){
      e.preventDefault();
      var msg = f.querySelector('.form-msg');
      if(msg){ msg.style.display='block'; }
      f.reset();
    });
  });

  // Donation modal — any [data-donate] element opens #donate-modal
  var modal = document.getElementById('donate-modal');
  if(modal){
    function openModal(e){ if(e){ e.preventDefault(); } modal.hidden=false; modal.setAttribute('aria-hidden','false'); document.body.classList.add('modal-open'); }
    function closeModal(){ modal.hidden=true; modal.setAttribute('aria-hidden','true'); document.body.classList.remove('modal-open'); }
    document.querySelectorAll('[data-donate]').forEach(function(b){ b.addEventListener('click', openModal); });
    modal.querySelectorAll('[data-donate-close]').forEach(function(c){ c.addEventListener('click', closeModal); });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape' && !modal.hidden){ closeModal(); } });
  }
})();

/* Dynamic scroll-reveal (js-reveal-init) — graceful: content shows if JS/observer absent */
(function(){
  document.documentElement.classList.add('js');
  var sel = '.card, .section-head, .photo-band, .proj, .tier, .postcard';
  var els = Array.prototype.slice.call(document.querySelectorAll(sel));
  els.forEach(function(el){ el.classList.add('reveal'); });
  if(!('IntersectionObserver' in window)){ els.forEach(function(el){el.classList.add('in');}); return; }
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {rootMargin:'0px 0px -8% 0px', threshold:0.06});
  els.forEach(function(el){ io.observe(el); });
})();
