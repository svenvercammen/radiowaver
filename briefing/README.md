# Radio Waver — tijdelijke event-webradio

> **Let op — dit is de oorspronkelijke brief (input).** De werkende
> projectopzet staat in de hoofdmap; zie de [README in de root](../README.md).
> Wijzigingen t.o.v. deze brief: de bestanden zijn herschikt (`icecast/`,
> `web/`), en de wachtwoorden staan niet meer in `icecast.xml` maar komen uit
> `.env` (zie `.env.example`). Een beheerpagina achter Keycloak is voorzien als
> fase 2.

Live audio van het mengpaneel → event-pc → Icecast op de VM → webspelers.
Bewust simpel gehouden: één lichte Icecast-container, een statische
spelerpagina, en je bestaande Caddy ervoor.

```
mengpaneel ──► audio-ingang pc ──► encoder (BUTT) ──┐  via internet
                                                    ▼
luisteraars ◄── Caddy (radio.waver.be) ◄── Icecast2 (Docker, poort 8000)
```

## Bestanden

| Bestand              | Doel                                                        |
|----------------------|-------------------------------------------------------------|
| `Dockerfile`         | Bouwt een Icecast2-container (Debian-pakket)                |
| `docker-compose.yml` | Start de Icecast-service                                    |
| `icecast.xml`        | Icecast-config (mount `/live`, 50 luisteraars, wachtwoorden)|
| `Caddyfile.snippet`  | Reverse proxy + statische speler voor `radio.waver.be`      |
| `web/index.html`     | Publieke spelerpagina                                       |

## Uitrollen op de VM

1. **Wachtwoorden zetten.** Open `icecast.xml` en vervang de drie
   `CHANGE_ME_*`-waarden. Zet dezelfde `source`-waarde straks in de encoder.

2. **Icecast starten.**
   ```bash
   docker compose up -d --build
   docker compose logs -f      # check de opstart
   ```

3. **Spelerpagina plaatsen** waar de Caddyfile naar wijst:
   ```bash
   sudo mkdir -p /srv/radio-waver/web
   sudo cp web/index.html /srv/radio-waver/web/
   ```

4. **Caddy.** Plak `Caddyfile.snippet` in je bestaande Caddyfile en herlaad:
   ```bash
   caddy reload --config /etc/caddy/Caddyfile
   ```
   (of `docker compose exec caddy caddy reload ...` als Caddy in Docker draait —
   pas dan ook de upstream aan, zie de noot in de snippet.)

5. **Testen.** Surf naar `https://radio.waver.be`. Zolang er nog geen bron is
   staat de speler op *offline*; zodra je aanlevert springt hij op *on air*.

## Aanleveren vanaf de event-pc (BUTT)

[BUTT](https://danielnoethen.de/butt/) = Broadcast Using This Tool. Gratis,
GUI, Windows/macOS/Linux. Instellen onder *Settings → Main*:

- **Server type:** Icecast
- **Address:** `radio.waver.be`
- **Port:** `8000`
- **Password:** je `source`-wachtwoord uit `icecast.xml`
- **Icecast mountpoint:** `/live`
- **Icecast user:** `source`

Onder *Settings → Audio*: kies je geluidskaart / USB-interface (de ingang waar
het mengpaneel op zit), codec **MP3**, bitrate **128 kbps**, en stel het
volume zo in dat de master niet clipt. Druk dan op **Play** in BUTT om te gaan
uitzenden.

> Liever alles over 443/TLS i.p.v. poort 8000 open? Kan, maar voor een
> eenmalig event is rechtstreeks aanleveren op 8000 het meest robuust.
> Beperk 8000 desnoods in je firewall tot het IP van de event-pc; de
> admin-interface (`:8000/admin`) is sowieso met wachtwoord beveiligd.

## Capaciteit

50 luisteraars × 128 kbps ≈ 6–7 Mbps uitgaand op de piek. Verwaarloosbaar
naast waverfeest.be en daak.be; CPU/RAM van Icecast is minimaal.

## Na het event

```bash
docker compose down
```
Verwijder de `radio.waver.be`-blok uit de Caddyfile en herlaad.
