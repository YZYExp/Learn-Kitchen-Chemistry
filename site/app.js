(() => {
  'use strict';
  const read = (key, fallback = null) => { try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; } };
  const write = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  const prefix = 'kitchen-science:';
  const themeButton = document.querySelector('[data-theme-toggle]');
  const applyTheme = value => {
    document.body.dataset.theme = value;
    if (themeButton) { themeButton.textContent = value === 'dark' ? '亮色' : '暗色'; themeButton.setAttribute('aria-pressed', String(value === 'dark')); }
  };
  applyTheme(read(prefix + 'theme', 'light'));
  themeButton?.addEventListener('click', () => { const next = document.body.dataset.theme === 'dark' ? 'light' : 'dark'; write(prefix + 'theme', next); applyTheme(next); });
  let fontSize = Math.max(16, Math.min(24, Number(read(prefix + 'font', '18')) || 18));
  const fontLabel = document.querySelector('[data-font-label]');
  const applyFont = () => { document.documentElement.style.setProperty('--body-size', fontSize + 'px'); if (fontLabel) fontLabel.textContent = fontSize + 'px'; };
  applyFont();
  document.querySelectorAll('[data-font-change]').forEach(button => button.addEventListener('click', () => { fontSize = Math.max(16, Math.min(24, fontSize + Number(button.dataset.fontChange))); write(prefix + 'font', String(fontSize)); applyFont(); }));
  const directoryLinks = [...document.querySelectorAll('[data-search-title]')];
  const search = document.querySelector('[data-directory-search]');
  search?.addEventListener('input', () => {
    const q = search.value.trim().toLocaleLowerCase(); let count = 0;
    directoryLinks.forEach(link => { const match = link.dataset.searchTitle.toLocaleLowerCase().includes(q); link.hidden = !match; if (match) count++; });
    document.querySelectorAll('[data-directory-part]').forEach(part => { part.hidden = ![...part.querySelectorAll('[data-search-title]')].some(a => !a.hidden); });
    const empty = document.querySelector('[data-search-empty]'); if (empty) empty.hidden = count > 0;
    const status = document.querySelector('[data-search-status]'); if (status) status.textContent = q ? `找到 ${count} 章` : '';
  });
  const sidebarDetails = document.querySelector('.sidebar details');
  if (matchMedia('(max-width: 780px)').matches) {
    if (sidebarDetails) sidebarDetails.open = false;
    const pageToc = document.querySelector('.reading-tools .toc'); if (pageToc) pageToc.open = false;
  }
  const path = location.pathname;
  const article = document.querySelector('.reader');
  const savedKey = prefix + 'position:' + path;
  let savedPosition = 0; try { savedPosition = Number(read(savedKey, '0')) || 0; } catch {}
  const progress = document.querySelector('.progress');
  if (article) {
    const title = document.querySelector('h1')?.textContent || document.title;
    write(prefix + 'last', JSON.stringify({ path, title }));
    const note = document.querySelector('[data-resume-note]');
    if (savedPosition > 250 && note) {
      note.hidden = false;
      note.querySelector('button')?.addEventListener('click', () => { window.scrollTo({ top: savedPosition, behavior: 'smooth' }); note.hidden = true; });
    }
    let timer;
    const update = () => {
      const total = Math.max(1, document.documentElement.scrollHeight - innerHeight);
      if (progress) progress.style.width = Math.max(0, Math.min(100, scrollY / total * 100)) + '%';
      clearTimeout(timer); timer = setTimeout(() => write(savedKey, String(Math.round(scrollY))), 250);
    };
    addEventListener('scroll', update, { passive: true }); update();
    addEventListener('pagehide', () => write(savedKey, String(Math.round(scrollY))));
  } else {
    try {
      const last = JSON.parse(read(prefix + 'last', 'null'));
      const resume = document.querySelector('[data-resume-link]');
      const base = document.body.dataset.base || '/';
      if (resume && last?.path?.startsWith(base + 'chapters/')) { resume.href = last.path; resume.hidden = false; resume.textContent = '继续阅读：' + last.title.replace(/^第\d+章\s*/, ''); }
    } catch {}
  }
  const dialog = document.querySelector('[data-image-dialog]');
  if (dialog && typeof dialog.showModal === 'function') {
    const picture = dialog.querySelector('img'); const caption = dialog.querySelector('p'); let previousFocus;
    const close = () => { dialog.close(); previousFocus?.focus(); };
    dialog.querySelector('button').addEventListener('click', close);
    dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
    document.querySelectorAll('[data-zoom-image]').forEach(image => {
      image.tabIndex = 0; image.setAttribute('role', 'button'); image.setAttribute('aria-label', '放大图片：' + image.alt);
      const open = () => { previousFocus = image; picture.src = image.dataset.full || image.src; picture.alt = image.alt; caption.textContent = image.closest('figure')?.querySelector('figcaption')?.textContent || image.alt; dialog.showModal(); };
      image.addEventListener('click', open); image.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); } });
    });
    dialog.addEventListener('close', () => { picture.removeAttribute('src'); previousFocus?.focus(); });
  }
})();
