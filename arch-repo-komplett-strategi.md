# Arch-Repo: Komplett strategi for agentstyrt felles arkitektur

> Versjon: 1.0 — 2026-03-31
> Strukturert etter ArchiMate 3.2, optimalisert for AI-agenter

---

## 1. Oversikt

### Hva er dette?

`myorg/arch` er et sentralt Git-repo som fungerer som "grunnlov" for alle
tjenesterepos i organisasjonen. Det inneholder arkitekturbeslutninger,
kontrakter, standarder og retningslinjer — strukturert slik at AI-agenter
kan lese, foreslå endringer via issues, og levere konkrete endringer via PRs.
Alle normative arkitekturdokumenter ligger under `docs/arkitektur/`.

### Designprinsipper

1. **ArchiMate-lagdeling** — Alle dokumenter er organisert etter ArchiMate 3.2
   sine lag, fra motivasjon til fysisk, med sikkerhet som tverrgående lag.

2. **Agent-først dokumentstruktur** — Hvert dokument starter med et kompakt
   agent-sammendrag som gir alt en agent trenger i 10–20 linjer.

3. **Mål og løsning i samme dokument** — Ingen duplisering. Mål- og
   løsningsarkitektur er seksjoner i samme fil, ikke separate mapper.

4. **Lesenivåer** — Agenter velger dybde etter oppgave:
   INDEX → Sammendrag → Løsning → Mål (eskalerende kontekstkostnad).

5. **Issues og PRs som kommunikasjon** — Agenter endrer aldri arch-repo
   direkte, men kommuniserer via issues (vagt behov) og PRs (konkret forslag).

6. **Sikkerhet gjennomgående** — Ikke et ettertanke, men et eget tverrgående
   lag med per-lag konkretiseringer.

---

## 2. ArchiMate-lagene

```
┌─────────────────────────────────────────────────────────┐
│                    MOTIVASJON [M]                        │
│         Interessenter, drivere, mål, prinsipper         │  ╔═══════════╗
├─────────────────────────────────────────────────────────┤  ║           ║
│                     STRATEGI [S]                        │  ║           ║
│           Kapabiliteter, ressurser, verdistrømmer       │  ║ SIKKERHET ║
├─────────────────────────────────────────────────────────┤  ║   [Sik]   ║
│                   FORRETNING [F]                        │  ║           ║
│         Prosesser, roller, tjenester, regelverk         │  ║ Tverr-    ║
├─────────────────────────────────────────────────────────┤  ║ gående    ║
│                   INFORMASJON [I]                       │  ║ gjennom   ║
│       Datamodeller, begreper, FHIR, informasjonsflyt    │  ║ alle lag  ║
├─────────────────────────────────────────────────────────┤  ║           ║
│                   APPLIKASJON [A]                       │  ║           ║
│        API-kontrakter, integrasjon, events              │  ║           ║
├─────────────────────────────────────────────────────────┤  ║           ║
│                    TEKNOLOGI [T]                        │  ║           ║
│       Plattform, infrastruktur, deploy, standarder      │  ║           ║
├─────────────────────────────────────────────────────────┤  ║           ║
│                     FYSISK [Fy]                         │  ║           ║
│        Hardware, enheter, nettverk, ESP32               │  ║           ║
├─────────────────────────────────────────────────────────┤  ╚═══════════╝
│              IMPLEMENTASJON & MIGRASJON [IM]            │
│       Veikart, arbeidspakker, leveranser, gap-analyse   │
└─────────────────────────────────────────────────────────┘
```

| Tag | Lag | Spørsmål | Endringstakt | Primært mål/løsning |
|-----|-----|----------|-------------|---------------------|
| `[M]` | Motivasjon | Hvorfor gjør vi dette? | Sjelden | Mål |
| `[S]` | Strategi | Hva kan og vil vi? | Kvartalsvis | Mål |
| `[F]` | Forretning | Hvem gjør hva? | Månedlig | Miks |
| `[I]` | Informasjon | Hvilke data? | Ukentlig | Løsningstung |
| `[A]` | Applikasjon | Hvilke systemer? | Ukentlig | Løsningstung |
| `[T]` | Teknologi | Hvilken plattform? | Månedlig | Løsning |
| `[Fy]` | Fysisk | Hvilken hardware? | Sjelden | Løsning |
| `[Sik]` | Sikkerhet | Er det trygt? | Ved enhver endring | Miks |
| `[IM]` | Impl. & Migrasjon | Når og hvordan? | Løpende | Miks |

---

## 3. Mål- vs. løsningsarkitektur

### Problemet

Agenter har begrenset kontekstvindu. Hvis de leser hele målarkitekturen
(as-is, to-be, gap, prinsipper) for å implementere ett FHIR-endpoint,
kaster de bort tokens. Samtidig trenger vi målarkitekturen for konsistens.

### Løsningen: Lesenivåer

Mål og løsning bor i **samme dokument**, men agenter styres til riktig
dybde via `arch-read`-scriptet og tydelige seksjoner:

```
┌─────────────────────────────────────────────────┐
│ Nivå 1: INDEX.md            ~500 tokens per lag │ ← Orientering
├─────────────────────────────────────────────────┤
│ Nivå 2: Agent-sammendrag    ~200 tokens per dok │ ← De fleste oppgaver
├─────────────────────────────────────────────────┤
│ Nivå 3: Løsningsarkitektur  ~500 tokens per dok │ ← Implementasjon
├─────────────────────────────────────────────────┤
│ Nivå 4: Målarkitektur       ~500 tokens per dok │ ← Arkitekturendringer
└─────────────────────────────────────────────────┘
```

### Dokumentformat

Hvert dokument i arch-repo følger denne strukturen:

```markdown
# <Tittel>

## Agent-sammendrag
<!-- Maks 20 linjer. Alt en agent trenger. Kan leses isolert. -->

## Løsningsarkitektur
<!-- Konkret: Typer, eksempler, konfigurasjon, regler.
     Det agenten trenger for å skrive kode. -->

## Målarkitektur
<!-- Strategisk: As-is, to-be, gap, prinsipper.
     Agenten leser dette kun ved arkitekturforslag. -->

## Referanser
<!-- Lenker til ADRs og relaterte dokumenter -->
```

### Dokumentkontrakt for maskinlesbarhet

For at `arch-read`, validering og automatisering skal være deterministisk,
gjelder disse kravene for alle arkitekturdokumenter:

1. Eksakte H2-overskrifter: `## Agent-sammendrag`, `## Løsningsarkitektur`,
  `## Målarkitektur`, `## Referanser`.
2. Ingen synonymer i normal drift. Overskrifter som `Summary`, `TL;DR` og
  `Sammendrag` brukes kun i en eksplisitt migrasjonsperiode.
3. Én H1 per fil, og H2-seksjonene skal komme i fast rekkefølge.
4. H3-overskrifter skal være unike innenfor samme H2-seksjon.
5. Filstier i eksempler og registry er alltid relative til repo-roten.
6. Nye dokumenter skal legges inn i riktig `INDEX.md` i samme PR.
7. Dokumenter som bryter kontrakten skal feile i CI; verktøyene skal ikke
  skjule strukturfeil med heuristikker i normal modus.

### Egenskaper

| Egenskap | Målarkitektur | Løsningsarkitektur |
|----------|---------------|-------------------|
| Spørsmål | Hvor skal vi? | Hvordan bygger vi det? |
| Perspektiv | Strategisk, overordnet | Konkret, implementasjonsnært |
| Målgruppe | Arkitekter, ledelse | Agenter, utviklere |
| Endringstakt | Kvartalsvis/årlig | Ukentlig/daglig |
| Detaljeringsnivå | Konseptuelt → logisk | Logisk → fysisk |
| ArchiMate-mapping | ABB (Architecture Building Block) | SBB (Solution Building Block) |
| Kontekstkostnad | Høy (500–2000 tokens) | Lav–middels (200–500 tokens) |
| Agent leser dette når | Foreslår arkitekturendring | Implementerer funksjon |

---

## 4. `arch-read` — Verktøy for konteksteffektiv lesing

Scriptet `scripts/arch-read.sh` gir agenter (og mennesker) presise
uttrekk fra arch-repo-dokumenter uten å fylle kontekstvinduet.

### Bruk

```bash
# Nivå 1: Vis INDEX for et lag
arch-read --index informasjon

# Nivå 2: Hent agent-sammendrag (default)
arch-read docs/arkitektur/informasjon/fhir/consent.md

# Nivå 3: Sammendrag + løsningsarkitektur
arch-read docs/arkitektur/informasjon/fhir/consent.md --løsning

# Nivå 4: Sammendrag + målarkitektur
arch-read docs/arkitektur/informasjon/fhir/consent.md --mål

# Full: Hele dokumentet
arch-read docs/arkitektur/informasjon/fhir/consent.md --full

# Spesifikk seksjon (fuzzy match, h2 og h3)
arch-read docs/arkitektur/informasjon/fhir/consent.md --seksjon "Events"
arch-read docs/arkitektur/informasjon/fhir/consent.md --seksjon "Datamodell"

# Søk i alle agent-sammendrag
arch-read --search "MedicationRequest"
arch-read --search "break-the-glass"

# Token-estimat per seksjon
arch-read docs/arkitektur/informasjon/fhir/consent.md --tokens

# Valider at dokumentet følger kontrakten
arch-read docs/arkitektur/informasjon/fhir/consent.md --check

# List tilgjengelige lag
arch-read --list
```

### Hvordan det fungerer

Scriptet parser markdown-strukturen med en fast dokumentkontrakt og feiler
tydelig når strukturen ikke stemmer:

- **Agent-sammendrag**: Henter alt mellom `## Agent-sammendrag` og neste `##`.
  Ingen alternative overskrifter i normal modus.

- **Løsningsarkitektur**: Henter `## Løsningsarkitektur`-seksjonen inkludert
  alle underseksjoner (`###`).

- **Fuzzy seksjonssøk**: `--seksjon` matcher delvis mot både `##` og `###`
  overskrifter, og respekterer hierarkiet (stopper ved neste seksjon på
  samme eller høyere nivå).

- **Søk**: Itererer over alle `.md`-filer, henter agent-sammendrag fra hver,
  og grepper etter søkeordet.

- **Kontraktssjekk**: `--check` verifiserer overskriftsrekkefølge, manglende
  seksjoner, duplikate overskrifter og ugyldige seksjonsnavn.

- **Migrasjonsmodus**: Eventuelle heuristikker eller gamle overskrifter støttes
  kun bak en eksplisitt `--legacy`-modus i overgangsperioder.

### Installasjon i tjenesterepos

Legg til i AGENTS.md:

```markdown
## Verktøy

arch-read er tilgjengelig for effektiv lesing av arch-repo:

    export ARCH_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/myorg/arch"
    if [ ! -d "$ARCH_DIR/.git" ]; then
        git clone --depth 1 https://github.com/myorg/arch.git "$ARCH_DIR"
    else
        git -C "$ARCH_DIR" pull --ff-only
    fi
    export PATH="$PATH:$ARCH_DIR/scripts"
```

---

## 5. Mappestruktur

```
myorg/arch/
├── AGENTS.md
├── README.md
├── CODEOWNERS
│
├── docs/
│   └── arkitektur/
│       ├── motivasjon/                  # [M] — HVORFOR
│       ├── strategi/                    # [S] — HVA VI KAN OG VIL
│       ├── forretning/                  # [F] — FORRETNINGSPROSESSER
│       ├── informasjon/                 # [I] — DATA OG BEGREPER
│       ├── applikasjon/                 # [A] — APPLIKASJONER OG API
│       ├── teknologi/                   # [T] — PLATTFORM OG INFRASTRUKTUR
│       ├── fysisk/                      # [Fy] — HARDWARE OG ENHETER
│       ├── sikkerhet/                   # [Sik] — TVERRGÅENDE SIKKERHET
│       ├── impl-migrasjon/              # [IM] — VEIKART OG MIGRERING
│       ├── adrs/
│       ├── views/
│       └── registry/
│
├── templates/
│   ├── service/
│   │   ├── AGENTS.md.tmpl
│   │   ├── Dockerfile.tmpl
│   │   └── ci.yml.tmpl
│   └── adr/
│       └── template.md
│
├── scripts/
│   ├── arch-read.sh                     # Konteksteffektiv leser
│   ├── arch-sync.sh                     # Synkronisering til tjenesterepos
│   ├── create-adr.sh                    # Opprett ny ADR
│   ├── validate-docs.sh                 # Valider dokumentkontrakt
│   ├── find-affected-services.sh        # Finn berørte tjenester fra registry
│   └── arch-policy.sh                   # Felles policy-motor for hooks og CI
│
└── .github/
    ├── hooks/
    │   └── arch-policy.json
    ├── skills/
    │   ├── arch-consume/
    │   │   ├── SKILL.md
    │   │   ├── scripts/
    │   │   │   ├── resolve-context.sh
    │   │   │   └── classify-impact.sh
    │   │   └── references/
    │   │       └── reading-order.md
    │   ├── arch-escalate/
    │   │   ├── SKILL.md
    │   │   ├── scripts/
    │   │   │   ├── create-arch-issue.sh
    │   │   │   └── prepare-arch-pr.sh
    │   │   └── references/
    │   │       └── change-classes.md
    │   └── arch-governance/
    │       ├── SKILL.md
    │       ├── scripts/
    │       │   ├── pre-tool-gate.sh
    │       │   ├── post-tool-validate.sh
    │       │   └── require-issue-link.sh
    │       └── references/
    │           └── policy-matrix.md
    ├── ISSUE_TEMPLATE/
    │   ├── arch-request.md
    │   ├── arch-proposal.md
    │   └── cross-repo-need.md
    ├── PULL_REQUEST_TEMPLATE/
    │   └── arch-change.md
    └── workflows/
        ├── validate-adr.yml
        ├── notify-services.yml
        └── label-triage.yml
```

---

## 6. AGENTS.md — Spillereglene

```markdown
# Agentregler for myorg/arch

## Arkitekturlagene

Repoet følger ArchiMate 3.2 pluss Sikkerhet som tverrgående lag:

  docs/arkitektur/motivasjon/       [M]   — Hvorfor: Drivere, mål, prinsipper
  docs/arkitektur/strategi/         [S]   — Hva vi kan: Kapabiliteter, verdistrømmer
  docs/arkitektur/forretning/       [F]   — Hvem og hva: Prosesser, roller, regelverk
  docs/arkitektur/informasjon/      [I]   — Hvilke data: Modeller, begreper, FHIR
  docs/arkitektur/applikasjon/      [A]   — Hvilke systemer: API, integrasjon, events
  docs/arkitektur/teknologi/        [T]   — Hvilken plattform: Infra, deploy, standarder
  docs/arkitektur/fysisk/           [Fy]  — Hvilken hardware: ESP32, sensorer, nettverk
  docs/arkitektur/sikkerhet/        [Sik] — Tverrgående: AuthN, AuthZ, personvern
  docs/arkitektur/impl-migrasjon/   [IM]  — Når: Veikart, arbeidspakker, gap-analyse

## Verktøy

    export ARCH_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/myorg/arch"
    if [ ! -d "$ARCH_DIR/.git" ]; then
        git clone --depth 1 https://github.com/myorg/arch.git "$ARCH_DIR"
    else
        git -C "$ARCH_DIR" pull --ff-only
    fi
    export PATH="$PATH:$ARCH_DIR/scripts"

## Hvordan lese — Lesenivåer

Bruk arch-read for konteksteffektiv lesing:

**Nivå 1 — Orientering** (~500 tokens per lag)
    arch-read --index informasjon

**Nivå 2 — Agent-sammendrag** (~200 tokens per dokument)
  arch-read docs/arkitektur/informasjon/fhir/consent.md

**Nivå 3 — Implementasjonsdetaljer** (~500-1000 tokens)
  arch-read docs/arkitektur/informasjon/fhir/consent.md --løsning

**Nivå 4 — Full kontekst** (hele dokumentet)
  arch-read docs/arkitektur/informasjon/fhir/consent.md --full

**Søk** — Finn relevante dokumenter
    arch-read --search "MedicationRequest"

### Tommelfingerregel
- Skriver du kode? → Nivå 2 (sammendrag) + Nivå 3 (løsning)
- Foreslår du arkitekturendring? → Nivå 4 (alt)
- Orienterer du deg? → Nivå 1 (INDEX)

## Navigeringsregler

Les **ovenfra og ned** for kontekst:
Motivasjon → Strategi → Forretning → Informasjon → Applikasjon →
Teknologi → Fysisk

Les **nedenfra og opp** for påvirkningsanalyse.

Les **sikkerhet alltid** — sjekk docs/arkitektur/sikkerhet/per-lag/<ditt-lag>.md.

### Minimum lesing per oppgavetype

| Oppgavetype | Les disse lagene |
|-------------|-----------------|
| Ny forretningsfunksjon | M → S → F → I → A → Sik |
| Ny integrasjon | A → I → T → Sik |
| Ny FHIR-ressurs | I → F (kontekst) → A (kontrakt) → Sik |
| Infrastrukturendring | T → A (påvirkning) → Sik |
| Ny fysisk enhet | Fy → T → A → Sik |
| Sikkerhetsendring | Sik → alle berørte lag |
| Ny tjeneste (komplett) | Alle lag |

## Hva som hører hjemme i arch-repo

Dette repoet skal være felles styringsgrunnlag, ikke en sekundær backlog eller
et speil av tjenesterepoene.

**Hører hjemme i arch-repo:**
- Delte kontrakter, profiler og kanoniske modeller
- Prinsipper, standarder og beslutninger som berører flere repos eller team
- Sikkerhetskrav og plattformkrav som skal håndheves konsekvent
- Vertikale views, ADRs og registry-mapping som brukes til koordinering

**Hører ikke hjemme i arch-repo:**
- Tjenestespesifikke implementasjonsdetaljer uten gjenbruksverdi
- Midlertidige workarounds og lokale deploy-notater
- Backlog-punkter uten arkitekturkonsekvens
- Regelverkstolkning som ikke er faglig eller juridisk kvalitetssikret

## Når du oppdager et behov

### Nivå 1: Spørsmål → Issue

Bruk når du er usikker eller trenger avklaring.

    gh issue create \
      --repo myorg/arch \
      --template arch-request.md \
      --title "[I] Trenger avklaring: <beskrivelse>" \
      --label "arch-request,auto-agent,lag-informasjon"

### Nivå 2: Konkret endring → Pull Request

Bruk når du kan levere en komplett endring.

    # 1. Branch
    git checkout -b agent/<ditt-repo>/<lag>/<beskrivelse>

    # 2. Gjør endringene — følg dokumentformatet:
    #    ## Agent-sammendrag → ## Løsningsarkitektur → ## Målarkitektur

    # 3. Commit
    git commit -m "arch: <lag>(<scope>): <beskrivelse>

    Foreslått av agent i <repo>.
    Kontekst: <kort forklaring>"

    # 4. PR
    gh pr create \
      --repo myorg/arch \
      --title "[<lag-tags>] <beskrivelse>" \
      --label "arch-proposal,auto-agent,lag-<lag>"

### Nivå 3: Tverrgående → Koordinert

Endringer som krysser lag eller repos:

    # 1. Koordinerings-issue i arch
    gh issue create \
      --repo myorg/arch \
      --template cross-repo-need.md \
      --title "[F][I][A] cross-layer: <beskrivelse>" \
      --label "cross-repo,cross-layer,auto-agent"

    # 2. PR i arch med endringene
    # 3. Issues i berørte repos som refererer tilbake

## Tags og labels

### Lag-tags i titler
    [I] Ny MedicationRequest-type
    [F][I][Sik] Samtykkemodell for nektelse
    [Sik][A][T] Innfør mutual TLS

### GitHub-labels
    lag-motivasjon, lag-strategi, lag-forretning, lag-informasjon,
    lag-applikasjon, lag-teknologi, lag-fysisk, lag-sikkerhet,
    lag-impl-migrasjon, cross-layer

### Branch-konvensjoner
    agent/<kilde-repo>/<lag>/<beskrivelse>

### Commit-meldinger
    arch: <lag>(<scope>): <beskrivelse>

## Review-prosess

| Endring | Review-krav |
|---------|-------------|
| Motivasjon / Strategi | Alltid manuell (menneske) |
| Enkelt lag, non-breaking | 1 review fra lag-eier |
| Enkelt lag, breaking | 2 reviews |
| Sikkerhetslag | Sikkerhetsansvarlig + 1 |
| Cross-layer (3+ lag) | 1 review per berørt lag |
| Forretning + regelverk | Juridisk/faglig review |

## Hva agenter IKKE skal gjøre

- Merge egne PRs
- Endre AGENTS.md eller docs/arkitektur/motivasjon/prinsipper/
- Slette ADRs (de kan supersedes, aldri slettes)
- Endre sikkerhetsarkitektur uten [Sik]-tag og dedikert review
- Endre regelverk-tolkninger uten manuell review
- Oppdatere veikart uten koordinering
```

### Kontrollkjede: Skill → Hook → GitHub Actions

Riktig arbeidsflyt håndheves i tre nivåer, med ulik rolle:

1. **Skills** velger riktig prosedyre og hjelper agenten å gjøre det rette.
2. **Hooks i VS Code og Copilot CLI** stopper eller ber om bekreftelse før
  commit, push eller PR-opprettelse.
3. **GitHub Actions** er siste og autoritative kontroll ved PR og merge.

Prinsippet er at samme policy brukes gjennom hele kjeden. Skills skal ikke ha
sin egen logikk for hva som er lov; de skal kalle de samme sjekkene som hooks
og CI bruker. Skill-mappene kan inneholde oppgaveorienterte scripts, men
policy-avgjørelser som må være konsistente på tvers av skills og CI bør ligge
samlet i `scripts/arch-policy.sh` eller tilsvarende delt modul.

I praksis bør hooks kalle `sh`-scripts direkte. Hvis man senere trenger rikere
logikk bak kulissene, skal også den nås via et `sh`-entrypoint slik at verken
VS Code, Copilot CLI eller lokale virtual environments styrer arbeidsflyten.

### Anbefalte skills

| Skill | Hvor brukes den? | Hovedansvar |
|------|-------------------|-------------|
| `arch-consume` | Løsningsrepo | Les riktig arkitektur, velg lag, sjekk sikkerhet og registry-mapping |
| `arch-escalate` | Løsningsrepo | Opprett issue som default, eller forbered PR når endringen er konkret og tillatt |
| `arch-governance` | Arkitekturrepo | Valider dokumentkontrakt, tagger, registry, påvirkning og review-rute |

### Autonomi for direkte PR fra agent

Agenter bør få friere tøyler til å lage direkte PR når de allerede har kontekst,
men ikke uten klassifisering og lokal gating.

| Endringsklasse | Eksempler | Skill-adferd | Hook-beslutning | Videre flyt |
|----------------|----------|--------------|-----------------|-------------|
| Klasse A: Lav risiko | Presiseringer, eksempler, INDEX, additive dokumentlenker, registry-oppdatering etter etablert mønster | Forbered PR direkte | `allow` | PR kan opprettes direkte |
| Klasse B: Moderat risiko | Nye additive typer, profiler, standardutvidelser, non-breaking kontraktsforbedringer | Forbered PR, men krev eksplisitt vurdering | `ask` | PR kan opprettes etter lokal bekreftelse og beståtte sjekker |
| Klasse C: Høy risiko | Prinsipper, strategi, sikkerhetsarkitektur, regelverkstolkning, breaking changes, cross-layer med organisatorisk påvirkning | Opprett issue, ikke PR | `deny` | Issue først, eventuelt koordinert PR senere |

### Standardregel for løsningsrepo

I løsningsrepo skal agenten følge denne regelen:

1. Les sentral arkitektur via `arch-consume`.
2. Hvis behovet kan dekkes lokalt uten å endre normativ arkitektur, gjør
  endringen lokalt og dokumenter eventuelt avvik.
3. Hvis sentral arkitektur mangler noe, bruk `arch-escalate`.
4. `arch-escalate` oppretter issue som default.
5. Direkte PR til arkitekturrepo er bare tillatt for klasse A og i noen tilfeller
  klasse B, når hookene ikke blokkerer og lokal validering er grønn.

### Standardregel for arkitekturrepo

I arkitekturrepo skal `arch-governance` være obligatorisk ved alle endringer som
berører dokumentkontrakt, registry, ADR-er eller sikkerhetsdokumenter.

Hooks skal her være strengere enn i løsningsrepo, fordi repoet er normativt.
Det betyr spesielt:

- `ask` eller `deny` ved forsøk på PR mot beskyttede områder
- `deny` hvis dokumentkontrakt eller registry ikke validerer
- `ask` hvis endringen er klasse B og `deny` hvis den er klasse C uten issue

---

## 7. Templates

### ADR-template

```markdown
# ADR-NNNN: <Tittel>

## Agent-sammendrag
<!-- 2-4 setninger: Hva ble besluttet og hvorfor. -->

## Lag
- [ ] [M] Motivasjon
- [ ] [S] Strategi
- [ ] [F] Forretning
- [ ] [I] Informasjon
- [ ] [A] Applikasjon
- [ ] [T] Teknologi
- [ ] [Fy] Fysisk
- [ ] [Sik] Sikkerhet
- [ ] [IM] Implementasjon & Migrasjon

## Status
Foreslått | Akseptert | Superseded av ADR-XXXX | Avvist

## Dato
YYYY-MM-DD

## Kontekst
<!-- Fra høyeste berørte lag og nedover. Slett irrelevante. -->

### Motivasjon og strategi
### Forretningskontekst
### Informasjonskontekst
### Applikasjonskontekst
### Teknologi- og fysisk kontekst
### Sikkerhetskontekst

## Beslutning

## Konsekvenser per lag

### Sikkerhet
<!-- PÅKREVD for alle ADRs -->

### Implementasjon & Migrasjon
<!-- Hva kreves for å realisere dette? -->

## Berørte tjenester
## Foreslått av
```

### PR-template

```markdown
## Lag
- [ ] [M] Motivasjon
- [ ] [S] Strategi
- [ ] [F] Forretning
- [ ] [I] Informasjon
- [ ] [A] Applikasjon
- [ ] [T] Teknologi
- [ ] [Fy] Fysisk
- [ ] [Sik] Sikkerhet
- [ ] [IM] Implementasjon & Migrasjon

## Type endring
- [ ] Ny/oppdatert ADR
- [ ] Ny/endret datamodell eller type
- [ ] Ny/endret API-kontrakt
- [ ] Ny/endret standard
- [ ] Sikkerhetsendring
- [ ] Infrastruktur/plattform
- [ ] Veikart/migrasjonsplan

## Opprinnelse
- **Repo:**
- **Agent/Person:**
- **Relatert issue:** #

## Endringer
## Begrunnelse

## Påvirkning
- **Repos:** 
- **Breaking change:** ja / nei
- **Krever migrasjon:** ja / nei

## Sjekkliste
- [ ] Lag er riktig tagget
- [ ] Agent-sammendrag oppdatert i berørte dokumenter
- [ ] Sikkerhetskonsekvenser vurdert
- [ ] ADR inkludert (hvis arkitekturbeslutning)
- [ ] INDEX.md oppdatert (hvis nye/slettede dokumenter)
```

### Issue-templates

**arch-request.md:**
```markdown
---
name: Arkitekturforespørsel
about: Spørsmål, vagt behov, eller idé som krever diskusjon
labels: arch-request
---

## Lag: <!-- [F], [I], [A], [T], [Fy], [Sik], [M], [S], [IM] -->
## Kontekst
- **Repo:** 
- **Opprettet av:** 
- **Oppgave:** 

## Behov
## Haster?
- [ ] Blokkerer pågående arbeid
- [ ] Ønskelig, men ikke blokkerende
- [ ] Langsiktig forbedring
```

**cross-repo-need.md:**
```markdown
---
name: Tverrgående behov
about: Endring som krever koordinering på tvers av repos
labels: cross-repo
---

## Lag: <!-- Hvilke lag berøres? -->
## Berørte repos
| Repo | Lag | Type endring | Omfang |
|------|-----|-------------|--------|

## Foreslått rekkefølge
## Arkitekturendring i arch-repo
## Migrasjonsstrategi
## Sikkerhetskonsekvenser
## Risiko
```

---

## 8. Sikkerhet som tverrgående lag

Sikkerhet gjennomtrenger alle ArchiMate-lag. I stedet for å spre
sikkerhetsdokumentasjon utover hvert lag, samler vi den i
`docs/arkitektur/sikkerhet/` med eksplisitte koblinger via
`docs/arkitektur/sikkerhet/per-lag/`.

### Per-lag sikkerhetsdokumenter

Hver `per-lag/`-fil følger dette formatet:

```markdown
# Sikkerhet i <lag>-laget

## Agent-sammendrag
<!-- Kort: Hva MÅ agenten vite om sikkerhet i dette laget? -->

## Krav og kontroller
<!-- Konkrete regler agenten skal følge -->

## Kobling til andre lag
<!-- Lenker til relaterte sikkerhetsdokumenter -->
```

### Horisontalt view

```
| Lag        | Sikkerhetstiltak                       | Ansvarlig    |
|------------|---------------------------------------|--------------|
| [M]        | Sikkerhetsprinsipper, compliance-mål   | Arkitekt     |
| [S]        | Sikkerhet som kapabilitet              | Ledelse      |
| [F]        | Roller, ansvar, DPIA, compliance       | PVO          |
| [I]        | Dataklassifisering, security labels    | Utvikler+PVO |
| [A]        | AuthN, AuthZ, input-validering, API    | Utvikler     |
| [T]        | TLS, secrets, nettverkssegmentering    | Ops          |
| [Fy]       | Secure boot, firmware-signing, BLE     | HW-utvikler  |
```

---

## 9. Vertikale views

Views viser hvordan én funksjon realiseres gjennom alle lag.

### Eksempel: Samtykke

```
[M]  Pasientrettigheter, GDPR, Pasientjournalloven
 └→ [S]  Kapabilitet: Samtykkeforvaltning
     └→ [F]  Prosess: Gi/endre/trekke samtykke
         └→ [I]  FHIR Consent med norsk profil
             └→ [A]  Consent API (service-b), event PatientConsentChanged
                 └→ [T]  Aidbox med AccessPolicy, Railway
[Sik]  HelseID autentisering → LBAC → security labels → audit log
[IM]   WP-002: Grunnleggende samtykke → Full nektelsesmodell
```

---

## 10. Registry med lag-mapping

### `docs/arkitektur/registry/services.yaml`

Registry skal være maskinlesbar kontrakt mellom arch-repo og tjenesterepoene.
Derfor gjelder disse reglene:

1. Hver sti i `lag-mapping` er relativ til roten av det angitte laget.
2. Et lag kan bare peke til dokumenter i sitt eget lag.
3. Krysskoblinger mellom lag uttrykkes med flere lagoppføringer, ikke ved å
  legge sikkerhetsdokumenter under applikasjonslaget eller lignende.
4. Alle registry-referanser skal valideres mot eksisterende filer i CI.
5. Nye tjenester skal ikke bare registreres; de skal også ha eierskap,
  språk, agentstøtte og minst ett dokument i hvert relevant lag.

```yaml
services:
  service-a:
    repo: myorg/service-a
    description: Medikasjonstjeneste
    language: typescript
    lag-mapping:
      forretning:
        - prosesser/medikasjonsrekvirering
      informasjon:
        - fhir/medication-request
        - fhir/types
      applikasjon:
        - api/fhir-api-profil
        - events/schemas
      teknologi:
        - plattform/aidbox
        - standarder/typescript
      sikkerhet:
        - per-lag/applikasjon-sikkerhet
        - autorisasjon/security-labels
    owners: [hans-arne]
    agents: [claude-code]

  service-b:
    repo: myorg/service-b
    description: Samtykke- og journaltjeneste
    language: typescript
    lag-mapping:
      forretning:
        - prosesser/pasientsamtykke
        - regelverk/pasientjournalloven
      informasjon:
        - fhir/consent
        - fhir/types
      applikasjon:
        - tjenester/service-b
        - api/fhir-api-profil
      teknologi:
        - plattform/aidbox
      sikkerhet:
        - autorisasjon/break-the-glass
        - autorisasjon/tilgangskontrollmodell
        - personvern/samtykkehaandtering
    owners: [collaborator]
    agents: [aider]

  boat-controller:
    repo: myorg/boat-controller
    description: ESP32-basert digital sikring for båt
    language: c/cpp
    lag-mapping:
      fysisk:
        - enheter/esp32-plattform
        - enheter/sensorer
        - nettverk/kommunikasjonsprotokoll
      teknologi:
        - standarder/error-handling
      sikkerhet:
        - per-lag/fysisk-sikkerhet
    owners: [hans-arne]
    agents: [claude-code]
```

---

## 11. GitHub Actions: Varsling og validering

Før GitHub Actions kjører, skal de samme policyene allerede ha vært vurdert
lokalt via hooks. Actions er ikke første forsvarslinje, men siste.

### Hooks i VS Code og Copilot CLI

Hooks brukes til raske, deterministiske sjekker før agenten kommer til commit,
push eller PR-opprettelse. De skal være korte, auditerbare og kalle samme
policylogikk som CI.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "sh .github/skills/arch-consume/scripts/resolve-context.sh",
        "timeout": 10
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "command": "sh .github/skills/arch-governance/scripts/pre-tool-gate.sh",
        "timeout": 10
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "sh .github/skills/arch-governance/scripts/post-tool-validate.sh",
        "timeout": 20
      }
    ]
  }
}
```

### Hva hookene skal gjøre

| Hook-event | Ansvar | Typiske reaksjoner |
|-----------|--------|--------------------|
| `SessionStart` | Sikre at `ARCH_DIR` er tilgjengelig og at nødvendig skill-kontekst kan lastes | Kun `allow` eller informativ melding |
| `PreToolUse` | Klassifisere endringen og stoppe risikable handlinger før de skjer | `allow`, `ask` eller `deny` |
| `PostToolUse` | Kjør raske valideringer når relevante filer er endret | Feil ved kontraktsbrudd, ellers fortsett |

### Konkrete regler for `PreToolUse`

Hooken skal inspisere verktøykallet og nåværende git-diff og bruke policy-motoren
til å bestemme `allow`, `ask` eller `deny`.

Den bør minimum håndheve dette:

1. Ved `gh pr create --repo myorg/arch`:
   `deny` for klasse C, `ask` for klasse B, `allow` for klasse A.
2. Ved `git push` fra arkitekturrepo:
   `deny` hvis lokal validering ikke er kjørt eller feiler.
3. Ved edits i beskyttede områder som `docs/arkitektur/motivasjon/prinsipper/`
  eller `docs/arkitektur/sikkerhet/`:
   `ask` eller `deny` avhengig av endringsklasse og issue-referanse.
4. Ved endring av delte kontrakter eller registry:
   krev lokal kjøring av dokument- og registry-sjekker før commit eller PR.

### Konkrete regler for `PostToolUse`

Hooken skal kjøre bare når relevante filer er endret, for å holde flyten rask.

```bash
# .github/skills/arch-governance/scripts/post-tool-validate.sh
changed_files=$(git diff --name-only --cached HEAD 2>/dev/null || git diff --name-only)

echo "$changed_files" | grep -Eq '(^|/)(docs/arkitektur/registry/|docs/arkitektur/adrs/|docs/arkitektur/.*\.md$)' || exit 0

./scripts/validate-docs.sh
sh ./scripts/find-affected-services.sh --registry docs/arkitektur/registry/services.yaml --validate-only
```

### Eksempel: policy-script for `PreToolUse`

```sh
# scripts/arch-policy.sh
pre_tool() {
  payload=$(cat)
  compact_payload=$(printf '%s' "$payload" | tr '\n' ' ')
  change_class=$(classify_change)

  if printf '%s' "$compact_payload" | grep -Fq 'gh pr create' \
    && printf '%s' "$compact_payload" | grep -Fq 'myorg/arch'; then
    case "$change_class" in
      C)
        emit_pretool_decision "deny" "Klasse C-endring krever issue og koordinering før PR"
        return 0
        ;;
      B)
        emit_pretool_decision "ask" "Klasse B-endring krever eksplisitt vurdering før PR"
        return 0
        ;;
    esac
  fi

  emit_pretool_decision "allow" "Ingen policy-blokkering"
```

### Hvor logikken skal bo

Skillene skal inneholde prosedyre og oppgaveorienterte scripts. Hooks og CI skal
kalle en felles policy-motor, slik at klassifisering og kontroll ikke divergerer.

- Skill-spesifikke scripts: `.github/skills/<skill>/scripts/`
- Delt policy-logikk: `scripts/arch-policy.sh`
- Hook-konfig: `.github/hooks/arch-policy.json`
- Server-side håndheving: `.github/workflows/*.yml`

### Varsle berørte repos ved merge

```yaml
# .github/workflows/notify-services.yml
name: Varsle berørte tjenester
on:
  pull_request:
    types: [closed]
jobs:
  notify:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Finn endrede filer
        id: affected
        run: |
          gh api repos/${{ github.repository }}/pulls/${{ github.event.pull_request.number }}/files \
            --paginate \
            --jq '.[].filename' > changed-files.txt
          sh scripts/find-affected-services.sh \
            --registry docs/arkitektur/registry/services.yaml \
            --changed-files changed-files.txt \
            --output affected-services.txt
          echo "repos<<EOF" >> $GITHUB_OUTPUT
          cat affected-services.txt >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Lag issues i berørte repos
        env:
          GH_TOKEN: ${{ secrets.CROSS_REPO_TOKEN }}
        run: |
          for repo in ${{ steps.affected.outputs.repos }}; do
            [ -n "$repo" ] || continue
            gh issue create \
              --repo myorg/$repo \
              --title "Arch-oppdatering: ${{ github.event.pull_request.title }}" \
              --label "arch-update" \
              --body "Merget: ${{ github.event.pull_request.html_url }}"
          done
```

Poenget er at varsling skal utledes fra faktiske endringer i arch-repo og
registry-mappingen, ikke fra fri tekst i PR-beskrivelsen.

### Valider dokumentformat

```yaml
# .github/workflows/validate-format.yml
name: Valider dokumentformat
on: pull_request
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Valider dokumentkontrakt
        run: |
          ./scripts/validate-docs.sh
      - name: Sjekk ADR-format
        run: |
          for adr in docs/arkitektur/adrs/[0-9]*.md; do
            [ -f "$adr" ] || continue
            if ! grep -q "## Lag" "$adr"; then
              echo "::error::ADR mangler '## Lag'-seksjon: $adr"
              exit 1
            fi
          done
      - name: Valider registry-referanser
        run: |
          sh scripts/find-affected-services.sh \
            --registry docs/arkitektur/registry/services.yaml \
            --validate-only
```

CI bør feile ved kontraktsbrudd. Varsler er nyttige i migrasjonsperioder,
men når repoet tas i bruk som styringsgrunnlag, må dokumenter og registry være
maskinlesbare uten manuell tolkning.

---

## 12. Tjeneste-repo: AGENTS.md referanse

Hvert tjenesterepo bør ha dette i sin AGENTS.md:

```markdown
## Felles arkitektur

Arkitekturen er organisert etter ArchiMate-lag.

    export ARCH_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/myorg/arch"
    if [ ! -d "$ARCH_DIR/.git" ]; then
        git clone --depth 1 https://github.com/myorg/arch.git "$ARCH_DIR"
    else
        git -C "$ARCH_DIR" pull --ff-only
    fi
    export PATH="$PATH:$ARCH_DIR/scripts"

### Før du starter en oppgave

    # 1. Orienter deg (Nivå 1)
    arch-read --index informasjon
    arch-read --index applikasjon

    # 2. Les relevante sammendrag (Nivå 2)
    arch-read docs/arkitektur/informasjon/fhir/consent.md

    # 3. Sjekk sikkerhet
    arch-read docs/arkitektur/sikkerhet/per-lag/applikasjon-sikkerhet.md

### Når du trenger endringer i felles arkitektur

- Usikker → Issue i myorg/arch med lag-tag
- Konkret forslag → PR med branch `agent/<dette-repo>/<lag>/<beskrivelse>`
- Flere lag → `cross-layer` label + issues i berørte repos

Husk: Alle dokumenter du oppretter/endrer SKAL ha `## Agent-sammendrag`
som første innholdsseksjon.

Se myorg/arch/AGENTS.md for fullstendige regler.
```

---

## 13. Eksempel: Komplett agent-flyt

### Oppgave: Implementer medikasjonsrekvirering i service-a

```bash
# ─── 1. Klon og sett opp ─────────────────────────────────────
export ARCH_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/myorg/arch"
if [ ! -d "$ARCH_DIR/.git" ]; then
  git clone --depth 1 https://github.com/myorg/arch.git "$ARCH_DIR"
else
  git -C "$ARCH_DIR" pull --ff-only
fi
export PATH="$PATH:$ARCH_DIR/scripts"

# ─── 2. Orienter deg (Nivå 1) ────────────────────────────────
arch-read --index informasjon
# → Ser MedicationRequest i fhir/medication-request.ts

arch-read --index applikasjon
# → Ser FHIR API-profil og event-katalog

# ─── 3. Les sammendrag (Nivå 2) ──────────────────────────────
arch-read docs/arkitektur/informasjon/fhir/medication-request.md
# → Viktigste regler, typer, API-referanse

arch-read docs/arkitektur/applikasjon/api/fhir-api-profil.md
# → HTTP-metoder, autentisering, validering

arch-read docs/arkitektur/sikkerhet/per-lag/applikasjon-sikkerhet.md
# → OAuth2, SMART on FHIR scopes, input-validering

# ─── 4. Implementasjonsdetaljer (Nivå 3) ─────────────────────
arch-read docs/arkitektur/informasjon/fhir/medication-request.md --løsning
# → TypeScript-type, JSON-eksempler, Aidbox-konfig, events

# ─── 5. Implementer ──────────────────────────────────────────
# Agenten har nå ~1500 tokens med arkitekturkontekst
# og kan bruke resten av kontekstvinduet til kode.

# ─── 6. Oppdager manglende type → Lager PR ───────────────────
cd "$ARCH_DIR"
git checkout -b agent/service-a/informasjon/add-dosage-type

# Følger dokumentformatet med Agent-sammendrag
# Lager ADR med lag-tagging
# Oppdaterer INDEX.md

gh pr create \
  --repo myorg/arch \
  --title "[I] Legg til DosageInstruction-type" \
  --label "arch-proposal,auto-agent,lag-informasjon,non-breaking"
```

---

## 14. Oppsummering

Denne strategien gir oss:

**For agenter:**
- `arch-read` for presise, konteksteffektive uttrekk
- Lesenivåer som sparer tokens (1500 i stedet for 5000+)
- Deterministisk dokumentkontrakt som gjør lesing og validering forutsigbar
- Tydelige regler for når og hvordan de foreslår endringer
- FIAT-tagging som gjør påvirkningsanalyse maskinvennlig

**For mennesker:**
- ArchiMate-lagdeling som er gjenkjennelig fra EA-praksis
- Vertikale views som viser sammenheng fra motivasjon til teknologi
- Sikkerhet som tverrgående perspektiv, ikke ettertanke
- ADRs som binder målarkitektur til løsningsbeslutninger
- Klarere avgrensning for hva som faktisk skal inn i felles arkitektur

**For samarbeid agent↔menneske:**
- Issues for vage behov, PRs for konkrete forslag
- Labels og tags som gjør review effektiv
- GitHub Actions som varsler berørte repos basert på faktiske endringer
- Registry som både viser eierskap og kan valideres maskinelt

**Minimal startpakke:**
1. Opprett `myorg/arch` med mappene fra seksjon 5
2. Legg inn `AGENTS.md` fra seksjon 6
3. Legg inn `scripts/arch-read.sh`
4. Legg inn `scripts/validate-docs.sh`, `scripts/find-affected-services.sh` og `scripts/arch-policy.sh`
5. Lag INDEX.md for de lagene du bruker mest (sannsynligvis I og A)
6. Lag 2-3 dokumenter som følger formatet (sammendrag → løsning → mål)
7. Legg til referanse i hvert tjenesterepos AGENTS.md

Resten kan du bygge opp iterativt etter hvert som agentene faktisk
trenger det. La bruken drive innholdet.
