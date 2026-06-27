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
| **1 — Publiek + dev** | Statische spelerpagina, Icecast-container, lokale dev-omgeving, uitrol-docs | **nu opgeleverd** |
| **2 — Beheer** | Beheerpagina achter **Keycloak**-login (now-playing tagline, status, wachtwoordbeheer) | gepland |

Beslissingen voor fase 1:
- **Luisteren is publiek**, geen login (PRD B3).
- **Beheer komt later** achter Keycloak (toevoeging op de PRD, fase 2).
- **De bron levert aan met het Icecast `source`-wachtwoord** (PRD B5) — geen
  aparte bron-login in fase 1.
- **Geen secrets in git**: de drie wachtwoorden komen uit `.env` en worden bij
  het starten in de Icecast-config gerenderd (envsubst in de entrypoint).

---

## Mappenstructuur

```
radiowaver/
├─ icecast/                 Icecast2-container
│  ├─ Dockerfile            Debian + icecast2 (self-contained, PRD B6)
│  ├─ icecast.xml.template  config-template; ${...} wordt uit .env ingevuld
│  └─ entrypoint.sh         rendert de config en start Icecast
├─ web/
│  └─ index.html            publieke spelerpagina (live-status + luisteraars)
├─ docker-compose.yml       productie: Icecast + web-container (VM `web`-netwerk)
├─ docker-compose.dev.yml   dev: Icecast + lokale Caddy op http://localhost:8080
├─ Caddyfile.web            interne Caddy van de prod web-container (:80)
├─ Caddyfile.snippet        blok voor de gedeelde Caddy op de VM
├─ Caddyfile.dev            lokale dev-Caddy (geen TLS)
├─ .env.example             sjabloon voor de wachtwoorden (kopieer naar .env)
├─ .gitignore
└─ briefing/                oorspronkelijke brief + PRD (radiowaver-prd.md)
```

---

## 1. Dev-omgeving (lokaal)

Vereist: **Docker Desktop** (Windows/Mac) of Docker Engine + compose-plugin.

```bash
# 1. Secrets aanmaken (eenmalig)
cp .env.example .env
#   zet ICECAST_HOSTNAME=localhost voor lokaal testen en kies wachtwoorden

# 2. Icecast + lokale Caddy starten
docker compose -f docker-compose.dev.yml up --build
```

Open **<http://localhost:8080>**. Zonder bron staat de speler op *offline* met
een uitgeschakelde knop. Stoppen: `Ctrl-C`, of `docker compose -f
docker-compose.dev.yml down`.

### Een test-bron pushen (zonder mengpaneel)

De pagina springt pas op *on air* zodra er audio op `/live` staat. Twee opties:

**A. Met ffmpeg** (een toon of een mp3-bestand in een lus):

```bash
# Een 440 Hz testtoon, oneindig, naar de dev-Icecast:
ffmpeg -re -f lavfi -i "sine=frequency=440:sample_rate=44100" \
  -acodec libmp3lame -b:a 128k -content_type audio/mpeg -legacy_icecast 1 \
  "icecast://source:<JOUW_SOURCE_PW>@localhost:8000/live"

# Of een bestaand mp3'tje in een lus:
ffmpeg -re -stream_loop -1 -i muziek.mp3 \
  -acodec libmp3lame -b:a 128k -content_type audio/mpeg -legacy_icecast 1 \
  "icecast://source:<JOUW_SOURCE_PW>@localhost:8000/live"
```

**B. Met BUTT** — zelfde instellingen als hieronder, maar Address `localhost`.

Zodra de bron loopt, toont <http://localhost:8080> *on air* en kun je luisteren.

---

## 2. Uitrol op de VM (productie)

De agent kan de VM niet bereiken — draai dit zelf op de server. Radio Waver past
in het bestaande patroon van de VM: een **gedeelde Caddy in Docker** op het
externe netwerk **`web`** routeert per containernaam. Radio Waver draait als
eigen compose-project `radiowaver-prod` met twee containers:

- `radiowaver-icecast-prod` — Icecast; publiceert poort **8000** (bron-aanlevering).
- `radiowaver-web-prod` — Caddy die de speler serveert en `/live` + `/status`
  intern naar Icecast proxyt; hangt aan `web`, **geen** host-poort.

**Vooraf (jij):** DNS voor `radio.waver.be` → IP van de VM, en het netwerk `web`
bestaat al (van JEKA/daak). Check: `docker network ls | grep web`.

1. **Repo + secrets.**
   ```bash
   git clone https://github.com/svenvercammen/radiowaver.git
   cd radiowaver
   cp .env.example .env        # vul de drie wachtwoorden in, hostname = radio.waver.be
   ```

2. **Starten.**
   ```bash
   docker compose up -d --build
   docker compose ps           # beide Up
   docker compose logs -f web  # check de opstart
   ```

3. **Gedeelde Caddy.** Plak het blok uit `Caddyfile.snippet` bij de bestaande
   reverse-proxy (in JEKA: `infra/reverse-proxy/`) en herlaad de gedeelde Caddy
   (bv. `bash deploy/reverse-proxy-up.sh`, of `docker exec <caddy> caddy reload
   --config /etc/caddy/Caddyfile`). Caddy regelt automatisch TLS.

4. **Firewall.** Open poort **8000** voor de bron, bij voorkeur beperkt tot het
   IP van de event-pc.

5. **Testen.** Surf naar <https://radio.waver.be>. Offline tot er een bron is;
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
| Port | `8000` |
| Password | je `source`-wachtwoord uit `.env` |
| Icecast mountpoint | `/live` |
| Icecast user | `source` |

*Settings → Audio*: kies de geluidskaart / USB-interface (de ingang van het
mengpaneel), codec **MP3**, bitrate **128 kbps**. Stel het volume zo in dat de
master niet clipt. Druk op **Play** om uit te zenden.

> Liever alles over 443/TLS i.p.v. poort 8000 open? Kan, maar voor een eenmalig
> event is rechtstreeks aanleveren op 8000 het meest robuust. Beperk 8000
> desnoods in de firewall tot het IP van de event-pc; de admin-interface
> (`:8000/admin`) is sowieso met wachtwoord beveiligd.

---

## Capaciteit

50 luisteraars × 128 kbps ≈ 6–7 Mbps uitgaand op de piek. Verwaarloosbaar naast
waverfeest.be en daak.be; CPU/RAM van Icecast is minimaal.

## Beveiliging

- Wachtwoorden staan in `.env` (gitignored), niet in de repo.
- De Icecast admin-interface is niet publiek via `radio.waver.be` bereikbaar:
  Caddy proxyt enkel `/live` en `/status-json.xsl`.
- Beperk poort 8000 in de firewall tot het IP van de event-pc waar mogelijk.

## Documentatie

- **PRD:** [briefing/radiowaver-prd.md](briefing/radiowaver-prd.md)
- **Oorspronkelijke brief:** [briefing/README.md](briefing/README.md)
