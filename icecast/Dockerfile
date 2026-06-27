# Self-contained Icecast2-image op basis van het Debian-pakket.
# Geen extern Icecast-image dat kan verdwijnen (PRD: NF6 / B6).
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# icecast2  = de streamingserver
# gettext-base = levert `envsubst`, waarmee de entrypoint de wachtwoorden
#                uit de omgeving in de config invult (geen secrets in git).
RUN apt-get update \
 && apt-get install -y --no-install-recommends icecast2 ca-certificates gettext-base \
 && rm -rf /var/lib/apt/lists/*

COPY icecast.xml.template /etc/icecast2/icecast.xml.template
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# De entrypoint rendert de config uit env-variabelen en start daarna Icecast.
# Icecast start als root en laat privileges vallen naar de icecast2-gebruiker
# via <changeowner> in de config.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["icecast2", "-c", "/etc/icecast2/icecast.xml"]
