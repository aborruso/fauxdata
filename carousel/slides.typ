#import "theme.typ": *

#set document(title: "fauxdata 0.2.0 - cosa c'è di nuovo", author: "Andrea Borruso")
#set text(lang: "it")
#set page(width: 7.5in, height: 7.5in, margin: 0in)
#set par(leading: 0.65em)

// Compilation (from this folder):
//   typst compile --font-path fonts slides.typ "output/slide-{p}.png" --ppi 144
//   typst compile --font-path fonts slides.typ output/deck.pdf

// ── 1 · Cover ─────────────────────────────────────────────────────────────
#slide({
  v(1.6fr)
  lbl[nuova release]
  v(0.15in)
  title(size: 96pt)[fauxdata]
  v(0.05in)
  title(size: 64pt, fill: AMBER, echo: rgb("#3d2b00"))[0.2.0]
  v(0.3in)
  text(size: 17pt, weight: "bold", fill: TEXT)[I tuoi dati reali ti mentono.]
  v(0.08in)
  text(size: 14pt, fill: DIM)[Quelli finti, almeno, rispettano le regole. \
  Ecco cosa c'è di nuovo.]
  v(0.35in)
  term(cmd("fauxdata --version"), out[fauxdata 0.2.0])
  v(1fr)
})

// ── 2 · What it is ────────────────────────────────────────────────────────
#slide({
  lbl[cos'è]
  v(0.2in)
  title(size: 46pt)[Dataset finti, \ realistici e validati]
  v(0.25in)
  text(size: 14pt)[Descrivi la tabella in un file YAML: colonne, tipi, vincoli, regole. fauxdata genera quante righe vuoi e le controlla con le stesse regole.]
  v(0.25in)
  item[nomi, email, città e telefoni coerenti con il paese]
  v(0.08in)
  item[CSV, Parquet, JSON e JSONL]
  v(0.08in)
  item[lo schema si può ricavare da una tabella reale]
  v(1fr)
  text(size: 11pt, fill: DIM)[Una CLI in Python, costruita su pointblank di Posit.]
})

// ── 3 · Agents ────────────────────────────────────────────────────────────
#slide({
  lbl[novità · agenti AI]
  v(0.2in)
  title(size: 46pt)[Si fa usare \ anche dagli agenti]
  v(0.25in)
  text(size: 14pt)[Un comando stampa la guida completa da far leggere all'agente. Con `--json` ogni risultato è un oggetto JSON.]
  v(0.3in)
  term(
    cmd("fauxdata agent"),
    out[\# guida in Markdown: flusso, schema, regole],
    [],
    cmd("fauxdata validate dati.csv schema.yml --json"),
    out(raw("{\"passed\": true, \"rows\": 1000, ...}")),
  )
  v(1fr)
  text(size: 11pt, fill: DIM)[`--json` su generate, validate, infer e preview.]
})

// ── 4 · Schema ────────────────────────────────────────────────────────────
#slide({
  lbl[novità · schema]
  v(0.2in)
  title(size: 46pt)[Lunghezza dei testi \ e decimali]
  v(0.25in)
  text(size: 14pt)[Una nuova regola controlla quanti caratteri ha un testo. `precision` arrotonda i decimali senza mai uscire da min e max.]
  v(0.3in)
  term(raw(block: true, "price:
  type: float
  min: 1
  max: 199.999
  precision: 2    # mai 200.00

- rule: col_vals_str_len
  column: note
  max: 80"))
})

// ── 5 · Fixes (inverted: amber) ───────────────────────────────────────────
#slide(fill: AMBER, fg: INK, muted: rgb("#5c4100"), frame: rgb("#5c4100"), code: INK, {
  lbl(fill: rgb("#5c4100"))[correzioni]
  v(0.2in)
  title(size: 46pt, fill: INK, echo: rgb("#c98d00"))[Più affidabile]
  v(0.3in)
  let fix(body) = { item(mark: INK, fill: INK, body); v(0.14in) }
  fix[i valori nulli non contano più come errori nelle regole sui valori]
  fix[`infer` da riga di comando non copia più nello schema i valori reali delle colonne di testo]
  fix[una regola su una colonna che non esiste risulta #text(weight: "bold")[NOT RUN], non superata]
  fix[i valori ammessi sono rispettati anche per le colonne numeriche]
})

// ── 6 · Try it ────────────────────────────────────────────────────────────
#slide({
  lbl[provalo]
  v(1fr)
  title(size: 64pt)[Installa \ o aggiorna]
  v(0.35in)
  term(
    cmd("uv tool install fauxdata-cli"),
    [],
    out[\# se lo hai già:],
    cmd("uv tool upgrade fauxdata-cli"),
  )
  v(0.35in)
  text(size: 14pt)[Note di rilascio e codice: \
  #text(fill: GREEN)[github.com/aborruso/fauxdata]]
  v(1fr)
})
