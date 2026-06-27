# Radio Waver — always-on stream.
#
#   BUTT (event-pc) ──harbor:8005──┐
#   fallback-bron ─────────────────┴─ fallback ─► Icecast /live ─► luisteraars
#
# De fallback-bron staat in /data/music/source.conf (door de beheer-API beheerd):
#   regel 1: "mp3"  -> speel /data/music/playlist.m3u (eigen MP3's, watch-reload)
#   regel 1: "radio", regel 2: <stream-URL>  -> relay een internetradio (input.http)
#
# Bij wissel van bron schrijft de API een nieuw token in restart.trigger;
# Liquidsoap stopt dan, en de container (restart: unless-stopped) start opnieuw
# en leest de nieuwe source.conf in.

pw = environment.get("ICECAST_SOURCE_PASSWORD")

# Live van de event-pc (BUTT levert hier aan: poort 8005, mount /live, user source).
# Kleinere buffer = lagere live-latency (iets gevoeliger voor jitter op de upload).
live = input.harbor("live", port=8005, password=pw, buffer=1.0, max=4.0)

# Fallback-bron bepalen uit de config.
conf = file.contents("/data/music/source.conf")
clines = string.split(separator="\n", conf)
mode = string.trim(list.nth(default="mp3", clines, 0))
url = string.trim(list.nth(default="", clines, 1))

fallback_src =
  if mode == "radio" and url != "" then
    log("Fallback-bron: internetradio relay #{url}")
    # Browser-User-Agent: veel zenders weigeren de standaard-UA van Liquidsoap/ffmpeg.
    # buffer(): ontkoppelt de klok van de netwerk-input van de hoofd-/output-klok.
    buffer(buffer=2.0, max=10.0,
      input.http(user_agent="Mozilla/5.0 (RadioWaver relay)", url))
  else
    log("Fallback-bron: eigen MP3-playlist")
    playlist(mode="normal", reload_mode="watch", "/data/music/playlist.m3u")
  end

# Live voorrang; bij wegvallen meteen (track_sensitive=false) naar de fallback.
# Altijd iets uitsturen (stilte als zowel live als fallback ontbreken).
radio = mksafe(fallback(track_sensitive=false, [live, fallback_src]))

# Hoofd-stream voor de luisteraars (live of fallback, naadloos).
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

# Signaal-mount: bestaat ALLEEN wanneer er echt live wordt uitgezonden.
# De website checkt of deze mount bestaat om 'live' vs 'fallback' te tonen.
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

# Herstart Liquidsoap zodra de fallback-config wijzigt: de container start opnieuw
# op en leest source.conf opnieuw in (nodig om input.http van URL te wisselen).
def reload_cfg() =
  log("Fallback-config gewijzigd -> Liquidsoap herstart")
  shutdown()
end
ignore(file.watch("/data/music/restart.trigger", reload_cfg))
