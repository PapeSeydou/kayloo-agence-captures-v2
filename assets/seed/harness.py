
"""Harness de capture : Chrome, 1440x810 @2x, etats propres, JSON des elements visibles.

Conventions de sortie (brief) :
  screens/NN_screen_state.png (+ .json, + .txt pour les cartes/textes legaux)
  elements/... crops 2x pour les etats de boutons
Les coordonnees du JSON sont exprimees dans l'image exportee (pixels CSS x facteur).
"""
import json
import os
import shutil
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".agents" / "capture-v2" / "out"
SCREENS = OUT / "screens"
ELEMENTS = OUT / "elements"
ASSETS = OUT / "assets"
HOST = "http://kayloo.local:8000"
VIEWPORT = {"width": 1440, "height": 810}
SCALE = 2

STATE_FILE = ROOT / ".agents" / "capture-v2" / "storage.json"

_ELEMENT_JS = r"""
(args) => {
  const [onlyInViewport, scrollX, scrollY, SCALE] = args;
  const out = [];
  const seen = new Set();
  const isVisible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return false;
    if (onlyInViewport) {
      return r.bottom > 0 && r.right > 0 && r.top < window.innerHeight && r.left < window.innerWidth;
    }
    return true;
  };
  const textOf = (el) => {
    if (el.getAttribute('aria-label')) return el.getAttribute('aria-label').trim();
    if (el.tagName === 'INPUT') {
      const t = (el.getAttribute('type') || 'text').toLowerCase();
      if (t === 'checkbox' || t === 'radio') {
        const lab = el.closest('label') || document.querySelector('label[for="' + el.id + '"]');
        if (lab) return lab.innerText.replace(/\s+/g, ' ').trim();
      }
      return (el.getAttribute('placeholder') || el.getAttribute('aria-label') || el.value || el.name || '').trim();
    }
    if (el.tagName === 'SELECT') {
      const lab = el.closest('label') || (el.id && document.querySelector('label[for="' + el.id + '"]'));
      return (el.getAttribute('aria-label') || (lab && lab.innerText) || el.name || '').replace(/\s+/g, ' ').trim();
    }
    if (el.tagName === 'TEXTAREA') return (el.getAttribute('placeholder') || el.name || '').trim();
    let t = (el.innerText || '').replace(/\s+/g, ' ').trim();
    if (!t) t = (el.getAttribute('title') || el.getAttribute('alt') || el.value || '').trim();
    if (t.length > 90) t = t.slice(0, 87) + '...';
    return t;
  };
  const kindOf = (el) => {
    const tag = el.tagName.toLowerCase();
    const type = (el.getAttribute('type') || '').toLowerCase();
    if (type === 'file') return 'upload';
    if (type === 'checkbox' || type === 'radio') return 'checkbox';
    if (tag === 'a') return 'link';
    if (tag === 'button' || type === 'submit' || type === 'button' || el.getAttribute('role') === 'button') return 'button';
    if (tag === 'input' || tag === 'select' || tag === 'textarea') return 'input';
    if (el.matches('[data-card], .card, .pack, [class*="card"], [class*="plan"], [class*="pack"]')) return 'card';
    return 'link';
  };
  const selectors = 'a, button, input, select, textarea, label[for], [role="button"], [role="tab"], ' +
    '[data-card], .card, [class*="card"], [class*="plan"], [class*="pack"]';
  for (const el of document.querySelectorAll(selectors)) {
    if (!isVisible(el)) continue;
    const r = el.getBoundingClientRect();
    const label = textOf(el);
    if (!label) continue;
    const kind = kindOf(el);
    const key = kind + '|' + label + '|' + Math.round(r.x) + '|' + Math.round(r.y);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({
      label,
      type: kind,
      x: Math.round(r.x * SCALE),
      y: Math.round(r.y * SCALE),
      width: Math.round(r.width * SCALE),
      height: Math.round(r.height * SCALE),
      tap: false,
    });
  }
  return out;
}
"""


class Capture:
    def __init__(self, scale=SCALE, viewport=None):
        self.scale = scale
        self.viewport = viewport or dict(VIEWPORT)
        self._pw = None
        self.browser = None
        self.ctx = None
        self.page = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(
            headless=True,
            args=[
                "--force-device-scale-factor=2",
                "--hide-scrollbars",
                "--disable-features=IsolateOrigins,site-per-process",
                "--font-render-hinting=none",
            ],
        )
        kw = dict(viewport=self.viewport, device_scale_factor=self.scale,
                  locale="fr-FR", timezone_id="Africa/Dakar", color_scheme="light")
        if STATE_FILE.exists():
            kw["storage_state"] = str(STATE_FILE)
        self.ctx = self.browser.new_context(**kw)
        self.page = self.ctx.new_page()
        self._block_noise()
        return self

    def _block_noise(self):
        page = self.page
        # aucun curseur, aucune animation residuelle
        page.add_init_script("""
            document.addEventListener('DOMContentLoaded', () => {
              const s = document.createElement('style');
              s.textContent = '*{animation:none !important;transition:none !important;caret-color:transparent !important;}';
              document.head.appendChild(s);
            });
        """)

    def save_state(self):
        self.ctx.storage_state(path=str(STATE_FILE))

    def goto(self, path, wait="networkidle", timeout=45000):
        url = HOST + path if path.startswith("/") else path
        self.page.goto(url, wait_until=wait, timeout=timeout)
        self.settle()

    def settle(self, ms=700):
        try:
            self.page.evaluate("() => document.fonts && document.fonts.ready")
        except Exception:
            pass
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        self.page.wait_for_timeout(ms)

    def dismiss_cookies(self):
        for label in ("Refuser", "Tout refuser", "Accepter", "J'accepte"):
            loc = self.page.get_by_role("button", name=label, exact=False)
            if loc.count():
                try:
                    loc.first.click(timeout=3000)
                    self.page.wait_for_timeout(400)
                    return label
                except Exception:
                    pass
        return None

    def elements(self, only_in_viewport=True):
        scroll = self.page.evaluate("() => ({x: window.scrollX, y: window.scrollY, w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight})")
        els = self.page.evaluate(_ELEMENT_JS, [only_in_viewport, scroll["x"], scroll["y"], self.scale])
        return els, scroll

    def shot(self, name, directory=SCREENS, full=False, tap_labels=(), note=None, txt=None):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        png = directory / (name + ".png")
        self.settle()
        if full:
            png = self.page.screenshot(path=str(png), full_page=True, animations="disabled", caret="hide")
        else:
            png = self.page.screenshot(path=str(png), full_page=False, animations="disabled", caret="hide")
        els, scroll = self.elements(only_in_viewport=not full)
        taps = {t.strip().lower() for t in tap_labels}
        for el in els:
            if el["label"].strip().lower() in taps:
                el["tap"] = True
        payload = {
            "screen": name,
            "file": png.name if hasattr(png, "name") else str(png),
            "url": self.page.url,
            "viewport": self.viewport,
            "device_scale_factor": self.scale,
            "full_page": full,
            "scroll": scroll,
            "elements": els,
        }
        if note:
            payload["note"] = note
        (directory / (name + ".json")).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if txt is not None:
            (directory / (name + ".txt")).write_text(txt, encoding="utf-8")
        return png

    def page_text(self, selector="body"):
        return self.page.locator(selector).first.inner_text()

    def crop(self, name, selector, pad=16, directory=None):
        """Crop 2x d'un element (marge en px CSS) pour les etats de boutons."""
        directory = Path(directory or ELEMENTS)
        directory.mkdir(parents=True, exist_ok=True)
        el = self.page.locator(selector).first
        el.scroll_into_view_if_needed()
        box = el.bounding_box()
        if not box:
            raise RuntimeError("no box for " + selector)
        png = directory / (name + ".png")
        self.page.screenshot(path=str(png), clip={
            "x": max(0, box["x"] - pad), "y": max(0, box["y"] - pad),
            "width": box["width"] + pad * 2, "height": box["height"] + pad * 2,
        }, animations="disabled", caret="hide")
        return png

    def hover(self, selector):
        self.page.locator(selector).first.hover()
        self.page.wait_for_timeout(450)

    def unhover(self):
        self.page.mouse.move(2, 2)
        self.page.wait_for_timeout(250)

    def __exit__(self, *exc):
        try:
            if self.ctx:
                self.ctx.close()
            if self.browser:
                self.browser.close()
        finally:
            if self._pw:
                self._pw.stop()
        return False
