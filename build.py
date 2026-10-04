"""Build docs/ into _site/. Run by GitHub Actions, not on your Mac."""
from __future__ import annotations

import html
import os
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import mistune
import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
OUT = ROOT / "_site"
NAME = os.environ.get("SITE_NAME", "Your Name")
BASE = urlsplit(os.environ.get("SITE_URL", "https://example.org/")).path.rstrip("/")
MEDIA = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}
IGNORE = {"stylesheets", "javascripts", "_templates", "templates"}
PAGES: dict[Path, dict] = {}
ASSETS: set[Path] = set()
FOLDERS: set[Path] = {Path(".")}

CSS = """
:root { color-scheme:light; --paper:#fffcf0; --paper2:#f2f0e5;
  --ink:#100f0f; --muted:#6f6e69; --line:#e6e4d9;
  --purple:#5e409d; --hover:#735eb5; --orange:#bc5215; }
* { box-sizing:border-box; }
html { background:var(--paper); scroll-padding-top:24px; }
body { margin:0; color:var(--ink); background:var(--paper);
  font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
a { color:var(--purple); background:transparent; text-decoration:none;
  text-underline-offset:4px; }
a:hover { color:var(--hover); text-decoration:underline; }
a:focus-visible { outline:2px solid var(--orange); outline-offset:5px; }
::selection { background:#da702c38; }
header { border-bottom:1px solid var(--line); }
.header { max-width:1080px; margin:auto; padding:24px;
  display:flex; flex-wrap:wrap; align-items:center; gap:18px 36px;
  min-height:104px; }
.brand { margin-right:auto; color:var(--ink); font-size:32px;
  font-weight:500; letter-spacing:-1px; line-height:1.2;
  overflow-wrap:anywhere; }
.brand:hover { color:var(--ink); text-decoration:none; }
nav { display:flex; flex-wrap:wrap; align-items:center;
  justify-content:flex-end; gap:8px 26px; max-width:100%; min-width:0; }
nav a { display:block; color:var(--ink); line-height:1.4; padding:7px 0;
  border-bottom:2px solid transparent; overflow-wrap:anywhere; max-width:100%; }
nav a:hover { color:var(--purple); text-decoration:none; }
nav a.current { border-color:var(--orange); }
main { width:min(100% - 48px,740px); margin:52px auto 90px; }
h1,h2,h3 { line-height:1.25; font-weight:550; letter-spacing:-.025em;
  overflow-wrap:anywhere; }
h1 { font-size:34px; margin:0 0 24px; }
h2 { font-size:25px; margin:44px 0 18px; }
h3 { font-size:20px; margin:32px 0 14px; }
p { margin:0 0 20px; }
article { overflow-wrap:anywhere; }
article ul,article ol { padding-left:24px; }
article li { margin:6px 0; }
.items { padding:0; margin:0; list-style:none; }
.items li { margin:0; padding:14px 0; border-bottom:1px solid var(--line); }
.items a { font-size:21px; line-height:1.4; }
.items time { display:block; margin-top:2px; }
.meta,time,footer { color:var(--muted); font-size:14px; }
.meta { margin:-12px 0 26px; }
.breadcrumb { display:block; margin-bottom:18px; font-size:14px; }
blockquote { margin:24px 0; padding:0 0 0 18px;
  border-left:2px solid var(--orange); color:var(--muted); }
code { background:var(--paper2); padding:2px 5px;
  font: .9em/1.6 ui-monospace,SFMono-Regular,Menlo,monospace; }
pre { overflow:auto; padding:18px; background:var(--paper2);
  border:1px solid var(--line); }
pre code { padding:0; background:transparent; }
a code { color:inherit; background:transparent; }
img,video { display:block; max-width:100%; height:auto; margin:24px auto; }
table { display:block; width:100%; overflow:auto; border-collapse:collapse;
  margin:24px 0; font-size:15px; }
th,td { padding:9px 14px; border:1px solid var(--line); text-align:left; }
th { background:var(--paper2); }
hr { border:0; border-top:1px solid var(--line); margin:36px 0; }
.math { overflow-x:auto; }
footer { max-width:1080px; margin:auto; padding:20px 24px;
  border-top:1px solid var(--line); }
.skip { position:absolute; left:12px; top:-100px; background:var(--paper); }
.skip:focus { top:8px; }
@media (max-width:700px) {
  .header { padding:22px 20px 16px; gap:12px; }
  .brand { font-size:29px; }
  nav { flex-basis:100%; justify-content:flex-start; gap:4px 21px; }
  nav a { font-size:16px; }
  main { width:calc(100% - 40px); margin-top:34px; }
  body { font-size:16px; }
  h1 { font-size:29px; } h2 { font-size:23px; }
}
"""

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def clean_title(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def anchor(text: str) -> str:
    return re.sub(r"[^\w\- ]", "", clean_title(text).lower()).replace(" ", "-")


def address(path: Path, asset: bool = False) -> str:
    if asset:
        return BASE + "/files/" + quote(path.as_posix(), safe="/")
    target = path.parent if path.name == "index.md" else path.with_suffix("")
    tail = "" if str(target) == "." else quote(target.as_posix(), safe="/") + "/"
    return BASE + "/" + tail


def folder_url(folder: Path) -> str:
    return address(folder / "index.md")


def load_pages() -> None:
    if not DOCS.is_dir():
        raise ValueError("Missing docs/ folder. Keep your notes inside docs/.")
    for source in sorted(DOCS.rglob("*")):
        rel = source.relative_to(DOCS)
        if any(part.startswith(".") or part in IGNORE for part in rel.parts):
            continue
        if source.is_symlink():
            raise ValueError(f"Symlinks are not published: {rel}")
        if not source.is_file():
            continue
        if source.suffix.lower() not in {".md", ".markdown"}:
            if source.suffix.lower() not in {".html", ".js", ".css", ".yml", ".yaml", ".py"}:
                ASSETS.add(rel)
            continue
        if rel.suffix != ".md":
            raise ValueError(f"Rename {rel} to use the .md extension.")
        text = source.read_text(encoding="utf-8-sig")
        meta = {}
        front = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
        if front:
            meta = yaml.safe_load(front.group(1)) or {}
            if not isinstance(meta, dict):
                raise ValueError(f"Invalid YAML properties: {rel}")
            text = text[front.end():]
        heading = re.match(r"\A\s*#\s+([^\n]+)\n?", text)
        fallback = rel.parent.name if rel.name == "index.md" else rel.stem
        title = str(meta.get("title") or (clean_title(mistune.html(heading.group(1))) if heading else re.sub(r"^\d{4}-\d{2}-\d{2}[ _-]+", "", fallback)))
        if heading:
            text = text[heading.end():]
        stamp = str(meta.get("date") or "")[:10]
        if not stamp and re.match(r"\d{4}-\d{2}-\d{2}", rel.stem):
            stamp = rel.stem[:10]
        if stamp:
            stamp = date.fromisoformat(stamp).isoformat()
        PAGES[rel] = {"title": title, "body": text, "date": stamp}
        FOLDERS.update(rel.parents)
    # A file and a folder cannot both own /Research/foo/.
    seen = set()
    for rel in PAGES:
        url = address(rel)
        if url in seen or (rel.name != "index.md" and rel.with_suffix("") in FOLDERS):
            raise ValueError(f"Conflicting page/folder URL: {rel}")
        seen.add(url)


def resolve(current: Path, target: str, image: bool = False, wiki: bool = False) -> str:
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return target
    if not parsed.path:
        return "#" + quote(anchor(unquote(parsed.fragment)) if wiki else unquote(parsed.fragment))
    raw = unquote(parsed.path)
    choices = [DOCS / raw.lstrip("/")] if raw.startswith("/") else [DOCS / current.parent / raw, DOCS / raw]
    found = None
    for choice in choices:
        candidate = choice.resolve()
        if not candidate.is_relative_to(DOCS.resolve()):
            continue
        rel = candidate.relative_to(DOCS.resolve())
        for item in [rel, Path(str(rel) + ".md"), rel / "index.md"]:
            if item in ASSETS or item in PAGES:
                found = item
                break
        if found is not None:
            break
        if rel in FOLDERS:
            found = rel / "index.md"
            break
    if found is None and wiki:
        matches = [p for p in set(PAGES) | ASSETS if p.name == raw or p.stem == raw]
        if len(matches) == 1:
            found = matches[0]
    if found is None:
        raise ValueError(f"{current}: cannot find '{target}' inside docs/. Fix the link before publishing.")
    is_asset = found in ASSETS
    if image and (not is_asset or found.suffix.lower() not in MEDIA):
        raise ValueError(f"{current}: only image embeds are supported, not note embeds: {target}")
    result = address(found, is_asset)
    if parsed.query:
        result += "?" + parsed.query
    if parsed.fragment:
        result += "#" + quote(anchor(unquote(parsed.fragment)) if wiki else unquote(parsed.fragment))
    return result


class Renderer(mistune.HTMLRenderer):
    def __init__(self, current: Path):
        super().__init__(escape=True)
        self.current = current
        self.ids: dict[str, int] = {}

    def heading(self, text: str, level: int, **attrs) -> str:
        key = anchor(text)
        count = self.ids.get(key, 0)
        self.ids[key] = count + 1
        return super().heading(text, level, id=key + (f"-{count}" if count else ""))

    def link(self, text: str, url: str, title=None) -> str:
        return super().link(text, resolve(self.current, url), title)

    def image(self, text: str, url: str, title=None) -> str:
        return super().image(text, resolve(self.current, url, image=True), title)

    def wiki(self, text: str, target: str, embed: bool = False) -> str:
        url = resolve(self.current, target, image=embed, wiki=True)
        if embed:
            return super().image(esc(text), url)
        return super().link(esc(text), url)


def wikilinks(md) -> None:
    def parse(inline, match, state):
        full = match.group(0)
        inside = full[3:-2] if full.startswith("!") else full[2:-2]
        target, _, label = inside.partition("|")
        state.append_token({"type": "wiki", "raw": label or target,
                            "attrs": {"target": target.strip(), "embed": full.startswith("!")}})
        return match.end()
    md.inline.register("wiki", r"!?\[\[[^\]\n]+\]\]", parse, before="link")


def single_line_math(md) -> None:
    def parse(block, match, state):
        state.append_token({"type": "block_math", "raw": match.group("display_math_body")})
        return match.end() + 1
    md.block.register("display_math", r"^ {0,3}\$\$(?P<display_math_body>.+?)\$\$[ \t]*$", parse, before="block_math")


def render(rel: Path) -> str:
    md = mistune.create_markdown(renderer=Renderer(rel),
         plugins=["table", "strikethrough", "footnotes", "task_lists", "math", single_line_math, wikilinks])
    return md(PAGES[rel]["body"])


def section_title(folder: Path) -> str:
    return PAGES.get(folder / "index.md", {}).get("title", folder.name)


def stamp(rel: Path) -> str:
    value = PAGES[rel]["date"]
    return f'<time datetime="{value}">{date.fromisoformat(value):%b %d, %Y}</time>' if value else ""


def listing(folder: Path) -> str:
    pages = [p for p in PAGES if p.name != "index.md" and p.is_relative_to(folder)]
    pages.sort(key=lambda p: (PAGES[p]["date"], p.as_posix()), reverse=True)
    return '<ul class="items">' + "".join(
        f'<li><a href="{esc(address(p))}">{esc(PAGES[p]["title"])}</a>{stamp(p)}</li>' for p in pages
    ) + "</ul>"


def write_page(rel: Path, title: str, content: str) -> None:
    top = rel.parts[0] if len(rel.parts) > 1 else ""
    tabs = [(section_title(p), folder_url(p), top == p.name) for p in sorted(FOLDERS) if len(p.parts) == 1]
    tabs += [(PAGES[p]["title"], address(p), p == rel) for p in sorted(PAGES) if len(p.parts) == 1 and p.name != "index.md"]
    navigation = "".join(f'<a href="{esc(url)}"' + (' class="current" aria-current="location"' if active else '') + f'>{esc(label)}</a>'
                         for label, url, active in tabs)
    # Math is the only optional browser script. The header has no JavaScript.
    math = '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.1/es5/tex-svg.js"></script>' if 'class="math"' in content else ""
    page_title = NAME if rel == Path("index.md") else f"{title} — {NAME}"
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page_title)}</title><style>{CSS}</style>{math}</head>
<body><a class="skip" href="#main">Skip to content</a>
<header><div class="header"><a class="brand" href="{esc(BASE + '/')}">{esc(NAME)}</a>
<nav aria-label="Sections">{navigation}</nav></div></header>
<main id="main">{content}</main><footer>{esc(NAME)}</footer></body></html>'''
    target = rel.parent / "index.html" if rel.name == "index.md" else rel.with_suffix("") / "index.html"
    output = OUT / target
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")


def main() -> None:
    load_pages()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for rel in sorted(ASSETS):
        destination = OUT / "files" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DOCS / rel, destination)
    for folder in sorted(FOLDERS):
        rel = folder / "index.md"
        title = NAME if folder == Path(".") else section_title(folder)
        body = ("" if folder == Path(".") else f"<h1>{esc(title)}</h1>")
        body += f"<article>{render(rel)}</article>" if rel in PAGES else ""
        if folder == Path("."):
            for child in sorted(FOLDERS):
                if len(child.parts) == 1:
                    body += f'<section><h2><a href="{esc(folder_url(child))}">{esc(section_title(child))}</a></h2>{listing(child)}</section>'
        else:
            body += listing(folder)
        write_page(rel, title, body)
    for rel in sorted(PAGES):
        if rel.name == "index.md":
            continue
        title = PAGES[rel]["title"]
        parent = rel.parent
        back = f'<a class="breadcrumb" href="{esc(folder_url(parent))}">← {esc(section_title(parent))}</a>' if parent != Path(".") else ""
        content = f'{back}<h1>{esc(title)}</h1><div class="meta">{stamp(rel)}</div><article>{render(rel)}</article>'
        write_page(rel, title, content)
    (OUT / ".nojekyll").touch()
    print(f"Built {len(PAGES)} notes and {len(FOLDERS)} folder pages into _site/.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, yaml.YAMLError) as error:
        raise SystemExit(f"Website build stopped: {error}") from error
