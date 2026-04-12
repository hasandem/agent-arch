# Creativity-First Architecture Governance

**Dato**: 2026-04-12
**Status**: Godkjent design, klar for implementeringsplan

---

## Bakgrunn og motivasjon

### Problemet vi løser

Agent-arch har en sekvensiell gating-modell der agenter i løsningsrepoer må gjennom `arch-intake` -> `arch-consume` -> `arch-escalate` i fast rekkefølge, med hooks som blokkerer handlinger underveis. Hver skill klassifiserer, validerer og gater før agenten får lov til å kode.

Denne modellen sikrer compliance, men har en utilsiktet bieffekt: **den samlede effekten av alle barrierene hemmer kreativiteten**. Agenter optimerer for å komme gjennom portene i stedet for å løse problemet godt. De blir lydige utførere fremfor kreative problemløsere.

### Kjernen i problemet

Tradisjonell arkitekturgovernance prøver å **forhindre feil** ved å sette opp porter som må passeres. Dette fungerer for deterministiske systemer, men for kreativt arbeid — enten det gjøres av mennesker eller AI-agenter — skaper det en kultur der aktøren optimerer for å *komme gjennom porten* i stedet for å *løse problemet godt*.

### Paradigmeskiftet

Vi snur modellen. I stedet for å gate kreativitet, **nærer** vi den med kontekst og **evaluerer** resultatet etterpå. Dette er samme skift som industrien har gjort fra waterfall til agile, fra pre-approval til code review, fra gatekeeping til observability.

### Inspirasjon: LLM Wiki-mønsteret

Andrej Karpathys LLM Wiki-mønster gir oss et konkret verktøy for dette: en levende kunnskapsbase der kunnskap **compounderer over tid**. Egenskaper som er direkte overførbare:

- **Levende kunnskapsbase** som vokser over tid — ikke statiske dokumenter
- **Ingest -> forstå -> diskuter -> skriv** — kunnskap bygger seg opp
- **Wiki-links mellom konsepter** — agenten navigerer etter behov
- **Lint/audit som en bevisst handling** — ikke en automatisk gate
- **Spørsmål besvares fra wikien** — et mellomlag av forståelse
- **Kunnskap compounderer** — gode svar skrives tilbake, compliance-rapporter blir input til neste runde

---

## Overordnet arkitektur

### Fra: Sekvensiell gating

```
intake -> consume -> [implementer under oppsyn] -> escalate
          | blokkert hvis ikke klassifisert
```

### Til: Kontekst inn, compliance ut

```
arch-context (frivillig, når som helst)
         | inspirasjon
    [implementer fritt og kreativt]
         | bevisst handling
arch-compliance (on-demand rapport)
         | hvis ønskelig
arch-propose (PR mot sentral arkitektur)
```

### Tre nye skills erstatter seks gamle

| Ny skill | Erstatter | Rolle |
|---|---|---|
| **`arch-context`** | `arch-intake` + `arch-consume` + `arch-escalate` (lesedelen) | Gir agenten arkitekturkontekst som inspirasjon. Bygger og vedlikeholder en lokal arkitektur-wiki per repo, inspirert av LLM Wiki-mønsteret. |
| **`arch-compliance`** | Hooks + policy-gating (`arch-policy.sh`) | On-demand compliance-sjekk. Produserer rapport med avvik, alvorlighet, og anbefalte tiltak basert på konfigurerbart regelset. |
| **`arch-propose`** | `arch-escalate` (PR-delen) | Eksplisitt steg for å foreslå arkitekturendring tilbake til sentral arkitektur via PR. |

### Hva som fjernes fra løsningsrepoer

- **Alle hooks** (pre/post-tool gating) — beholdes kun i sentral arkitektur-repo
- **Sekvensiell skill-avhengighet** — ingen skill krever at en annen har kjørt først
- **Automatisk klassifisering** (Class A/B/C) — erstattes av compliance-profilens konfigurerbare regler
- **arch-intake**, **arch-consume**, **arch-escalate** — fjernes helt
- **arch-brainstorming**, **arch-writing-plans**, **arch-systematic-debugging**, **arch-requesting-code-review** — fjernes, erstattes av standard superpowers-skills uten arch-gating (agenten har wiki-kontekst tilgjengelig uansett)

### Designprinsipper

1. **Arkitektur er kontekst og inspirasjon** — ikke en gate
2. **Agenter har frihet til å innovere** — ingen pre-gating under implementasjon
3. **Compliance sjekkes som en bevisst handling etterpå** — ikke per operasjon
4. **Agenten foreslår tiltak, mennesket bestemmer** — compliance-rapporten er rådgivende
5. **Kunnskap compounderer** — wiki vokser over tid, compliance-rapporter blir input
6. **Innovasjon flyter tilbake** — løsningsrepoer kan foreslå arkitekturendringer via PR

---

## Wiki-laget

### Hvorfor wiki fremfor statiske dokumenter

Arkitekturdokumenter har en tendens til å bli skrevet én gang og deretter ignorert. Wiki-mønsteret løser dette ved å gjøre kunnskap til noe som **brukes aktivt og vokser organisk**. Agenter leser ikke et 50-siders dokument — de navigerer mellom sammenkoblede konseptsider og følger lenker etter behov.

Wiki-tilnærmingen gir også et naturlig sted for kunnskap som ikke passer inn i normative dokumenter: designvalg, compliance-resultater, mønstre som har fungert. I den gamle modellen forsvant denne kunnskapen. I wiki-modellen compounderer den.

### Tolagsmodell

**Sentral arkitektur-wiki** (i agent-arch repoet):

| Element | Beskrivelse |
|---|---|
| `raw/` | Normative arkitekturdokumenter (ArchiMate-lagdelt). Immutable for agenter — kun mennesker og `arch-governance` endrer disse |
| `wiki/` | Agentoptimalisert kunnskapsbase. Generert fra `raw/`, vedlikeholdt av governance-skillen |
| `wiki/index.md` | Innholdsfortegnelse med one-liners — agentens startpunkt |
| `wiki/log.md` | Append-only endringslogg — sporbarhet |
| Konseptsider | Én side per nøkkelkonsept med `[[wiki-links]]` mellom relaterte konsepter |

**Lokal arkitektur-wiki** (i hvert løsningsrepo):

| Element | Beskrivelse |
|---|---|
| `docs/arch-wiki/raw/central/` | Synkronisert fra sentral wiki (read-only snapshot) |
| `docs/arch-wiki/raw/local/` | Lokale normative kilder agenten ikke har skrevet (importerte docs) |
| `docs/arch-wiki/raw/external/` | Tredjepartsdocs, standarder |
| `docs/arch-wiki/wiki/` | Agentvedlikeholdt kunnskapsbase |
| `docs/arch-wiki/wiki/index.md` | Lokal innholdsfortegnelse |
| `docs/arch-wiki/wiki/log.md` | Lokal endringslogg |
| `docs/arch-wiki/compliance-profile.yaml` | Konfigurerbart regelset |

### Kunnskapsflyt

```
+-----------------------------------+
|   Sentral arkitektur-wiki         |
|   (agent-arch/wiki/)              |
|                                   |
|   raw/ -> wiki/ (governance)      |
|   index.md, konseptsider,         |
|   [[wiki-links]], log.md          |
|                                   |
|         ^ arch-propose (PR)       |
|         |                         |
+---------+-------------------------+
          |
    +-----+--------------------------+
    |     |  Løsningsrepo            |
    |     |                          |
    |  docs/arch-wiki/               |
    |     |                          |
    |  arch-context    arch-compliance|
    |  (leser sentral  (sjekker mot  |
    |   wiki, bygger   compliance-   |
    |   lokal wiki)    profil)       |
    |                                |
    |  Agenten jobber fritt,         |
    |  wiki compounderer over tid    |
    +--------------------------------+
```

---

## Typede wiki-sider

### Hvorfor typer

I en ren wiki uten typer mister man evnen til å spørre "hvilke beslutninger har vi tatt?" vs "hva forstår vi om domenet?". Ved å gi hver side en type i frontmatter får vi det beste fra to verdener:

- **Friheten** til at alt lever i én sammenhengende wiki med naturlige krysslenker
- **Strukturen** til å kunne filtrere og resonnere over *hva slags* kunnskap noe er

ADR-er, designdocs og API-kontrakter er ofte skrevet *av* agenten, *sammen med* et menneske. De er ikke eksterne kilder man ingesterer — de er beslutninger tatt underveis. Derfor hører de hjemme i `wiki/` som typede sider, ikke i `raw/` som later som de er eksterne kilder.

`raw/` er reservert for genuint eksterne/importerte kilder: sentral arkitektur, tredjepartsstandarder, importerte dokumenter.

### Typedefinisjoner

| Type | Formål | Compliance-relevans |
|---|---|---|
| `concept` | Domeneforståelse, forklaringer | Kontekst — sjekkes ikke direkte |
| `decision` | Designvalg, ADR-er | Sjekkes mot arkitekturen — er beslutningen alignet? |
| `contract` | API-kontrakter, grensesnitt | Sjekkes for kompatibilitet |
| `pattern` | Mønstre og best practices | Sjekkes som soft-anbefaling |
| `review` | Compliance-rapporter, audit-resultater | Kilde til neste ingest-runde |

### Wiki-sidekontrakt

Hver wiki-side følger en fast struktur:

```markdown
---
type: concept | decision | contract | pattern | review
status: draft | active | superseded | deprecated
date: 2026-04-12
sources:
  - raw/central/informasjon/fhir/resources.md
  - raw/external/hl7-fhir-r4.md
superseded-by: wiki/newer-page.md  # kun hvis status: superseded
---

# Sidetittel

**Sammendrag**: Én til to setninger som beskriver denne siden.

---

Hovedinnhold her. Bruk klare overskrifter og korte avsnitt.
Lenk til relaterte konsepter med [[wiki-links]] gjennom teksten.

Hver faktapåstand refererer til sin kilde (kilde: raw/central/...).

## Relaterte sider

- [[relatert-konsept-1]]
- [[relatert-konsept-2]]
```

### Siteringsregler

- Hver faktapåstand i wiki refererer til sin kilde: `(kilde: raw/local/adrs/adr-003.md)`
- Hvis sentral og lokal kilde er i konflikt, noter motsetningen eksplisitt
- Påstander uten kilde markeres som "trenger verifisering"
- Compliance-rapporten kan bruke disse siteringene for å spore *hvorfor* noe er et avvik

---

## Skill 1: `arch-context`

### Formål

Gi agenten rik, relevant arkitekturkontekst som inspirasjon — ikke som en gate. Bygge og vedlikeholde en lokal arkitektur-wiki som compounderer kunnskap over tid.

### Hvorfor denne skillen finnes

Agenter gjør bedre arbeid når de forstår konteksten de opererer i. Men det er forskjell på å *tvinge* en agent gjennom en sjekkliste og å *tilby* en kunnskapsbase den kan bruke når den trenger det. `arch-context` er agentens oppslagsverk — den bruker det når det gir verdi, ikke fordi den må.

### Når den brukes

- Frivillig, når som helst i arbeidsflyten
- Typisk ved oppstart av nytt arbeid, eller når agenten trenger domeneforståelse
- Kan kjøres gjentatte ganger — hver kjøring kan hente mer fra sentral wiki

### Hva den gjør

```
1. ORIENTERING
   - Les lokal wiki/index.md (hvis den finnes)
   - Les sentral wiki/index.md (fra raw/central/)
   - Identifiser relevante konseptsider basert på oppgaven

2. KONTEKSTBYGGING
   - Les relevante wiki-sider (lokale først, sentrale som supplement)
   - Følg [[wiki-links]] for å bygge forståelse
   - Presenter nøkkelkontekst til agenten

3. INGEST (når nye kilder finnes)
   - Les kildedokument fra raw/
   - Diskuter nøkkelfunn med utvikler
   - Opprett/oppdater konseptsider i wiki/ med riktig type
   - Legg til [[wiki-links]]
   - Oppdater index.md og log.md

4. TILBAKESKRIVING (etter arbeid)
   - Agenten kan skrive nye wiki-sider for ting den lærte
   - Designvalg -> type: decision
   - Nye mønstre -> type: pattern
   - Domeneforståelse -> type: concept
```

### Hva den IKKE gjør

- Klassifiserer ikke endringer (Class A/B/C)
- Blokkerer ingen handlinger
- Krever ikke at andre skills har kjørt
- Validerer ikke compliance

---

## Skill 2: `arch-compliance`

### Formål

On-demand compliance-sjekk som produserer en rapport med avvik, alvorlighet, og anbefalte tiltak. Agenten foreslår, mennesket bestemmer.

### Hvorfor denne skillen finnes

Frihet uten feedback er ikke frihet — det er ubevissthet. Compliance-skillen gir teamet et klart bilde av hvor løsningen står i forhold til arkitekturen, uten å bremse arbeidet underveis. Den er en *bevisst handling* — teamet velger å sjekke status fordi de vil ta informerte valg, ikke fordi de er tvunget.

Compliance-rapporten har en dobbel rolle: den er både et **beslutningsgrunnlag** og en **kunnskapskilde**. Når den lagres som en `type: review` wiki-side, blir den input til neste ingest-runde, og wikien blir rikere. Slik compounderer kunnskap — avvik blir til lærdom.

### Når den brukes

- Eksplisitt, når teamet ønsker å sjekke compliance-status
- Typisk etter en implementasjonsfase, før PR, eller ved milepæler
- Kan kjøres periodisk for å følge med på drift

### Hva den sjekker

Compliance-skillen sjekker mot et konfigurerbart regelset definert i `compliance-profile.yaml`:

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

Ulike team har ulike modenhets- og risikonivå. Et team som bygger en sikkerhetskritisk tjeneste trenger strengere harde krav enn et team som lager interne verktøy. Ved å gi teamet eierskap over profilen flyttes ansvar til teamet, sentral arkitektur forblir rådgivende, og gradvis adopsjon er mulig.

### Hva den produserer

```markdown
---
type: review
date: 2026-04-12
scope: feature/medication-history
sources:
  - raw/central/sikkerhet/consent.md
  - wiki/medication-api.md
  - wiki/adr-003-event-sourcing.md
---

# Compliance Review: Medication History Feature

## Sammendrag
3 hard avvik, 1 soft anbefaling, 2 info-observasjoner

## Hard avvik
1. **Manglende consent-sjekk ved API-kall**
   Kilde: raw/central/sikkerhet/consent.md
   Berørt kode: src/api/medication.ts:45-62
   Anbefalt tiltak: Implementer consent-middleware
   Alternativt tiltak: Foreslå arkitekturendring hvis consent-modellen ikke passer

## Soft anbefalinger
1. **Event-navn følger ikke navnekonvensjon**
   ...

## Info
1. **Bruker REST der arkitekturen anbefaler GraphQL**
   Merknad: Lokal decision (adr-003) begrunner valget
   ...

## Wiki-helse
- 2 orphan-sider funnet
- 1 konsept nevnt uten egen side: [[audit-logging]]
- 0 motstrid mellom lokal og sentral wiki
```

### Wiki-helse (lint)

Inspirert av LLM Wiki-mønsteret sjekker compliance-skillen også wiki-helsen:

- Orphan-sider (ingen innkommende lenker)
- Konsepter nevnt uten egen side
- Utdaterte sider (eldre enn konfigurert terskel)
- Påstander uten kildehenvisning
- Motstrid mellom lokal og sentral wiki

### Feedback-loop: compliance -> kunnskap

```
Implementer fritt
       |
arch-compliance -> rapport (type: review)
       |
Rapport lagres i wiki/
       |
Neste ingest -> wiki oppdateres med lærdom
       |
Agenten er smartere neste gang
```

---

## Skill 3: `arch-propose`

### Formål

Foreslå endringer tilbake til sentral arkitektur via PR, basert på innovasjon og erfaringer fra løsningsrepoet.

### Hvorfor denne skillen finnes

Arkitektur som bare flyter *nedover* (fra sentral til løsning) blir utdatert. Den virkelige verdien oppstår når innovasjon i løsningsrepoene flyter *tilbake* og forbedrer arkitekturen for alle. `arch-propose` gjør denne tilbakeflytingen til en eksplisitt, sporbar handling.

Skillen bygger på wiki-kunnskapen: den bruker lokale `decision`-sider, `review`-rapporter, og `pattern`-sider som dokumentasjon av *hva* som ble gjort og *hvorfor* det fungerte. Dette gir sentral arkitektur-teamet et rikt beslutningsgrunnlag.

### Når den brukes

- Eksplisitt, etter at compliance-rapport har identifisert avvik teamet mener bør løses i arkitekturen
- Når teamet har funnet et mønster som fungerer bedre enn det arkitekturen foreskriver
- Når nye konsepter bør inn i sentral wiki

### Hva den gjør

```
1. SAMLE EVIDENS
   - Les relevante wiki-sider (decisions, patterns, reviews)
   - Identifiser hvilke sentrale docs som berøres
   - Bygg en argumentasjon basert på lokal erfaring

2. KLASSIFISER ENDRING
   - Klargjøring/tillegg -> enklere PR
   - Ny anbefaling/mønster -> PR med begrunnelse
   - Prinsipiell endring -> Issue først, deretter PR

3. OPPRETT PR MOT SENTRAL ARKITEKTUR
   - Foreslå endringer i relevante docs i raw/
   - Foreslå oppdateringer i sentral wiki/
   - Inkluder lenker til lokal evidens
   - Tilordne til arkitektur-teamet for review

4. OPPDATER LOKAL WIKI
   - Marker berørte sider som "foreslått endring pending"
   - Logg i wiki/log.md
```

---

## Compliance-profil

### Konfigurasjon

```yaml
# docs/arch-wiki/compliance-profile.yaml

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
      source: wiki/*  # type: contract

  soft:
    - id: naming-conventions
      source: raw/central/konvensjoner/
    - id: documentation-standards
    - id: preferred-patterns
      source: wiki/*  # type: pattern

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

# Wiki-helse
wiki-health:
  check-orphans: true
  check-missing-concepts: true
  check-stale-pages: 90d
  check-source-conflicts: true
```

### Hvorfor konfigurerbar profil

Ulike team har ulike modenhets- og risikonivå. Ved å gi teamet eierskap over profilen:

- **Ansvar flyttes til teamet** — de bestemmer hva som er viktig for dem
- **Sentral arkitektur forblir rådgivende** — den definerer *hva* som finnes, ikke *hvor strengt* hvert team følger det
- **Gradvis adopsjon** — nye team starter med en minimal profil og utvider etter hvert
- **Unngå one-size-fits-all** — som var kjerneproblemet med de gamle gatede skillsene

---

## Migrering

### Strategi: Én omgang, ingen overgangsperiode

Ren overgang. Gamle skills fjernes helt, nye erstatter. Dette gir et klart signal om paradigmeskiftet og unngår kompleksiteten med å støtte to modeller parallelt.

### Hva som endres

| Dagens modell | Ny modell | Handling |
|---|---|---|
| `arch-intake` | Fjernes | Absorbert av `arch-context` |
| `arch-consume` | Fjernes | Erstattet av `arch-context` |
| `arch-escalate` | Fjernes | Lesedel -> `arch-context`, PR-del -> `arch-propose` |
| `arch-governance` | **Beholdes, tilpasses** | Vedlikeholder sentral wiki i tillegg til normative docs |
| `arch-brainstorming` | Fjernes | Standard superpowers-brainstorming (wiki gir kontekst) |
| `arch-writing-plans` | Fjernes | Standard superpowers-writing-plans (wiki gir kontekst) |
| `arch-systematic-debugging` | Fjernes | Standard superpowers-debugging (wiki gir kontekst) |
| `arch-requesting-code-review` | Fjernes | `arch-compliance` + standard code review |
| Hooks i løsningsrepo | **Fjernes helt** | Ingen pre/post-tool gating |
| Hooks i sentral repo | **Beholdes** | Sentral arkitektur trenger fortsatt governance |
| `arch-policy.sh` | **Refaktoreres** | Klassifiseringslogikk gjenbrukes i compliance og propose |
| `arch-read.sh` | **Beholdes, utvides** | Brukes av `arch-context` for lesing av raw/ |
| `solution-standard.manifest` | **Oppdateres** | Ny filstruktur med wiki/, compliance-profile.yaml |
| `install-method.sh` | **Oppdateres** | Bootstrapper wiki-struktur og default compliance-profil |

### Migreringssekvens for sentral repo

```
Fase 1: Opprett wiki-laget
   - Opprett wiki/ med index.md og log.md
   - Generer konseptsider fra eksisterende raw/ docs
   - arch-governance lærer å vedlikeholde wikien

Fase 2: Nye skills
   - Implementer arch-context, arch-compliance, arch-propose
   - Fjern arch-intake, arch-consume, arch-escalate
   - Fjern arch-brainstorming, arch-writing-plans, arch-systematic-debugging, arch-requesting-code-review
   - Oppdater solution-standard.manifest
   - Oppdater install-method.sh

Fase 3: Oppdater templates
   - Ny AGENTS.md.tmpl som refererer nye skills
   - Ny compliance-profile.yaml default-template
   - Ny wiki-bootstrap template

Fase 4: Dokumentasjon
   - Oppdater docs/adoption/ med ny modell
   - Oppdater docs/method/ med wiki-mønsteret
```

### Migreringssekvens for løsningsrepoer

```
Fase 1: Oppdater agent-arch install
   - Kjør oppdatert install-method.sh
   - Gamle skills erstattes av nye
   - Hooks fjernes
   - Wiki-struktur bootstrappes

Fase 2: Initial ingest
   - arch-context kjøres første gang
   - Sentral wiki synkroniseres til raw/central/
   - Eksisterende lokale docs flyttes til raw/local/ eller wiki/
   - Initial wiki genereres

Fase 3: Konfigurer compliance-profil
   - Team tilpasser compliance-profile.yaml
   - Velger hvilke regler som er hard/soft/info
   - Setter scope for hva som sjekkes

Fase 4: Daglig bruk
   - Agenter bruker arch-context når de vil
   - Team kjører arch-compliance når de vil
   - Wiki vokser organisk
```

---

## Filstruktur etter migrering

### Sentral arkitektur-repo

```
agent-arch/
+-- raw/                          # Normative arkitekturdokumenter
|   +-- motivasjon/
|   +-- strategi/
|   +-- sikkerhet/
|   +-- informasjon/
|   +-- ...
+-- wiki/                         # Agentoptimalisert kunnskapsbase
|   +-- index.md
|   +-- log.md
|   +-- [konseptsider].md
+-- .github/
|   +-- skills/
|   |   +-- arch-context/         # NY
|   |   +-- arch-compliance/      # NY
|   |   +-- arch-propose/         # NY
|   |   +-- arch-governance/      # OPPDATERT
|   +-- hooks/                    # Beholdes for sentral repo
+-- scripts/
|   +-- arch-read.sh              # Beholdes
|   +-- ...
+-- install/
|   +-- profiles/
|       +-- solution-standard.manifest  # OPPDATERT
+-- templates/                    # OPPDATERT med wiki-struktur
+-- docs/
    +-- adoption/
    +-- method/
    +-- reference/
    +-- solution-space/
```

### Løsningsrepo etter install

```
docs/arch-wiki/
+-- raw/
|   +-- central/                  # Synkronisert fra sentral wiki
|   +-- local/                    # Importerte lokale kilder
|   +-- external/                 # Tredjepartsdocs
+-- wiki/
|   +-- index.md
|   +-- log.md
|   +-- [konseptsider].md         # Typede sider
+-- compliance-profile.yaml       # Konfigurerbart regelset
```

---

## Oppsummering av designvalg og begrunnelser

| Designvalg | Begrunnelse |
|---|---|
| Fjerne alle pre-gates | Den samlede effekten av barrierene hemmer kreativitet mer enn den sikrer kvalitet |
| Wiki fremfor statiske docs | Kunnskap som brukes aktivt og vokser organisk er mer verdifull enn dokumenter som leses én gang |
| Typede wiki-sider (ikke raw/ for agentskrevet innhold) | ADR-er og designdocs er beslutninger tatt underveis, ikke eksterne kilder. Typer gir filtrering uten å bryte wiki-flyten |
| Konfigurerbar compliance-profil | Unngå one-size-fits-all. Ansvar flyttes til teamet. Sentral arkitektur forblir rådgivende |
| Compliance som bevisst handling | Frihet uten feedback er ubevissthet. Men feedback skal komme når teamet er klare for det, ikke som en bremse |
| Agenten foreslår, mennesket bestemmer | Holder ansvaret der det hører hjemme |
| Toveis-flyt via arch-propose | Arkitektur som bare flyter nedover blir utdatert. Innovasjon må kunne flyte tilbake |
| Én omgang migrering | Klart signal om paradigmeskifte. Unngå kompleksitet med to parallelle modeller |
| Compliance-rapport som wiki-side (type: review) | Dobbel rolle: beslutningsgrunnlag OG kunnskapskilde. Compounderer lærdom over tid |
| LLM Wiki-mønster som fundament | Bevist mønster for levende kunnskapsbaser. Ingest, wiki-links, lint, og compounding kunnskap |
