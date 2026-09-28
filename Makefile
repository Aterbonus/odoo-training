include .env
export

.PHONY: up down restart odoo-run logs ps shell odoo-shell psql install update reset oca-pull

# addons_path: módulos propios + cada repo externo descargado en
# external-addons/ (ver repos.yaml y `make oca-pull`).
comma := ,
empty :=
space := $(empty) $(empty)
# De momento los repos OCA (19.0) quedan fuera del addons_path, ya que no son
# compatibles con Odoo 20. Para reactivarlos, usar la línea comentada.
# ADDONS_PATH := $(subst $(space),$(comma),/mnt/extra-addons $(patsubst %/,/mnt/%,$(wildcard external-addons/*/)))
ADDONS_PATH := /mnt/extra-addons

up: ## Levanta el contenedor de Odoo (inactivo) + Postgres en segundo plano
	docker compose up -d

down: ## Detiene y elimina los contenedores (conserva los volúmenes/datos)
	docker compose down

restart: ## Reinicia el contenedor de Odoo (útil tras editar docker-compose.yml/Dockerfile)
	docker compose restart odoo

# Uso: make odoo-run [ARGS="-d training -u estate"]
odoo-run: ## Levanta el servicio de Odoo en primer plano (Ctrl+C para detener; volver a correr tras agregar archivos .py nuevos)
	docker compose exec odoo /entrypoint.sh odoo -c /etc/odoo/odoo.conf --addons-path=$(ADDONS_PATH) $(ARGS)

logs: ## Sigue los logs de Odoo
	docker compose logs -f odoo

ps: ## Estado de los contenedores
	docker compose ps

shell: ## Abre una shell bash dentro del contenedor de Odoo
	docker compose exec odoo bash

odoo-shell: ## Abre el shell de Python de Odoo (odoo shell) sobre ODOO_DB
	docker compose exec odoo odoo shell -d $(ODOO_DB) --addons-path=$(ADDONS_PATH),/usr/lib/python3/dist-packages/odoo/addons

psql: ## Conecta con psql a la base de datos ODOO_DB
	docker compose exec db psql -U $(POSTGRES_USER) -d $(ODOO_DB)

# Uso: make install MODULE=nombre_modulo
install: ## Instala un módulo propio en ODOO_DB (y detiene Odoo al terminar)
	docker compose run --rm odoo odoo -d $(ODOO_DB) --addons-path=$(ADDONS_PATH) -i $(MODULE) --stop-after-init

# Uso: make update MODULE=nombre_modulo
update: ## Actualiza un módulo propio en ODOO_DB (y detiene Odoo al terminar)
	docker compose run --rm odoo odoo -d $(ODOO_DB) --addons-path=$(ADDONS_PATH) -u $(MODULE) --stop-after-init

oca-pull: ## Descarga/actualiza los repos externos definidos en repos.yaml (requiere uv)
	uvx --from git-aggregator gitaggregate -c repos.yaml

reset: ## Elimina TODO (contenedores + volúmenes = borra la base de datos y filestore)
	docker compose down -v
