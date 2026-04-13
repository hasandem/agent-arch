# Creativity-First Architecture Governance

**Dato**: 2026-04-13
**Status**: Godkjent design, klar for implementeringsplan
**Inspirasjonskilder**: Andrej Karpathy (LLM Wiki), Cole Medin (claude-memory-compiler)

---

## Bakgrunn og motivasjon

### Problemet vi løser

Agent-arch har en sekvensiell gating-modell der agenter i løsningsrepoer må
gjennom `arch-intake` → `arch-consume` → `arch-escalate` i fast rekkefølge,
med hooks som blokkerer handlinger underveis. Hver skill klassifiserer,
validerer og gater før agenten får lov til å kode.

Denne modellen sikrer compliance, men har en utilsiktet bieffekt: **den samlede
effekten av alle barrierene hemmer kreativiteten**. Agenter optimerer for å
komme gjennom portene i stedet for å løse problemet godt. De blir lydige
utførere fremfor kreative problemløsere.

### Kjernen i problemet

Tradisjonell arkitekturgovernance prøver å **forhindre feil** ved å sette opp
porter som må passeres. Dette fungerer for deterministiske systemer, men for
kreativt arbeid — enten det gjøres av mennesker eller AI-agenter — skaper det
en kultur der aktøren optimerer for å *komme gjennom porten* i stedet for å
*løse problemet godt*.

### Paradigmeskiftet

Vi snur modellen. I stedet for å gate kreativitet, **nærer** vi den med
kontekst og **evaluerer** resultatet etterpå. Dette er samme skift som
industrien har gjort fra waterfall til agile, fra pre-approval til code review,
fra gatekeeping til observability.

### Inspirasjonskilder

**Andrej Karpathys LLM Wiki-mønster** gir oss grunnstrukturen: en levende
kunnskapsbase der kunnskap compounderer over tid. Nøkkelegenskaper:

- Levende kunnskapsbase som vokser over tid — ikke statiske dokumenter
- Ingest → forstå → diskuter → skriv — kunnskap bygger seg opp
- Lenker mellom konsepter — agenten navigerer etter behov
- Lint/audit som en bevisst handling — ikke en automatisk gate
- Kunnskap compounderer — gode svar skrives tilbake

**Cole Medins claude-memory-compiler** gir oss automatiseringsmønsteret:

- Hooks fanger arkitekturbeslutninger automatisk fra samtaler
- Flush filtrerer "hva er verdt å lagre?" via LLM
- Compile syntetiserer daglige logger til strukturerte knowledge-artikler
- Session-start injiserer kontekst fra kunnskapsbasen
- Daglige logger er immutable — knowledge-artikler evolverer

### Agentisk universalitet — et designkrav

Systemet skal fungere med **alle AI-agenter**: Claude Code, Cursor, GitHub
Copilot, Codex, Windsurf, og fremtidige verktøy. Dette betyr:

- **Filer og CLI er det universelle grensesnittet** — alle agenter kan lese
  filer og kjøre kommandoer
- **Git hooks er den universelle trigger-mekanismen** — alle agenter opererer
  i git-repoer
- **Agentspesifikke instruksjonsfiler** (CLAUDE.md, .cursorrules, AGENTS.md)
  er tynne adaptere som peker til de samme kommandoene
- **Ingen avhengighet til spesifikke agent-SDK-er** — scripts bruker standard
  Python/shell og kaller LLM via et konfigurerbart endepunkt
- **Knowledge-strukturen er ren markdown** — lesbar for alle agenter og
  mennesker

---

## Overordnet arkitektur

### Fra: Sekvensiell gating

```
intake → consume → [implementer under oppsyn] → escalate
          ↓ blokkert hvis ikke klassifisert
```

### Til: Kontekst inn, compliance ut

```
arch-context (frivillig, når som helst)
         ↓ inspirasjon
    [implementer fritt og kreativt]
         ↓ automatisk (hooks fanger kunnskap)
    daily/ logger → flush → compile → knowledge/
         ↓ bevisst handling
arch-compliance (on-demand rapport)
         ↓ hvis ønskelig
arch-propose (PR mot sentral arkitektur)
```

### Tre skills + automatisk kunnskapsfangst

| Komponent | Rolle |
|---|---|
| **`arch-context`** | Gir agenten arkitekturkontekst som inspirasjon. Bootstrapper og vedlikeholder lokal kunnskapsbase. Ingesterer nye kilder. |
| **`arch-compliance`** | On-demand compliance-sjekk. Rapport med avvik, alvorlighet, tiltak. Agenten foreslår, mennesket bestemmer. |
| **`arch-propose`** | Foreslår arkitekturendring tilbake til sentral arkitektur via PR. |
| **Hooks + CLI** | Automatisk kunnskapsfangst via git hooks og CLI-kommandoer. Fanger arkitekturbeslutninger fra samtaler og kode. |

### Hva som fjernes fra løsningsrepoer

- **Alle blokkerende hooks** — erstattes av ikke-blokkerende kunnskapsfangst
- **Sekvensiell skill-avhengighet** — ingen skill krever at en annen har kjørt
- **Automatisk klassifisering** (Class A/B/C) — erstattes av konfigurerbar compliance-profil
- **arch-intake**, **arch-consume**, **arch-escalate** — fjernes helt
- **arch-brainstorming**, **arch-writing-plans**, **arch-systematic-debugging**,
  **arch-requesting-code-review** — fjernes, standard agent-verktøy brukes

### Designprinsipper

1. **Arkitektur er kontekst og inspirasjon** — ikke en gate
2. **Agenter har frihet til å innovere** — ingen pre-gating under implementasjon
3. **Kunnskap fanges automatisk** — hooks og CLI sørger for compounding
4. **Compliance sjekkes som en bevisst handling** — ikke per operasjon
5. **Agenten foreslår tiltak, mennesket bestemmer** — compliance er rådgivende
6. **Innovasjon flyter tilbake** — løsningsrepoer foreslår arkitekturendringer
7. **Agentisk universalitet** — fungerer med alle AI-agenter via filer og CLI

---

## Agentisk universalitet — grensesnittlaget

### Prinsipp: Filer inn, filer ut, CLI som verb

Alle agenter — uavhengig av plattform — kan:
- Lese markdown-filer
- Kjøre shell-kommandoer
- Operere i git-repoer

Dette er det universelle grensesnittet. Alt annet er adaptere.

### CLI-kommandoer (det universelle API-et)

```bash
# Kontekst og kunnskapsbygging
arch-knowledge context              # Les relevant kontekst for nåværende oppgave
arch-knowledge ingest <fil>         # Ingest en ny kilde til knowledge/
arch-knowledge search <term>        # Søk i kunnskapsbasen
arch-knowledge bootstrap            # Førstegangs-oppsett

# Automatisk kunnskapsfangst
arch-knowledge flush [--input <fil>] # Filtrer og lagre arkitekturrelevant kunnskap
arch-knowledge compile [--all]       # Syntetiser daily/ til knowledge/-artikler
arch-knowledge lint                  # Sjekk kunnskapsbasens helse

# Compliance
arch-knowledge compliance            # Kjør compliance-sjekk, produser rapport
arch-knowledge propose               # Foreslå endring til sentral arkitektur
```

Alle kommandoer er standard shell-scripts/Python som kan kalles av enhver agent.

### Agentspesifikke adaptere

Tynne konfigurasjonsfiler som forteller hver agent hvordan den bruker CLI-en:

```
.claude/         → CLAUDE.md med instruksjoner + hooks i settings.json
.cursor/         → .cursorrules med instruksjoner
.github/         → AGENTS.md (GitHub Copilot) + copilot-instructions.md
codex/           → codex-instructions.md
```

Hver adapter inneholder:
1. **Instruksjoner**: "Bruk `arch-knowledge context` for kontekst. 
   Kjør `arch-knowledge compliance` for compliance-sjekk."
2. **Hook-mapping**: Hvordan plattformens hook-system mapper til CLI-kommandoene
3. **Kontekstinjeksjon**: Hvordan plattformen leser knowledge/index.md ved oppstart

### Hook-adaptere per plattform

| Event | Claude Code | Cursor | Git (universelt) |
|---|---|---|---|
| Sesjonstart | SessionStart hook | .cursorrules lest automatisk | — |
| Før komprimering | PreCompact hook | — | — |
| Sesjonsslutt | SessionEnd hook | — | — |
| Etter commit | — | — | post-commit git hook |
| Før push | — | — | pre-push git hook |

**Git hooks er det universelle fallbacket**. Plattformer som støtter rikere
hooks (Claude Code) får bedre automatikk, men grunnfunksjonaliteten virker
overalt via git.

### Universell kontekstinjeksjon

Uavhengig av plattform kan enhver agent lese:

```
docs/arch-knowledge/knowledge/index.md     → Oversikt over all kunnskap
docs/arch-knowledge/daily/YYYY-MM-DD.md    → Siste daglige logg
docs/arch-knowledge/arch-statement.md      → Repo-konfigurasjon
```

For plattformer med sesjonstart-hook injiseres dette automatisk.
For andre plattformer instrueres agenten til å lese disse filene selv.

---

## Knowledge-laget

### Hvorfor "knowledge" fremfor "wiki"

"Wiki" bærer konnotasjoner fra Wikipedia — åpen redigering, flat struktur.
"Knowledge" kommuniserer tydeligere hva vi bygger: en kunnskapsbase som
agenten aktivt bruker og beriker. `raw/` + `knowledge/` leser også bedre —
det kommuniserer forskjellen: **raw er importert, knowledge er forstått**.

### Tre lag av kunnskap

Inspirert av Medins trelagsmodell, tilpasset arkitekturkontekst:

| Lag | Innhold | Mutabilitet |
|---|---|---|
| `raw/` | Importerte kilder — sentral arkitektur, tredjepartsdocs | Immutable for agenter |
| `daily/` | Daglige logger — rå fangst fra samtaler og arbeid | Append-only, aldri redigert |
| `knowledge/` | Syntetiserte artikler — forståelse, beslutninger, mønstre | Evolverer over tid |

**Hvorfor tre lag?**
- `raw/` er sannhetskilden — det som er *gitt*
- `daily/` er det som *skjedde* — sporbar, ufiltrert fangst
- `knowledge/` er det som er *forstått* — syntetisert, strukturert, lenket

Daglige logger gir full sporbarhet tilbake til den opprinnelige samtalen eller
hendelsen. Knowledge-artikler gir rask, navigerbar forståelse. Raw gir
autoritativ referanse.

### Tolagsmodell: sentral og lokal

**Sentral kunnskapsbase** (i agent-arch repoet):

| Element | Beskrivelse |
|---|---|
| `raw/` | Normative arkitekturdokumenter (ArchiMate-lagdelt). Immutable for agenter — kun mennesker og `arch-governance` endrer disse |
| `knowledge/` | Agentoptimalisert kunnskapsbase. Generert fra `raw/`, vedlikeholdt av governance |
| `knowledge/index.md` | Innholdsfortegnelse med one-liners — agentens startpunkt |
| `knowledge/log.md` | Append-only endringslogg — sporbarhet |
| `daily/` | Daglige logger fra governance-arbeid |

**Lokal kunnskapsbase** (i hvert løsningsrepo):

| Element | Beskrivelse |
|---|---|
| `docs/arch-knowledge/raw/central/` | Synkronisert fra sentral kunnskapsbase (read-only) |
| `docs/arch-knowledge/raw/local/` | Importerte lokale kilder (ikke agentskrevet) |
| `docs/arch-knowledge/raw/external/` | Tredjepartsdocs, standarder |
| `docs/arch-knowledge/daily/` | Daglige logger — automatisk fangst |
| `docs/arch-knowledge/knowledge/` | Syntetiserte knowledge-artikler |
| `docs/arch-knowledge/knowledge/index.md` | Lokal innholdsfortegnelse |
| `docs/arch-knowledge/knowledge/log.md` | Lokal endringslogg |
| `docs/arch-knowledge/arch-statement.md` | Repo-konfigurasjon |
| `docs/arch-knowledge/compliance-profile.yaml` | Konfigurerbart regelset |

### Kunnskapsflyt

```
+--------------------------------------------+
|   Sentral kunnskapsbase                    |
|   (agent-arch/)                            |
|                                            |
|   raw/ → knowledge/ (governance)           |
|   index.md, konseptartikler,               |
|   [[lenker]], log.md                       |
|                                            |
|         ↑ arch-knowledge propose (PR)      |
|         |                                  |
+---------+----------------------------------+
          |
    +-----+-----------------------------------+
    |     |  Løsningsrepo                     |
    |     |                                   |
    |  docs/arch-knowledge/                   |
    |     |                                   |
    |  CLI: context/     CLI: compliance/     |
    |  ingest/search     propose              |
    |     |                                   |
    |  Hooks: automatisk kunnskapsfangst      |
    |  daily/ → flush → compile → knowledge/  |
    |                                         |
    |  Agenten jobber fritt,                  |
    |  kunnskap compounderer automatisk       |
    +-----------------------------------------+
```

---

## Automatisk kunnskapsfangst (hooks + pipeline)

### Hvorfor automatisk fangst

I det opprinnelige designet var compounding avhengig av at agenten *husket*
å skrive tilbake til kunnskapsbasen. Cole Medins mønster løser dette elegant:
kunnskap fanges **automatisk** fra samtaler og arbeid via hooks.

Agenten trenger ikke å huske å dokumentere — systemet fanger det opp.

### Pipeline: Hook → Flush → Compile

```
1. FANGST (hook eller manuell)
   Agent jobber, tar beslutninger, diskuterer med utvikler
       ↓
   Hook/trigger fanger samtale eller diff
       ↓
   Rå kontekst skrives til temp-fil

2. FLUSH (asynkron, i bakgrunnen)
   arch-knowledge flush --input <temp-fil>
       ↓
   LLM filtrerer: "Hva er arkitekturrelevant?"
       ↓
   Kategoriserer: beslutninger, mønstre, konsepter, lærdom
       ↓
   Appender til daily/YYYY-MM-DD.md med tidsstempel
       ↓
   Returnerer FLUSH_OK hvis ingenting relevant

3. COMPILE (asynkron, periodisk)
   arch-knowledge compile
       ↓
   Leser daily/ logger + eksisterende knowledge/
       ↓
   LLM syntetiserer til knowledge-artikler (nye/oppdaterte)
       ↓
   Oppdaterer index.md og log.md
       ↓
   Hash-basert endringssporing — kun endret innhold prosesseres
```

### Trigger-mekanismer (agentisk universelt)

**Rike plattformer (Claude Code):**
- SessionStart → injiser knowledge/index.md + siste daily/ logg
- PreCompact → fang samtale før kontekstkomprimering
- SessionEnd → fang samtale ved sesjonsslutt
- Alle hooks spawner flush i bakgrunnen (<10s hook-tid)

**Universelt via git hooks:**
- post-commit → trigger flush med commit-diff som input
- pre-push → trigger compile for å syntetisere dagens kunnskap

**Manuelt via CLI:**
- `arch-knowledge flush --input <fil>` — flush en spesifikk kilde
- `arch-knowledge compile` — manuell kompilering
- `arch-knowledge compile --all` — rekompiler alt

**Agentinstruksjoner (for plattformer uten hooks):**
- Instruksjonsfilen (.cursorrules etc.) ber agenten om å kjøre
  `arch-knowledge flush` periodisk under arbeidet

### Rekursjonsbeskyttelse

Inspirert av Medins mønster: hooks sjekker en miljøvariabel
(f.eks. `ARCH_KNOWLEDGE_INVOKED_BY`) for å unngå at flush/compile
trigges rekursivt når en agent kalles av systemet selv.

### Deduplisering

Session-ID + tidsstempel forhindrer at samme samtale flusher to ganger
(f.eks. hvis både PreCompact og SessionEnd trigges tett etter hverandre).

---

## Typede knowledge-artikler

### Hvorfor typer

I en kunnskapsbase uten typer mister man evnen til å spørre "hvilke
beslutninger har vi tatt?" vs "hva forstår vi om domenet?". Ved å gi
hver artikkel en type i frontmatter får vi det beste fra to verdener:

- **Friheten** til at alt lever i én sammenhengende kunnskapsbase med
  naturlige krysslenker
- **Strukturen** til å kunne filtrere og resonnere over *hva slags*
  kunnskap noe er

Agentskrevet innhold (ADR-er, designdocs, API-kontrakter) hører hjemme
i `knowledge/` — ikke i `raw/`. De er beslutninger tatt underveis, ikke
eksterne kilder. `raw/` er reservert for genuint importerte kilder.

### Typedefinisjoner

| Type | Formål | Compliance-relevans |
|---|---|---|
| `concept` | Domeneforståelse, forklaringer | Kontekst — sjekkes ikke direkte |
| `decision` | Designvalg, ADR-er | Sjekkes mot arkitekturen — er beslutningen alignet? |
| `contract` | API-kontrakter, grensesnitt | Sjekkes for kompatibilitet |
| `pattern` | Mønstre og best practices | Sjekkes som soft-anbefaling |
| `review` | Compliance-rapporter, audit-resultater | Kilde til neste compile-runde |

### Artikkelkontrakt

Hver knowledge-artikkel følger en fast struktur:

```markdown
---
type: concept | decision | contract | pattern | review
status: draft | active | superseded | deprecated
date: 2026-04-12
sources:
  - raw/central/informasjon/fhir/resources.md
  - daily/2026-04-12.md
superseded-by: knowledge/newer-article.md  # kun ved superseded
---

# Artikkeltittel

**Sammendrag**: Én til to setninger som beskriver denne artikkelen.

---

Hovedinnhold her. Bruk klare overskrifter og korte avsnitt.
Lenk til relaterte konsepter med [[knowledge-lenker]] gjennom teksten.

Hver faktapåstand refererer til sin kilde (kilde: raw/central/...).

## Relaterte artikler

- [[relatert-konsept-1]]
- [[relatert-konsept-2]]
```

### Decision-artikler med changelog

Beslutninger (ADR-er) evolverer over tid i stedet for å bli erstattet.
En beslutning modnes — den opprinnelige konteksten endres, nye erfaringer
påvirker den. Changelog-seksjonen gir full sporbarhet.

```markdown
---
type: decision
status: active
date: 2026-04-12
sources:
  - raw/central/informasjon/fhir/resources.md
  - daily/2026-04-12.md
---

# ADR-003: Event Sourcing for Medication History

**Sammendrag**: Vi bruker event sourcing for medisinhistorikk fordi
vi trenger full sporbarhet og audit trail.

---

## Kontekst

[[medication-api]] krever full historikk...

## Beslutning

Vi velger event sourcing fordi...

## Konsekvenser

- Mer kompleks infrastruktur
- Full audit trail
- [[cqrs-pattern]] blir nødvendig

## Changelog

| Dato | Endring | Begrunnelse |
|---|---|---|
| 2026-04-12 | Opprettet | Initiell beslutning basert på compliance-krav |
| 2026-05-03 | Lagt til CQRS som konsekvens | Erfaring fra sprint 4 |
| 2026-06-15 | Status: under review | Compliance-rapport stiller spørsmål |

## Relaterte artikler

- [[medication-api]]
- [[cqrs-pattern]]
- [[compliance-review-2026-06]]
```

`superseded-by` brukes kun når beslutningen er *helt erstattet*, ikke justert.

### Siteringsregler

- Hver faktapåstand refererer til sin kilde: `(kilde: raw/central/...)`
- Daglige logger som kilde: `(kilde: daily/2026-04-12.md)`
- Konflikt mellom kilder → noter motsetningen eksplisitt
- Påstander uten kilde → markeres som "trenger verifisering"

---

## Skill 1: `arch-context` (CLI: `arch-knowledge context`)

### Formål

Gi agenten rik, relevant arkitekturkontekst som inspirasjon — ikke som en gate.
Bootstrappe og vedlikeholde en lokal kunnskapsbase som compounderer over tid.

### Hvorfor denne skillen finnes

Agenter gjør bedre arbeid når de forstår konteksten de opererer i. Men det er
forskjell på å *tvinge* en agent gjennom en sjekkliste og å *tilby* en
kunnskapsbase den kan bruke når den trenger det. `arch-context` er agentens
oppslagsverk — den bruker det når det gir verdi, ikke fordi den må.

### Når den brukes

- Frivillig, når som helst i arbeidsflyten
- Typisk ved oppstart av nytt arbeid, eller når agenten trenger domeneforståelse
- Kan kjøres gjentatte ganger
- Ved bootstrap av nye repoer

### Hva den gjør

```
1. ORIENTERING
   - Les knowledge/index.md (lokal, hvis den finnes)
   - Les sentral knowledge/index.md (fra raw/central/, hvis connected)
   - Identifiser relevante artikler basert på oppgaven

2. KONTEKSTBYGGING
   - Les relevante knowledge-artikler (lokale først, sentrale som supplement)
   - Følg [[lenker]] for å bygge forståelse
   - Presenter nøkkelkontekst til agenten

3. INGEST (når nye kilder finnes)
   - Les kildedokument fra raw/
   - Diskuter nøkkelfunn med utvikler
   - Opprett/oppdater knowledge-artikler med riktig type
   - Legg til [[lenker]]
   - Oppdater index.md og log.md

4. BOOTSTRAP (førstegangs-oppsett)
   - Se "Bootstrap-prosess" seksjon
```

### Hva den IKKE gjør

- Klassifiserer ikke endringer (Class A/B/C)
- Blokkerer ingen handlinger
- Krever ikke at andre skills har kjørt
- Validerer ikke compliance

---

## Skill 2: `arch-compliance` (CLI: `arch-knowledge compliance`)

### Formål

On-demand compliance-sjekk som produserer en rapport med avvik, alvorlighet,
og anbefalte tiltak. Agenten foreslår, mennesket bestemmer.

### Hvorfor denne skillen finnes

Frihet uten feedback er ikke frihet — det er ubevissthet. Compliance-skillen
gir teamet et klart bilde av hvor løsningen står i forhold til arkitekturen,
uten å bremse arbeidet underveis. Den er en *bevisst handling*.

Compliance-rapporten har en dobbel rolle: den er både et **beslutningsgrunnlag**
og en **kunnskapskilde**. Når den lagres som en `type: review` knowledge-artikkel,
blir den input til neste compile-runde, og kunnskapsbasen blir rikere.
Slik compounderer kunnskap — avvik blir til lærdom.

### Når den brukes

- Eksplisitt, når teamet ønsker å sjekke compliance-status
- Typisk etter en implementasjonsfase, før PR, eller ved milepæler
- Kan kjøres periodisk for å følge med på drift

### Hva den sjekker

Mot konfigurerbart regelset i `compliance-profile.yaml`:

```yaml
rules:
  hard:    # Må fikses — rapporteres som blokkerende
    - security-principles
    - data-privacy
    - api-contract-compatibility
  soft:    # Bør vurderes — rapporteres som anbefaling
    - naming-conventions
    - documentation-standards
    - preferred-patterns
  info:    # Informativt — rapporteres for bevissthet
    - technology-radar-alignment
    - performance-guidelines
```

### Hva den produserer

```markdown
---
type: review
date: 2026-04-12
scope: feature/medication-history
sources:
  - raw/central/sikkerhet/consent.md
  - knowledge/medication-api.md
  - knowledge/adr-003-event-sourcing.md
---

# Compliance Review: Medication History Feature

## Sammendrag
3 hard avvik, 1 soft anbefaling, 2 info-observasjoner

## Hard avvik
1. **Manglende consent-sjekk ved API-kall**
   Kilde: raw/central/sikkerhet/consent.md
   Berørt kode: src/api/medication.ts:45-62
   Anbefalt tiltak: Implementer consent-middleware
   Alternativt tiltak: Foreslå arkitekturendring via arch-knowledge propose

## Soft anbefalinger
1. **Event-navn følger ikke navnekonvensjon**
   ...

## Info
1. **Bruker REST der arkitekturen anbefaler GraphQL**
   Merknad: Lokal decision (adr-003) begrunner valget
   ...

## Kunnskapshelse
- 2 orphan-artikler funnet
- 1 konsept nevnt uten egen artikkel: [[audit-logging]]
- 0 motstrid mellom lokal og sentral kunnskapsbase
- 1 stale artikkel (eldre enn 90 dager)
```

### Kunnskapshelse (lint)

Integrert i compliance, inspirert av Medins lint.py:

1. Brutte lenker (gratis)
2. Orphan-artikler — ingen innkommende lenker (gratis)
3. Ukompilerte daglige logger (gratis)
4. Stale artikler — logger endret etter kompilering (gratis)
5. Manglende backlinks — enveis-lenker (gratis)
6. Sparse artikler — under 200 ord (gratis)
7. Motstrid — LLM-basert semantisk sjekk (valgfritt, `--structural-only` hopper over)

### Feedback-loop: compliance → kunnskap

```
Implementer fritt
       ↓
arch-knowledge compliance → rapport (type: review)
       ↓
Rapport lagres i knowledge/
       ↓
Neste compile → kunnskapsbasen oppdateres med lærdom
       ↓
Agenten er smartere neste gang
```

---

## Skill 3: `arch-propose` (CLI: `arch-knowledge propose`)

### Formål

Foreslå endringer tilbake til sentral arkitektur via PR, basert på innovasjon
og erfaringer fra løsningsrepoet.

### Hvorfor denne skillen finnes

Arkitektur som bare flyter *nedover* (fra sentral til løsning) blir utdatert.
Den virkelige verdien oppstår når innovasjon i løsningsrepoene flyter *tilbake*
og forbedrer arkitekturen for alle. `arch-propose` gjør tilbakeflytingen til
en eksplisitt, sporbar handling.

Skillen bygger på kunnskapen: den bruker lokale `decision`-artikler,
`review`-rapporter, og `pattern`-artikler som dokumentasjon av *hva* som ble
gjort og *hvorfor* det fungerte.

### Når den brukes

- Etter compliance-rapport har identifisert avvik som bør løses i arkitekturen
- Når teamet har funnet et mønster som fungerer bedre enn arkitekturen foreskriver
- Når nye konsepter bør inn i sentral kunnskapsbase
- Kun tilgjengelig i `connected` modus (se arch-statement.md)

### Hva den gjør

```
1. SAMLE EVIDENS
   - Les relevante knowledge-artikler (decisions, patterns, reviews)
   - Identifiser hvilke sentrale docs som berøres
   - Bygg argumentasjon basert på lokal erfaring

2. KLASSIFISER ENDRING
   - Klargjøring/tillegg → enklere PR
   - Ny anbefaling/mønster → PR med begrunnelse
   - Prinsipiell endring → Issue først, deretter PR

3. OPPRETT PR MOT SENTRAL ARKITEKTUR
   - Foreslå endringer i relevante docs i raw/
   - Foreslå oppdateringer i sentral knowledge/
   - Inkluder lenker til lokal evidens
   - Tilordne til arkitektur-teamet for review

4. OPPDATER LOKAL KUNNSKAPSBASE
   - Marker berørte artikler som "foreslått endring pending"
   - Logg i knowledge/log.md
```

---

## Compliance-profil

### Konfigurasjon

```yaml
# docs/arch-knowledge/compliance-profile.yaml

# Sentral arkitekturkilde
source:
  repo: org/agent-arch
  branch: main
  sync-strategy: manual  # manual | on-context | scheduled

# Regler med alvorlighet
rules:
  hard:
    - id: security-principles
      source: raw/central/sikkerhet/
      description: "Sikkerhetsprinsipper er ufravikelige"
    - id: data-privacy
      source: raw/central/personvern/
    - id: api-contract-compatibility
      source: knowledge/*  # type: contract

  soft:
    - id: naming-conventions
      source: raw/central/konvensjoner/
    - id: documentation-standards
    - id: preferred-patterns
      source: knowledge/*  # type: pattern

  info:
    - id: technology-radar
    - id: performance-guidelines

# Scope for compliance-sjekk
scope:
  include:
    - src/**
    - api/**
  exclude:
    - tests/**

# Kunnskapshelse
knowledge-health:
  check-orphans: true
  check-missing-concepts: true
  check-stale-articles: 90d
  check-source-conflicts: true
  check-sparse-articles: true
  check-broken-links: true

# LLM-konfigurasjon for flush/compile/compliance
llm:
  provider: anthropic  # anthropic | openai | ollama | custom
  model: claude-sonnet-4-20250514
  # endpoint: https://custom-endpoint.example.com  # for custom provider
```

### Hvorfor konfigurerbar profil

- **Ansvar flyttes til teamet** — de bestemmer hva som er viktig
- **Sentral arkitektur forblir rådgivende** — definerer *hva*, ikke *hvor strengt*
- **Gradvis adopsjon** — start med minimal profil, utvid etter hvert
- **Unngå one-size-fits-all** — kjerneproblemet med de gamle gatede skillsene
- **LLM-agnostisk** — teamet velger sin foretrukne LLM-provider

---

## arch-statement.md — standalone/connected modus

### Formål

Konfigurasjonspunkt for om repoet har et sentralt arkitekturrepo eller ikke.
Gjør det mulig å starte standalone og koble til senere — for eksempel etter
å ha innovert fritt en stund.

### Format

```markdown
# Architecture Statement

## Modus
mode: standalone  # standalone | connected

## Sentralt arkitekturrepo (kun hvis mode: connected)
# central-repo: org/agent-arch
# central-repo-url: https://github.com/org/agent-arch.git

## Beskrivelse
Kort beskrivelse av dette repoets arkitekturelle kontekst.
```

### Skill-tilpasning etter modus

| Scenario | `arch-context` | `arch-compliance` | `arch-propose` |
|---|---|---|---|
| **standalone** | Kun lokal knowledge. Ingen raw/central/. | Kun lokal compliance-profil | Utilgjengelig |
| **connected** | Synkroniserer fra sentral + bygger lokal | Sentral + lokal profil | PR mot sentralt repo |

### Overgang standalone → connected

Når en organisasjon modnes og vil koble til et sentralt repo:

```
1. Bruker ber om tilkobling
2. Skill spør: "Har du allerede et sentralt arkitekturrepo?"

   Hvis nei:
   - Guider gjennom opprettelse av nytt repo
   - Bootstrapper sentral knowledge-struktur
   - Spør om URL/path som gh/git kan nå
   - Oppdaterer arch-statement.md

   Hvis ja:
   - Spør om URL eller org/repo-navn
   - Validerer tilgjengelighet
   - Synkroniserer raw/central/
   - Oppdaterer arch-statement.md

3. Eksisterende lokal knowledge bevares og berikes med sentral kontekst
4. Lokal knowledge kan migreres oppover som input til sentralt repo
```

### Nøkkelinnsikt

Team som innoverer fritt i standalone-modus og deretter kobler til et sentralt
repo, kan bruke sin lokale knowledge som *input* til det sentrale repoet.
Arkitekturen vokser organisk nedenfra — fra erfaring, ikke fra teori.

---

## Bootstrap-prosess for nye repoer

### Tre steg

```
Steg 1: INSTALL
   - Kjør arch-knowledge bootstrap (eller install-method.sh)
   - Oppretter docs/arch-knowledge/ med tom struktur
   - Legger inn default compliance-profile.yaml
   - Oppretter arch-statement.md (spør om standalone/connected)
   - Hvis connected: synkroniserer raw/central/
   - Genererer agentspesifikke adaptere (.claude/, .cursor/, .github/)

Steg 2: INITIAL INGEST
   - Leser sentral knowledge/index.md (hvis connected)
   - Spør: "Hva skal dette repoet gjøre?"
   - Identifiserer relevante konsepter
   - Oppretter lokale knowledge-artikler for de mest relevante
   - Oppretter index.md og log.md

Steg 3: FIRST DECISIONS
   - Oppfordrer til å dokumentere tidlige designvalg
   - "Du har satt opp [teknologi X]. Vil du dokumentere dette som en beslutning?"
   - Første decision-artikler opprettes med changelog
```

### Bootstrap er en samtale

Bootstrap er ikke en automatisk prosess — det er en samtale mellom agenten
og utvikleren. Agenten spør, utvikleren svarer, og sammen bygger de den
initielle kunnskapsbasen. Mer innsats første gang, men kunnskapsbasen starter
med genuin forståelse.

---

## Migrering

### Strategi: Én omgang, ingen overgangsperiode

Ren overgang. Gamle skills fjernes helt, nye erstatter. Klart signal om
paradigmeskiftet.

### Hva som endres

| Dagens modell | Ny modell | Handling |
|---|---|---|
| `arch-intake` | Fjernes | Absorbert av `arch-knowledge context` |
| `arch-consume` | Fjernes | Erstattet av `arch-knowledge context` |
| `arch-escalate` | Fjernes | Lesedel → context, PR-del → propose |
| `arch-governance` | **Beholdes, tilpasses** | Vedlikeholder sentral knowledge |
| `arch-brainstorming` | Fjernes | Standard agent-verktøy (knowledge gir kontekst) |
| `arch-writing-plans` | Fjernes | Standard agent-verktøy |
| `arch-systematic-debugging` | Fjernes | Standard agent-verktøy |
| `arch-requesting-code-review` | Fjernes | compliance + standard code review |
| Hooks i løsningsrepo | **Erstattes** | Blokkerende → ikke-blokkerende kunnskapsfangst |
| Hooks i sentral repo | **Beholdes** | Sentral arkitektur trenger fortsatt governance |
| `arch-policy.sh` | **Refaktoreres** | Logikk gjenbrukes i compliance og propose |
| `arch-read.sh` | **Beholdes, utvides** | Brukes av context for lesing av raw/ |
| `solution-standard.manifest` | **Oppdateres** | Ny filstruktur + agentadaptere |
| `install-method.sh` | **Oppdateres** | Bootstrapper knowledge-struktur |

### Migreringssekvens for sentral repo

```
Fase 1: Opprett knowledge-laget
   - Opprett knowledge/ med index.md og log.md
   - Generer artikler fra eksisterende raw/ docs
   - Opprett daily/ for governance-logger
   - arch-governance lærer å vedlikeholde knowledge

Fase 2: Nye skills og CLI
   - Implementer arch-knowledge CLI (context, compliance, propose, flush, compile, lint)
   - Implementer agent-adaptere (CLAUDE.md, .cursorrules, AGENTS.md)
   - Fjern arch-intake, arch-consume, arch-escalate
   - Fjern arch-brainstorming, arch-writing-plans, arch-systematic-debugging, arch-requesting-code-review
   - Oppdater solution-standard.manifest
   - Oppdater install-method.sh med bootstrap

Fase 3: Oppdater templates
   - Ny AGENTS.md.tmpl med agentuniverselle instruksjoner
   - Ny compliance-profile.yaml default-template
   - Nye agent-adapter-templates
   - Ny arch-statement.md template

Fase 4: Dokumentasjon
   - Oppdater docs/adoption/ med ny modell
   - Oppdater docs/method/ med knowledge-mønsteret
```

### Migreringssekvens for løsningsrepoer

```
Fase 1: Bootstrap
   - Kjør arch-knowledge bootstrap
   - Gamle skills erstattes av CLI + adaptere
   - Blokkerende hooks erstattes av kunnskapsfangst-hooks
   - Knowledge-struktur opprettes

Fase 2: Initial ingest
   - arch-knowledge context kjøres første gang
   - Sentral knowledge synkroniseres (hvis connected)
   - Eksisterende lokale docs flyttes til raw/local/ eller knowledge/
   - Initial knowledge genereres

Fase 3: Konfigurer
   - Team tilpasser compliance-profile.yaml
   - Team tilpasser arch-statement.md
   - Velger LLM-provider for flush/compile

Fase 4: Daglig bruk
   - Agenter bruker arch-knowledge context når de vil
   - Hooks fanger kunnskap automatisk
   - Team kjører arch-knowledge compliance når de vil
   - Knowledge vokser organisk
```

---

## Filstruktur etter migrering

### Sentral arkitektur-repo

```
agent-arch/
├── raw/                          # Normative arkitekturdokumenter
│   ├── motivasjon/
│   ├── strategi/
│   ├── sikkerhet/
│   ├── informasjon/
│   └── ...
├── daily/                        # Daglige governance-logger
├── knowledge/                    # Syntetisert kunnskapsbase
│   ├── index.md
│   ├── log.md
│   └── [artikler].md
├── .github/
│   ├── skills/
│   │   ├── arch-context/         # NY (wrapper rundt CLI)
│   │   ├── arch-compliance/      # NY (wrapper rundt CLI)
│   │   ├── arch-propose/         # NY (wrapper rundt CLI)
│   │   └── arch-governance/      # OPPDATERT
│   └── hooks/                    # Beholdes for sentral repo
├── scripts/
│   ├── arch-knowledge            # NY: universell CLI
│   ├── flush.py                  # NY: kunnskapsfiltrering
│   ├── compile.py                # NY: kunnskapssyntetisering
│   ├── arch-read.sh              # Beholdes
│   └── ...
├── install/
│   ├── profiles/
│   │   └── solution-standard.manifest
│   └── adapters/                 # NY: agentspesifikke adaptere
│       ├── claude/
│       ├── cursor/
│       ├── github-copilot/
│       └── generic/
├── templates/
│   ├── arch-statement.md.tmpl
│   ├── compliance-profile.yaml.tmpl
│   └── ...
└── docs/
    ├── adoption/
    ├── method/
    ├── reference/
    └── solution-space/
```

### Løsningsrepo etter install

```
docs/arch-knowledge/
├── raw/
│   ├── central/                  # Synkronisert fra sentral (hvis connected)
│   ├── local/                    # Importerte lokale kilder
│   └── external/                 # Tredjepartsdocs
├── daily/                        # Daglige logger (append-only)
│   └── YYYY-MM-DD.md
├── knowledge/                    # Syntetiserte artikler
│   ├── index.md
│   ├── log.md
│   └── [artikler].md
├── arch-statement.md             # Standalone/connected konfigurasjon
└── compliance-profile.yaml       # Konfigurerbart regelset

# Agentspesifikke adaptere (i repo-root)
.claude/settings.json             # Claude Code hooks
.cursorrules                      # Cursor-instruksjoner
.github/copilot-instructions.md   # GitHub Copilot-instruksjoner
AGENTS.md                         # Generiske agentinstruksjoner

# Git hooks (universelt)
.githooks/
├── post-commit                   # Trigger flush
└── pre-push                      # Trigger compile
```

---

## Oppsummering av designvalg og begrunnelser

| Designvalg | Begrunnelse |
|---|---|
| Fjerne alle pre-gates | Den samlede effekten av barrierene hemmer kreativitet mer enn den sikrer kvalitet |
| Knowledge fremfor statiske docs | Kunnskap som brukes aktivt og vokser organisk er mer verdifull enn dokumenter som leses én gang |
| Tre lag (raw/daily/knowledge) | raw er importert, daily er hva som skjedde, knowledge er hva som er forstått. Full sporbarhet |
| Automatisk kunnskapsfangst | Agenten trenger ikke huske å dokumentere. Hooks fanger det opp. Inspirert av Medin |
| Typede knowledge-artikler | Filtrering uten å bryte kunnskapsflyten. Decision vs concept vs pattern |
| Decision-artikler med changelog | Beslutninger modnes over tid. Changelog gir sporbarhet |
| Konfigurerbar compliance-profil | Unngå one-size-fits-all. Teamet eier sin profil. Sentral arkitektur rådgivende |
| Compliance som bevisst handling | Frihet uten feedback er ubevissthet. Feedback når teamet er klare |
| Agenten foreslår, mennesket bestemmer | Ansvaret der det hører hjemme |
| Toveis-flyt via arch-propose | Innovasjon må flyte tilbake. Arkitektur som bare flyter ned blir utdatert |
| Standalone/connected modus | Lav terskel for å starte. Koble til sentral arkitektur når klar |
| Agentisk universalitet | CLI + filer som universelt grensesnitt. Adaptere per plattform. Ingen vendor lock-in |
| Git hooks som universelt fallback | Alle agenter opererer i git-repoer. Rike plattformer får bedre automatikk |
| Én omgang migrering | Klart paradigmeskifte. Ingen kompleksitet med to parallelle modeller |
| LLM-agnostisk flush/compile | Teamet velger sin LLM-provider. Ikke låst til Anthropic |
| Markdown over vector DB | Ved arkitekturskala (50-500 artikler) overgår LLM-resonnering vektorsøk. Enklere, billigere |
