# Handleiding — Radio Waver

Praktische gids voor het uitzenden en beluisteren van **radio.waver.be**.
Voor de technische uitrol op de server, zie [README.md](README.md).

- [Voor luisteraars](#voor-luisteraars)
- [Voor de zender — uitzenden met BUTT](#voor-de-zender--uitzenden-met-butt)
  - [1. Wat is BUTT?](#1-wat-is-butt)
  - [2. Installeren](#2-installeren)
  - [3. De server instellen (eenmalig)](#3-de-server-instellen-eenmalig)
  - [4. Het geluid kiezen](#4-het-geluid-kiezen)
  - [5. Uitzenden](#5-uitzenden)
  - [6. Controleren of het werkt](#6-controleren-of-het-werkt)
  - [7. Problemen oplossen](#7-problemen-oplossen)
- [Snelchecklist op de eventdag](#snelchecklist-op-de-eventdag)

---

## Voor luisteraars

Surf naar **<https://radio.waver.be>**. Geen app of account nodig.

- Staat er een uitzending bezig, dan zie je **on air** (rood) en kun je op de
  afspeelknop drukken.
- Is er nog geen uitzending, dan staat de pagina op **offline** en is de knop
  uitgeschakeld — kom dan later terug.
- De pagina toont ook hoeveel mensen er meeluisteren.

Werkt in elke gewone browser, op desktop en mobiel (ook iPhone/Safari).

---

## Voor de zender — uitzenden met BUTT

### 1. Wat is BUTT?

**BUTT** ("Broadcast Using This Tool") is een klein, gratis programma dat:

1. het geluid van een audio-ingang van je pc opneemt,
2. het ter plekke comprimeert naar MP3, en
3. doorstuurt naar de Icecast-server achter radio.waver.be.

BUTT is dus letterlijk de **zender**: het duwt het geluid van je pc naar de
server, waarna luisteraars het via de website horen.

```
mengpaneel ──► audio-ingang pc ──► BUTT ──► radio.waver.be ──► luisteraars
```

Op het event sluit je het **mengpaneel** aan op de audio-ingang van de pc. Om
gewoon even te **testen** kun je je microfoon of het pc-geluid gebruiken.

### 2. Installeren

1. Ga op de pc die je gaat gebruiken naar **<https://danielnoethen.de/butt/>**.
2. Download de versie voor jouw besturingssysteem (Windows / macOS / Linux).
3. Installeer en open BUTT.

### 3. De server instellen (eenmalig)

Open **Settings** (tandwiel-icoon) → tabblad **Main**. Klik bij *Server* op
**Add** en vul in:

| Veld | Waarde |
|---|---|
| Type | **Icecast** |
| Address | `radio.waver.be` |
| Port | `8000` |
| Password | het **source-wachtwoord** (zie kader hieronder) |
| Icecast mount | `/live` |
| Icecast user | `source` |

Klik op **Add / Save**.

> **Waar vind ik het source-wachtwoord?** Dat is de waarde van
> `ICECAST_SOURCE_PASSWORD` in het bestand `.env` op de server. De beheerder
> heeft die ingesteld bij de uitrol. Vraag het op als je het niet hebt — het
> staat bewust niet in deze repo.

### 4. Het geluid kiezen

Nog steeds in **Settings** → tabblad **Audio**:

- **Audio device** — waar het geluid binnenkomt:
  - *Voor een test:* je **microfoon** (of "Stereo Mix" als je het geluid van de
    pc zelf wil uitzenden).
  - *Op het event:* de **geluidskaart / USB-interface** waar het mengpaneel op
    aangesloten is.
- **Codec:** `MP3`
- **Bitrate:** `128 kbps`

Stel het volume zo in dat de master **niet clipt** (niet in het rood). Sluit
Settings.

### 5. Uitzenden

Druk op de grote **Play / ▶**-knop in BUTT. BUTT verbindt nu met de server en
begint uit te zenden. De tijdsteller begint te lopen.

Stoppen doe je met **Stop / ■**. De website valt dan terug op *offline*.

### 6. Controleren of het werkt

Open in een browser **<https://radio.waver.be>**:

- De badge springt van *offline* naar **on air** (rood).
- De afspeelknop wordt actief — klik erop en je hoort wat er binnenkomt op de
  microfoon / het mengpaneel.
- De **luisteraarsteller** loopt mee.

### 7. Problemen oplossen

| Symptoom in BUTT | Waarschijnlijke oorzaak | Oplossing |
|---|---|---|
| Foutmelding over *authentication* / *password* | Source-wachtwoord klopt niet | Controleer het wachtwoord tegen `ICECAST_SOURCE_PASSWORD` in `.env` |
| Foutmelding over *connection* / *timeout* | Poort 8000 geblokkeerd of fout adres | Check Address = `radio.waver.be`, Port = `8000`; controleer de firewall op de server |
| BUTT zendt uit, maar je hoort niets | Verkeerd audio-device of volume op nul | Kies in *Settings → Audio* het juiste device; check het ingangsvolume |
| Pagina blijft op *offline* terwijl BUTT speelt | Verkeerde mount | Mount moet exact `/live` zijn |
| Geluid hapert | Te krappe upload of te hoge bitrate | Check de internetverbinding op locatie; 128 kbps is het maximum voor dit event |

> **Sneller testen zonder BUTT?** Met `ffmpeg` kun je een testtoon of een
> mp3-bestand naar `/live` sturen. Zie het ffmpeg-voorbeeld in
> [README.md](README.md#een-test-bron-pushen-zonder-mengpaneel) (vervang
> `localhost` door `radio.waver.be` om naar de live server te sturen).

---

## Snelchecklist op de eventdag

1. **Mengpaneel** aan op de audio-ingang van de pc; master-uit op een gezond
   niveau (niet clippen).
2. **BUTT** openen → juiste **Server** geselecteerd (radio.waver.be / 8000 /
   `/live`) en juist **Audio device** (de mengpaneel-ingang).
3. **Play** drukken in BUTT.
4. **<https://radio.waver.be>** openen op je telefoon → controleer dat de status
   **on air** is en dat je geluid hoort.
5. Klaar. Na afloop: **Stop** in BUTT.
