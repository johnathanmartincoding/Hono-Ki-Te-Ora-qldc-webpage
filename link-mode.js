/*
 * link-mode.js
 *
 * Include this on every page with:
 *   <script src="link-mode.js" defer></script>
 *
 * On load, it checks whether serve.py exists next to this page (i.e. it's
 * being tested locally or via the GitHub Pages preview copy of the repo).
 *   - serve.py found     -> nav links point at the GitHub Pages preview
 *   - serve.py NOT found -> nav links point at the real live site
 *
 * So: once this gets folded into the real site and serve.py is deleted from
 * that deployment, every link on every page switches over automatically -
 * nothing else needs to change.
 */
(function () {
  var GH_PAGES_BASE = "https://johnathanmartincoding.github.io/Hono-Ki-Te-Ora-qldc-webpage/";
  var LIVE_BASE = "https://www.hkto.org.nz";

  // Local filename -> { preview: path on GitHub Pages, live: path on the real site }
  var PAGES = {
    "index.html": { preview: "index.html", live: "/" },
    "about.html": { preview: "about.html", live: "/about" },
    "contact.html": { preview: "contact.html", live: "/contact" },
    "how-it-works.html": { preview: "how-it-works.html", live: "/how-it-works" },
    "for-referrers.html": { preview: "for-referrers.html", live: "/for-referrers" },
    "referral.html": { preview: "referral.html", live: "/referral" }
  };

  function apply(serveFound) {
    var base = serveFound ? GH_PAGES_BASE : LIVE_BASE;
    document.querySelectorAll("a[href]").forEach(function (a) {
      var href = a.getAttribute("href").replace(/^\.\//, "");
      var page = PAGES[href];
      if (!page) return; // leave anything not in the list (tel:, mailto:, the directory page, etc.) alone
      a.setAttribute("href", base + (serveFound ? page.preview : page.live));
    });
  }

  fetch("serve.py", { method: "HEAD", cache: "no-store" })
    .then(function (r) { apply(r.ok); })
    .catch(function () { apply(false); }); // no serve.py reachable at all -> treat as live
})();
