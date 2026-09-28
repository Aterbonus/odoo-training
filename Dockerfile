ARG ODOO_BASE_VERSION=19.0
FROM odoo:${ODOO_BASE_VERSION}

# La imagen oficial deja el shell del usuario odoo como nologin, lo que
# impide abrir una terminal interactiva (p. ej. VS Code "Attach to Running
# Container"). Se habilita bash sin cambiar de usuario ni otorgar
# privilegios nuevos: sigue siendo el mismo usuario no root de siempre.
USER root
RUN usermod --shell /bin/bash odoo

# Mientras no exista la imagen oficial de Odoo 20, se usa la imagen 19 como
# base y el source de 20 se monta encima del paquete instalado (ver
# docker-compose.yml). Odoo 20 requiere h11, que la imagen 19 no incluye.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-h11 \
    && rm -rf /var/lib/apt/lists/*
USER odoo
