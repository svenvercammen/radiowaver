# Radio Waver — always-on stream.
#
#   BUTT (event-pc) ──harbor:8005──┐
#                                  ├─ fallback ─► Icecast /live ─► luisteraars
#   MP3-playlist (in lus) ─────────┘
#
# Live heeft voorrang; valt die weg, dan speelt automatisch de MP3-lijst in lus.
# De MP3-volgorde komt uit /data/music/playlist.m3u (door de beheer-API beheerd).

pw = environment.get("ICECAST_SOURCE_PASSWORD")

# Live van de event-pc (BUTT levert hier aan: poort 8005, mount /live, user source).
# Kleinere buffer = lagere live-latency (iets gevoeliger voor jitter op de upload).
live = input.harbor("live", port=8005, password=pw, buffer=1.0, max=4.0)

# Muziek-fallback: speelt de lijst in volgorde, in oneindige lus,
# en herlaadt automatisch zodra de playlist wijzigt.
music = playlist(mode="normal", reload_mode="watch", "/data/music/playlist.m3u")

# Live voorrang; bij wegvallen meteen (track_sensitive=false) naar muziek.
# Altijd iets uitsturen (stilte als zowel live als muziek ontbreken).
radio = mksafe(fallback(track_sensitive=false, [live, music]))

# Hoofd-stream voor de luisteraars (live of muziek, naadloos).
output.icecast(
  %mp3(bitrate=128),
  host="icecast",
  port=8000,
  mount="live",
  password=pw,
  name="Radio Waver",
  description="Live vanop het evenement",
  radio
)

# Signaal-mount: bestaat ALLEEN wanneer er echt live wordt uitgezonden
# (fallible: de output verbindt enkel als de harbor-bron actief is).
# De website checkt of deze mount bestaat om 'live' vs 'muziek' te tonen.
output.icecast(
  %mp3(bitrate=64),
  host="icecast",
  port=8000,
  mount="islive",
  password=pw,
  name="Radio Waver (live-signaal)",
  fallible=true,
  live
)
