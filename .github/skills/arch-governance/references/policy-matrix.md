# Policy Matrix

Bruk denne matrisen når agenten vurderer commit, push og PR:

- Klasse A: `allow` for direkte PR når lokal validering er grønn
- Klasse B: `ask` før PR, og krev lokal validering
- Klasse C: `deny` for direkte PR; opprett issue først

Beskyttede områder som `motivasjon/prinsipper/`, `strategi/`, `sikkerhet/` og veikart krever alltid strengere vurdering enn vanlig dokumentasjon.
