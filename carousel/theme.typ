// fauxdata 0.2.0 - design tokens taken from docs/index.html

// — palette (CSS custom properties of the site) —
#let BG       = rgb("#050a05")
#let BG2      = rgb("#0a110a")
#let BORDER   = rgb("#1a3a1a")
#let GREEN    = rgb("#00ff41")
#let GREEN-DIM = rgb("#00b32c")
#let GREEN-DARK = rgb("#003d0d")
#let TEXT     = rgb("#c8ffc8")
#let DIM      = rgb("#7aaa7a")
#let AMBER    = rgb("#ffb300")
#let INK      = rgb("#050a05")   // text on amber

// — fonts (bundled in fonts/, compile with --font-path fonts) —
#let DISPLAY = ("VT323", "DejaVu Sans Mono")
#let MONO    = ("IBM Plex Mono", "DejaVu Sans Mono")

#let URL = "aborruso.github.io/fauxdata"

// — section label, as on the site: "// the problem" —
#let lbl(body, fill: DIM) = text(font: MONO, size: 11pt, fill: fill)[\/\/ #body]

// — big pixel title with the site's offset "echo" —
#let title(body, size: 54pt, fill: GREEN, echo: GREEN-DARK) = box({
  set text(font: DISPLAY, size: size, ligatures: false)   // VT323 "fi" ligature breaks the pixel look
  set par(leading: 0.35em)
  place(dx: 2.5pt, dy: 2.5pt, text(fill: echo, body))
  text(fill: fill, body)
})

// — terminal block: one or more lines, prompt in green —
#let term(..lines) = block(
  fill: BG2, stroke: 0.75pt + BORDER, inset: (x: 14pt, y: 12pt), width: 100%,
  {
    set text(font: MONO, size: 12pt, fill: TEXT)
    set par(leading: 0.75em)
    set smartquote(enabled: false)   // JSON quotes stay straight
    show raw: set text(fill: TEXT)   // commands in plain text colour, not the inline-code green
    lines.pos().join(linebreak())
  },
)
#let cmd(s) = [#text(fill: GREEN)[\$] #raw(s)]   // string → no "--" dash, no smart quotes
#let out(body) = { show raw: set text(fill: DIM); text(fill: DIM, body) }

// — bullet with a green ">" —
#let item(body, mark: GREEN, fill: TEXT) = grid(
  columns: (0.3in, 1fr),
  text(font: MONO, size: 14pt, weight: "bold", fill: mark)[>],
  text(font: MONO, size: 14pt, fill: fill, body),
)

// — card: full-bleed, thin frame, counter top right, URL bottom left —
#let slide(fill: BG, fg: TEXT, muted: DIM, frame: BORDER, code: GREEN, body) = page(fill: fill, {
  set text(font: MONO, fill: fg)
  show raw: set text(font: MONO, size: 1.25em, fill: code)   // raw is scaled to 0.8em by default: 0.8 × 1.25 = 1
  place(top + left, dx: 0.28in, dy: 0.28in,
    rect(width: 7.5in - 0.56in, height: 7.5in - 0.56in, stroke: 0.75pt + frame))
  place(top + right, dx: -0.6in, dy: 0.55in, context text(size: 11pt, fill: muted,
    [#counter(page).display("01") / #numbering("01", counter(page).final().first())]))
  place(bottom + left, dx: 0.6in, dy: -0.52in, text(size: 11pt, fill: muted, URL))
  block(
    width: 100%, height: 100%,
    inset: (left: 0.6in, right: 0.6in, top: 0.55in, bottom: 0.95in),
    body,
  )
})
