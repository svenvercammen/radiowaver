# PRD — Radio Waver (radio.waver.be)

| | |
|---|---|
| **Project** | Radio Waver — tijdelijke event-webradio |
| **Domein** | radio.waver.be |
| **Status** | Concept / klaar voor uitrol |
| **Datum** | 27 juni 2026 |
| **Type** | Tijdelijk project, gekoppeld aan een evenement |

## 1. Samenvatting

Radio Waver is een tijdelijke webradio die het live geluid van een mengpaneel
op het evenement uitzendt naar luisteraars via het web. De keten loopt van het
mengpaneel naar de audio-ingang van een pc op locatie, vandaar via een encoder
naar een Icecast-server op de bestaande VM, en via de bestaande Caddy reverse
proxy naar de browsers van de luisteraars. Het project is bewust eenvoudig en
makkelijk op te zetten en weer af te breken.

```
mengpaneel ──► audio-ingang pc ──► encoder (BUTT) ──┐  via internet
                                                    ▼
luisteraars ◄── Caddy (radio.waver.be) ◄── Icecast2 (Docker, poort 8000)
```

## 2. Doel & context

Het doel is dat bezoekers en thuisblijvers de live-uitzending van het evenement
kunnen volgen via een eenvoudige webpagina, zonder app of account. Het is
nadrukkelijk **live audio** (één doorlopende uitzending), geen on-demand
muziekdienst.

Het project draait op de bestaande infrastructuur naast twee andere projecten
(waverfeest.be en daak.be) op dezelfde OVH-VM. Bestaande bouwstenen die
hergebruikt worden: Docker op Ubuntu, Caddy als reverse proxy met automatische
HTTPS, en een aanwezige dev-omgeving. Keycloak is beschikbaar op de VM maar
wordt voor dit project niet ingezet (luisteren is publiek).

## 3. Scope

**In scope**
- Eén live audiostream uitzenden vanaf een mengpaneel.
- Publieke spelerpagina op radio.waver.be met afspeelknop en live-status.
- Icecast-server in Docker, ingepast achter de bestaande Caddy.
- Documentatie voor uitrol en voor aanlevering vanaf de event-pc.

**Out of scope**
- On-demand luisteren, opnames of een archief van uitzendingen.
- Gebruikersaccounts, login of toegangsbeperking op het luisteren.
- Meerdere gelijktijdige zenders/kanalen.
- Native mobiele apps.
- Automatische muziek-/jingleprogrammering (zie open punten).

## 4. Gebruikers & scenario's

**Luisteraar.** Opent radio.waver.be, ziet of er live wordt uitgezonden, drukt
op afspelen en luistert. Werkt in een gewone browser op desktop en mobiel,
zonder installatie.

**Zender / techniek op locatie.** Sluit het mengpaneel aan op de audio-ingang
van de pc, opent de encoder (BUTT), en start de uitzending. Kan tijdens het
event de uitzending pauzeren en hervatten.

**Beheerder.** Rolt het project uit op de VM, beheert de Icecast-config en
wachtwoorden, en breekt het na het event weer af.

## 5. Functionele requirements

- **F1.** Het systeem zendt één live audiostream uit op mount `/live`.
- **F2.** Luisteraars kunnen de stream afspelen via een afspeelknop op de
  publieke pagina (geen autoplay; speelt na een gebruikersactie).
- **F3.** De pagina toont een duidelijke on-air-/offline-indicatie op basis van
  de werkelijke status van de stream.
- **F4.** De pagina toont het actuele aantal luisteraars.
- **F5.** Zolang er geen bron aanlevert, toont de pagina een "nog niet live"-
  boodschap en is de afspeelknop uitgeschakeld.
- **F6.** De zender levert aan via een eenvoudige encoder (BUTT) met
  wachtwoordbeveiliging op de bron.
- **F7.** De spelerpagina haalt de status same-origin op (via Caddy), zodat er
  geen CORS-configuratie nodig is.

## 6. Niet-functionele requirements

- **NF1 — Capaciteit.** Ontworpen voor maximaal **50 gelijktijdige
  luisteraars**. Bij 128 kbps komt dat neer op ±6–7 Mbps uitgaand op de piek;
  verwaarloosbaar voor de VM. Mount-limiet staat op 55 met wat globale marge.
- **NF2 — Compatibiliteit.** Codec **MP3 @ 128 kbps** voor universele
  afspeelbaarheid in alle browsers, inclusief iOS Safari.
- **NF3 — Eenvoud.** Geen automatische fallback of complexe audio-engine; één
  bron, één encoder, één container.
- **NF4 — Resourcevriendelijk.** Mag de bestaande projecten op de VM niet
  hinderen; Icecast is licht qua CPU/RAM, de enige relevante belasting is
  bandbreedte tijdens het event.
- **NF5 — Beveiliging.** Bron, relay en admin met wachtwoord. De
  admin-interface is niet publiek via radio.waver.be bereikbaar (Caddy proxyt
  enkel `/live` en de statusendpoint).
- **NF6 — Onderhoudsgemak.** Self-contained Docker-image (eigen Dockerfile,
  geen afhankelijkheid van een extern image dat kan verdwijnen). In één commando
  op te zetten en af te breken.
- **NF7 — Toegankelijkheid.** Spelerpagina werkt responsive op mobiel, heeft
  zichtbare toetsenbordfocus en respecteert `prefers-reduced-motion`.

## 7. Architectuur

De signaalketen bestaat uit twee zones: de **event-pc** (mengpaneel, audio-
ingang, encoder) en de **OVH-VM** (Icecast in Docker, Caddy als reverse proxy).
De encoder duwt de stream over het internet naar Icecast; Caddy zet er TLS op en
serveert zowel de stream als de statische spelerpagina onder radio.waver.be.

| Component | Locatie | Rol |
|---|---|---|
| Mengpaneel | Event-pc | Bronaudio (master-uit) |
| Audio-ingang pc | Event-pc | Line-in / USB-interface |
| Encoder (BUTT) | Event-pc | Codeert naar MP3 en levert aan Icecast |
| Icecast2 | OVH-VM (Docker) | Ontvangt de bron, bedient luisteraars |
| Caddy | OVH-VM | TLS, reverse proxy, serveert de spelerpagina |
| Spelerpagina | OVH-VM (statisch) | Publieke webspeler met live-status |
| Luisteraars | Browser | Afspelen via HTML5-audio |

**Routing.** Luisteraars komen binnen op `radio.waver.be` (443). Caddy serveert
de statische spelerpagina op `/`, en proxyt `/live` en `/status-json.xsl` naar
Icecast met `flush_interval -1` (geen response-buffering). Bewust geen
compressie op dit blok, omdat dat een audiostream doet haperen. De bron levert
rechtstreeks aan op poort 8000 (zie beslissing B5).

## 8. Technische beslissingen

- **B1 — Live radio via Icecast.** Klassiek, volwassen en licht; past in de
  bestaande Docker-/Caddy-opzet.
- **B2 — MP3 @ 128 kbps.** Maximale compatibiliteit boven efficiëntie; Opus is
  zuiniger maar in browsers niet overal betrouwbaar voor een publiek waarvan je
  de toestellen niet controleert.
- **B3 — Publiek, geen auth.** Luisteren is open; Keycloak wordt niet ingezet.
- **B4 — BUTT als bron, geen Liquidsoap.** Doodsimpele GUI, ideaal voor een
  eenmalig event. Een automatisch vangnet (jingle bij stilte/drop) is bewust
  weggelaten om het simpel te houden.
- **B5 — Bron levert aan op poort 8000.** Het meest robuust voor een eenmalig
  event; luisteraars gaan via Caddy op 443. Poort 8000 kan in de firewall
  beperkt worden tot het IP van de event-pc. Alternatief (aanleveren over
  443/TLS) blijft open, zie sectie 11.
- **B6 — Eigen Dockerfile (Debian + icecast2).** Self-contained en volledig
  onder eigen beheer, in plaats van een extern Docker-image.
- **B7 — Caddy `flush_interval -1`, geen `encode`.** Voorkomt buffering en
  hapering op de stream.

## 9. Deliverables

| Bestand | Doel |
|---|---|
| `Dockerfile` | Bouwt de Icecast2-container |
| `docker-compose.yml` | Start de Icecast-service |
| `icecast.xml` | Icecast-config (mount `/live`, limieten, wachtwoorden) |
| `Caddyfile.snippet` | Reverse proxy + statische speler voor radio.waver.be |
| `web/index.html` | Publieke spelerpagina met live-status |
| `README.md` | Uitrol- en aanleverinstructies |

## 10. Uitrol

1. De drie wachtwoorden in `icecast.xml` instellen (en niet naar een publieke
   repo committen).
2. Icecast starten: `docker compose up -d --build`.
3. Spelerpagina plaatsen op het pad waar de Caddyfile naar wijst
   (`/srv/radio-waver/web`).
4. Het Caddy-blok in de bestaande Caddyfile plakken en Caddy herladen.
5. Aanleveren vanaf de event-pc met BUTT: Icecast, `radio.waver.be:8000`,
   mount `/live`, MP3 128 kbps, juiste audio-ingang.
6. Na het event: `docker compose down` en het Caddy-blok verwijderen.

## 11. Risico's & open punten

- **Wegvallende bron tijdens het event.** Zonder vangnet horen luisteraars
  stilte of verliezen ze de verbinding wanneer de bron wegvalt. Mitigatie binnen
  scope: snel hervatten via BUTT. Buiten scope: optionele Liquidsoap-fallback.
- **Aanleveren over poort 8000.** Eenvoudig maar minder afgeschermd; mitigatie
  via firewallregel naar het IP van de event-pc.
- **Now-playing metadata.** Bij live mengpaneelgeluid is er meestal geen
  songtitel; de pagina valt dan terug op een vaste tagline.

**Mogelijke uitbreidingen (niet in scope):**
- Aanleveren over 443/TLS in plaats van poort 8000.
- Automatische jingle-/muziekloop als vangnet bij stilte of drop.
- Uitgebreidere spelerpagina met programmaschema.

## 12. Acceptatiecriteria

- radio.waver.be laadt over HTTPS en toont de spelerpagina.
- Zonder bron staat de pagina op "offline" met uitgeschakelde afspeelknop.
- Zodra BUTT aanlevert, springt de status op "on air" en is afspelen mogelijk.
- De stream speelt zonder hoorbare hapering in courante browsers op desktop en
  mobiel, inclusief iOS Safari.
- Het luisteraarsaantal wordt op de pagina getoond en werkt bij.
- 50 gelijktijdige luisteraars worden bediend zonder hinder voor de andere
  projecten op de VM.

## 13. Addendum — beslissingen bij de uitvoering

Bijgewerkt na de start van de implementatie (repo:
<https://github.com/svenvercammen/radiowaver>). Dit addendum vult de PRD aan
zonder de oorspronkelijke tekst te herschrijven.

- **A1 — Fasering.** Fase 1 (nu opgeleverd): publieke statische spelerpagina,
  Icecast-container en een lokale dev-omgeving. Fase 2 (gepland): een
  **beheerpagina achter Keycloak-login** (now-playing tagline, status,
  wachtwoordbeheer). Dit breidt de PRD uit: luisteren blijft publiek (B3), maar
  het *beheer* van de site komt achter Keycloak.
- **A2 — Bron-login.** De bron levert in fase 1 aan met het standaard Icecast
  `source`-wachtwoord (conform B5). Een Keycloak- of token-gebaseerde bron-login
  is overwogen maar bewust uitgesteld.
- **A3 — Geen secrets in git.** De drie wachtwoorden staan niet langer in een
  gecommit `icecast.xml`. Ze komen uit `.env` (zie `.env.example`) en worden bij
  het starten in de config gerenderd (envsubst in `icecast/entrypoint.sh`). Dit
  vervangt de oorspronkelijke uitrolstap "wachtwoorden in `icecast.xml` zetten".
- **A4 — Bestandsindeling.** De deliverables uit sectie 9 zijn herschikt naar
  `icecast/` (Dockerfile, template, entrypoint) en `web/` (spelerpagina), met een
  aparte `docker-compose.dev.yml` + `Caddyfile.dev` voor lokaal testen. Zie de
  [README in de root](../README.md).
