#!/bin/sh
# Rendert /etc/icecast2/icecast.xml uit de template + omgevingsvariabelen,
# zodat de wachtwoorden via .env binnenkomen en niet in de repo staan.
set -eu

# Verplichte secrets — faal duidelijk als er eentje ontbreekt.
: "${ICECAST_SOURCE_PASSWORD:?ICECAST_SOURCE_PASSWORD ontbreekt (zet hem in .env)}"
: "${ICECAST_RELAY_PASSWORD:?ICECAST_RELAY_PASSWORD ontbreekt (zet hem in .env)}"
: "${ICECAST_ADMIN_PASSWORD:?ICECAST_ADMIN_PASSWORD ontbreekt (zet hem in .env)}"
# Optioneel met default.
: "${ICECAST_HOSTNAME:=radio.waver.be}"
export ICECAST_HOSTNAME

# Alleen onze eigen placeholders vervangen; de rest van de XML blijft intact.
envsubst '${ICECAST_SOURCE_PASSWORD} ${ICECAST_RELAY_PASSWORD} ${ICECAST_ADMIN_PASSWORD} ${ICECAST_HOSTNAME}' \
  < /etc/icecast2/icecast.xml.template \
  > /etc/icecast2/icecast.xml

exec "$@"
