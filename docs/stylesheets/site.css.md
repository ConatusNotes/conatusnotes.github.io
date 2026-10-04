:root {

  --paper: #fffcf0;

  --paper-2: #f2f0e5;

  --ink: #100f0f;

  --muted: #6f6e69;

  --border: #e6e4d9;

  

  --purple: #5e409d;

  --purple-hover: #8b7ec8;

  

  --orange: #bc5215;

  --orange-hover: #da702c;

  

  --md-default-bg-color: var(--paper);

  --md-default-fg-color: var(--ink);

  --md-typeset-a-color: var(--purple);

}

  

/* ---------- whole page ---------- */

  

html,

body,

.md-container,

.md-main {

  background: var(--paper);

  color: var(--ink);

}

  

body {

  font-family:

    -apple-system,

    BlinkMacSystemFont,

    "Segoe UI",

    Helvetica,

    Arial,

    sans-serif;

}

  

/* ---------- header ---------- */

  

.md-header {

  background: var(--paper);

  color: var(--ink);

  

  box-shadow: none;

  border-bottom: 1px solid var(--border);

}

  

.md-header__inner {

  max-width: 980px;

}

  

.md-header__title {

  color: var(--ink);

  font-weight: 500;

  font-size: 1.05rem;

}

  

/* remove Material-looking clutter */

  

.md-search,

.md-header__source {

  display: none;

}

  

/* ---------- horizontal section tabs ---------- */

  

.md-tabs {

  background: var(--paper);

  color: var(--ink);

  

  border-bottom: 1px solid var(--border);

}

  

.md-tabs__inner {

  max-width: 980px;

}

  

.md-tabs__link {

  position: relative;

  

  color: var(--ink);

  opacity: 1;

  

  font-size: 0.78rem;

  font-weight: 450;

}

  

.md-tabs__link:hover {

  color: var(--purple);

}

  

/* active tab = tiny orange mark */

  

.md-tabs__item--active .md-tabs__link {

  color: var(--ink);

  font-weight: 550;

}

  

.md-tabs__item--active .md-tabs__link::after {

  content: "";

  

  position: absolute;

  left: 0;

  right: 0;

  bottom: -0.65rem;

  

  height: 2px;

  

  background: var(--orange);

}

  

/* ---------- article ---------- */

  

.md-grid {

  max-width: 980px;

}

  

.md-content__inner {

  max-width: 760px;

  

  margin: 0 auto;

  padding-top: 2.5rem;

  padding-bottom: 6rem;

}

  

.md-typeset {

  color: var(--ink);

  

  font-size: 17px;

  line-height: 1.68;

}

  

/* ---------- headings ---------- */

  

.md-typeset h1 {

  margin: 0 0 1.5rem;

  

  color: var(--ink);

  

  font-size: 2rem;

  font-weight: 550;

  letter-spacing: -0.025em;

  line-height: 1.18;

}

  

.md-typeset h2 {

  margin-top: 2.5rem;

  

  color: var(--ink);

  

  font-size: 1.45rem;

  font-weight: 550;

  letter-spacing: -0.015em;

}

  

.md-typeset h3 {

  color: var(--ink);

  

  font-size: 1.12rem;

  font-weight: 600;

}

  

/* ---------- links ---------- */

  

.md-typeset a {

  color: var(--purple);

  

  text-decoration: none;

  text-decoration-thickness: 1px;

  text-underline-offset: 3px;

}

  

.md-typeset a:hover {

  color: var(--purple-hover);

  text-decoration: underline;

}

  

/* ---------- subtle orange accents ---------- */

  

.md-typeset blockquote {

  border-left: 2px solid var(--orange);

  

  color: var(--muted);

}

  

.md-typeset hr {

  border-color: var(--border);

}

  

.md-typeset ::selection {

  background: rgba(218, 112, 44, 0.22);

}

  

/* ---------- dates / secondary text ---------- */

  

.md-typeset small,

.md-typeset .date,

.md-typeset .meta {

  color: var(--muted);

}

  

/* ---------- code ---------- */

  

.md-typeset code {

  background: var(--paper-2);

  color: var(--ink);

  

  border-radius: 2px;

}

  

.md-typeset pre > code {

  background: var(--paper-2);

}

  

/* ---------- images ---------- */

  

.md-typeset img {

  border-radius: 0;

  box-shadow: none;

}

  

/* ---------- navigation/sidebar ---------- */

  

.md-nav__link {

  color: var(--muted);

}

  

.md-nav__link:hover {

  color: var(--purple);

}

  

.md-nav__link--active {

  color: var(--purple);

  font-weight: 550;

}

  

/* ---------- footer ---------- */

  

.md-footer,

.md-footer-meta {

  background: var(--paper);

  color: var(--muted);

}

  

/* ---------- mobile ---------- */

  

@media screen and (max-width: 767px) {

  .md-content__inner {

    padding-top: 1.5rem;

  }

  

  .md-typeset {

    font-size: 16px;

  }

  

  .md-typeset h1 {

    font-size: 1.75rem;

  }

}