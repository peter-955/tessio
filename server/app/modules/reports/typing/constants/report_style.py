REPORT_STYLE = """
@page { size: A4; margin: 18mm 14mm; @bottom-right { content: counter(page) " / " counter(pages); font-size: 8pt; } }
body { font-family: "DejaVu Sans", sans-serif; font-size: 9.5pt; color: #111827; line-height: 1.4; }
h1 { font-size: 17pt; margin: 0 0 4pt; }
.subtitle { color: #4b5563; margin: 0 0 12pt; }
h2 { font-size: 12pt; margin: 16pt 0 6pt; border-bottom: 1px solid #d1d5db; padding-bottom: 2pt; }
dl.facts { display: grid; grid-template-columns: max-content auto; gap: 2pt 12pt; margin: 0 0 8pt; }
dl.facts dt { color: #4b5563; }
dl.facts dd { margin: 0; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 8pt; }
th, td { border: 1px solid #d1d5db; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
tr { page-break-inside: avoid; }
p.empty { color: #6b7280; font-style: italic; }
"""
