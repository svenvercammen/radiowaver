# Radio Waver — tijdelijke event-webradio

Live audio van het mengpaneel → event-pc → Icecast op de VM → webspelers.
Bewust simpel: één lichte Icecast-container, een statische spelerpagina, en de
bestaande Caddy ervoor.

Domein: **radio.waver.be** · Repo: <https://github.com/svenvercammen/radiowaver>

```
mengpaneel ──► audio-ingang pc ──► encoder (BUTT) ──┐  via internet
                                                    ▼
luisteraars ◄── Caddy (radio.waver.be) ◄── Icecast2 (Docker, poort 8000)
```

Draait op dezelfde OVH-VM als **waverfeest.be** en **daak.be** (Docker op
Ubuntu, Caddy als reverse proxy met automatische HTTPS).

---

## Status & fasering

| Fase | Inhoud | Status |
|------|--------|--------|
| **1 — Publiek + dev** | Statische spelerpagina, Icecast-container, lokale dev-omgeving, uitrol-docs | **opgeleverd** |
| **2 — Beheer** | Beheerpagina achter **Keycloak**-login: mededelingenbalk, **live berichten** (gemodereerd), agenda (CRUD, met affiche + rich-text) en partners (met logo). Publieke pagina wordt dynamisch gevuld. | **opgeleverd** |
| **3 — Always-on** | **Liquidsoap**-fallback: bij geen live speelt automatisch een **MP3-lus** (beheerbaar, te ordenen). Site toont *live* vs *non-stop muziek*. | **opgeleverd** |

Beslissingen:
- **Luisteren is publiek**, geen login (PRD B3).
- **De bron levert aan met het `source`-wachtwoord** op de Liquidsoap-harbor (8005).
- **Beheer** zit achter een **eigen Keycloak-container** (rol `beheerder`).
- **Always-on radio** via Liquidsoap (PRD §11-uitbreiding): live heeft voorrang,
  valt automatisch terug op de muziek-lus; één naadloze `/live`-stream.
- **Geen secrets in git**: alle wachtwoorden komen uit `.env`.

### Beheer in het kort

- Subtiel **slot-icoon** in de footer van de site → **/beheer/** (Keycloak-login).
- Hoofdpagina **/beheer/**: Mededeling + Partners (inline), en links naar de
  aparte pagina's hieronder.
- **/beheer/berichten/** — live berichten: insturen, **goedkeuren** en CRUD.
- **/beheer/agenda/** — evenementen: toevoegen/bewerken/verwijderen + **slepen**
  voor de volgorde, met affiche en rich-text uitleg.
- **/beheer/muziek/** — bron bij geen live: **eigen MP3-lijst** (uploaden,
  **slepen**, aan/uit) of een **internetradio relayen** (kies een voorbeeld of
  vul een eigen stream-URL in). Bij een bronwissel herstart Liquidsoap even
  (~5s). De publieke pagina toont "Speelt momenteel: Live / Autoplay / <zender>".
  - Relay-aandachtspunten: gebruik **http://**-stream-URL's (https faalt soms in
    ffmpeg), en zorg dat je het **recht hebt om te heruitzenden** (licentie). Voor
    vrij te gebruiken muziek: Creative Commons-zenders of de Free Music Archive.
- De publieke pagina haalt mededeling/berichten/agenda/partners op uit
  `GET /api/content` (ververst elke 15 s; statische fallback).

---

## Mappenstructuur

```
radiowaver/
├─ icecast/                 Icecast2-container (Dockerfile, template, entrypoint)
├─ backend/                 FastAPI-beheer-API (SQLite + uploads)
│  ├─ Dockerfile
│  ├─ requirements.txt
│  └─ app/                  main.py (routes), auth.py (Keycloak), db.py
├─ web/
│  ├─ index.html            publieke spelerpagina (dynamisch gevuld)
│  └─ beheer/index.html     beheerpagina achter Keycloak-login
├─ infra/keycloak/          realm-import (radiowaver-realm.json)
├─ docker-compose.yml       productie: icecast + api + keycloak + web
├─ docker-compose.dev.yml   dev: volledige stack op http://localhost:8080
├─ Caddyfile.web            interne Caddy van de prod web-container (:80)
├─ Caddyfile.snippet        blok voor de gedeelde Caddy op de VM
├─ Caddyfile.dev            lokale dev-Caddy (geen TLS)
├─ .env.example             sjabloon voor alle secrets (kopieer naar .env)
├─ .gitignore
└─ briefing/                oorspronkelijke brief + PRD + design
```

---

## 1. Dev-omgeving (lokaal)

Vereist: **Docker Desktop** (Windows/Mac) of Docker Engine + compose-plugin.

```bash
# 1. Secrets aanmaken (eenmalig)
cp .env.example .env
#   zet ICECAST_HOSTNAME=localhost voor lokaal testen en kies wachtwoorden

# 2. Volledige stack starten (icecast + api + keycloak + caddy)
docker compose -f docker-compose.dev.yml up --build
```

Open **<http://localhost:8080>**. Zonder bron staat de speler op *offline* met
een uitgeschakelde knop. Stoppen: `Ctrl-C`, of `docker compose -f
docker-compose.dev.yml down`.

**Beheer lokaal:** <http://localhost:8080/beheer/> — login **`beheerder`** /
**`radiowaver`** (eerste keer: profiel aanvullen + wachtwoord wijzigen).
Keycloak heeft na de start ~15 s nodig om het realm te importeren.

### Een test-bron pushen (zonder mengpaneel)

De pagina springt pas op *on air* zodra er audio op `/live` staat. Twee opties:

**A. Met ffmpeg** (een toon of een mp3-bestand in een lus):

```bash
# Een 440 Hz testtoon, oneindig, naar de dev-Icecast:
ffmpeg -re -f lavfi -i "sine=frequency=440:sample_rate=44100" \
  -acodec libmp3lame -b:a 128k -content_type audio/mpeg -legacy_icecast 1 \
  "icecast://source:<JOUW_SOURCE_PW>@localhost:8005/live"

# Of een bestaand mp3'tje in een lus:
ffmpeg -re -stream_loop -1 -i muziek.mp3 \
  -acodec libmp3lame -b:a 128k -content_type audio/mpeg -legacy_icecast 1 \
  "icecast://source:<JOUW_SOURCE_PW>@localhost:8005/live"
```

**B. Met BUTT** — zelfde instellingen als hieronder, maar Address `localhost`.

Zodra de bron loopt, toont <http://localhost:8080> *on air* en kun je luisteren.

---

## 2. Uitrol op de VM (productie)

De agent kan de VM niet bereiken — draai dit zelf op de server. Radio Waver past
in het bestaande patroon van de VM: een **gedeelde Caddy in Docker** op het
externe netwerk **`web`** routeert per containernaam. Radio Waver draait als
eigen compose-project `radiowaver-prod` met vijf containers:

- `radiowaver-liquidsoap-prod` — mengt live + muziek tot één doorlopende stream
  en publiceert poort **8005** (BUTT levert hier aan). Valt automatisch terug op
  de MP3-lus als er geen live is.
- `radiowaver-icecast-prod` — Icecast; ontvangt de stream van Liquidsoap, intern.
- `radiowaver-api-prod` — FastAPI-beheer (SQLite + uploads + playlist), intern.
- `radiowaver-keycloak-prod` — eigen Keycloak (login voor het beheer), intern.
- `radiowaver-web-prod` — Caddy die de speler serveert en `/live`, `/api`,
  `/auth` en `/uploads` intern routeert; hangt aan `web`, **geen** host-poort.

**Vooraf (jij):** DNS voor `radio.waver.be` → IP van de VM, en het netwerk `web`
bestaat al (van JEKA/daak). Check: `docker network ls | grep web`.

1. **Repo + secrets.**
   ```bash
   git clone https://github.com/svenvercammen/radiowaver.git
   cd radiowaver
   cp .env.example .env        # vul ALLE waarden in (Icecast + Keycloak + issuer)
   ```
   Belangrijk in `.env`: `ICECAST_HOSTNAME=radio.waver.be`,
   `PUBLIC_URL=https://radio.waver.be`,
   `KEYCLOAK_ISSUER=https://radio.waver.be/auth/realms/radiowaver`,
   `KEYCLOAK_INTERNAL_ISSUER=http://keycloak:8080/auth/realms/radiowaver`.

2. **Starten.**
   ```bash
   docker compose up -d --build
   docker compose ps           # alle vier Up (keycloak ~30-60s)
   docker compose logs -f web keycloak
   ```

3. **Gedeelde Caddy.** Plak het blok uit `Caddyfile.snippet` bij de bestaande
   reverse-proxy en herlaad de gedeelde Caddy (`docker exec reverse-proxy-caddy
   caddy reload --config /etc/caddy/Caddyfile`). Caddy regelt automatisch TLS.

4. **Firewall.** Open poort **8005** voor de bron (Liquidsoap-harbor), bij
   voorkeur beperkt tot het IP van de event-pc.

5. **Beheer in gebruik nemen.** Surf naar <https://radio.waver.be/beheer/> en log
   in met **`beheerder`** / **`radiowaver`**. Bij de eerste login vul je je
   profiel aan en kies je een **nieuw wachtwoord**. (De master-admin console
   staat op `/auth/admin` met `KC_ADMIN`/`KC_ADMIN_PASSWORD` uit `.env`.)

6. **Testen.** Surf naar <https://radio.waver.be>. Offline tot er een bron is;
   *on air* zodra je aanlevert.

> Draait de Caddy op de VM toch op de **host** (niet in Docker)? Zie de
> alternatieve variant onderaan `Caddyfile.snippet` (proxy rechtstreeks naar
> `127.0.0.1:8000` + spelerpagina naar `/srv/radio-waver/web`).

### Na het event

```bash
docker compose down
```
Verwijder het `radio.waver.be`-blok uit de gedeelde Caddy en herlaad.

---

## 3. Aanleveren vanaf de event-pc (BUTT)

[BUTT](https://danielnoethen.de/butt/) = Broadcast Using This Tool. Gratis, GUI,
Windows/macOS/Linux. *Settings → Main*:

| Veld | Waarde |
|------|--------|
| Server type | Icecast |
| Address | `radio.waver.be` |
| Port | `8005` |
| Password | je `source`-wachtwoord uit `.env` |
| Icecast mountpoint | `/live` |
| Icecast user | `source` |

*Settings → Audio*: kies de geluidskaart / USB-interface (de ingang van het
mengpaneel), codec **MP3**, bitrate **128 kbps**. Stel het volume zo in dat de
master niet clipt. Druk op **Play** om uit te zenden.

> De bron levert aan op poort **8005** (Liquidsoap-harbor), niet rechtstreeks op
> Icecast. Stop je met uitzenden, dan schakelt de radio automatisch over op de
> non-stop muziek (beheer via *Beheer → Muziek*). Beperk 8005 in de firewall tot
> het IP van de event-pc.

---

## Capaciteit

50 luisteraars × 128 kbps ≈ 6–7 Mbps uitgaand op de piek. Verwaarloosbaar naast
waverfeest.be en daak.be; CPU/RAM van Icecast is minimaal.

## Beveiliging

- Wachtwoorden staan in `.env` (gitignored), niet in de repo.
- De Icecast admin-interface is niet publiek via `radio.waver.be` bereikbaar:
  Caddy proxyt enkel `/live` en `/status-json.xsl`.
- Beperk poort 8005 (bron) in de firewall tot het IP van de event-pc waar mogelijk.

## Documentatie

- **Handleiding (zenden + luisteren, BUTT):** [handleiding.md](handleiding.md)
- **PRD:** [briefing/radiowaver-prd.md](briefing/radiowaver-prd.md)
- **Oorspronkelijke brief:** [briefing/README.md](briefing/README.md)
