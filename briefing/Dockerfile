FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends icecast2 ca-certificates \
 && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

# Icecast start als root en laat daarna privileges vallen naar de
# icecast2-gebruiker via <changeowner> in icecast.xml.
CMD ["icecast2", "-c", "/etc/icecast2/icecast.xml"]
