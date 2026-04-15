.PHONY: help snapshot download expand clean viewlatest

CHARACTER ?= MiragMaraBatato
LEAGUE ?= Mirage
REALM ?= sony
POB_TOOLS := pob/PathOfBuilding-2.59.2/tools
BUILD_SNAPSHOTS := build_snapshots

help:
	@echo "Available targets:"
	@echo "  make snapshot CHARACTER=<name> LEAGUE=<league> REALM=<realm>  - Download and expand a character"
	@echo "  make download CHARACTER=<name> REALM=<realm>                             - Download character from PoE (lua)"
	@echo "  make expand FILE=<file> LEAGUE=<league> REALM=<realm>                   - Expand downloaded JSON"
	@echo "  make viewlatest                                                 - View latest expanded file with less"
	@echo "  make clean                                                      - Clean build_snapshots/"

snapshot: download expand

download:
	@echo "Downloading $(CHARACTER) from $(REALM)..."
	@cd $(POB_TOOLS) && lua import_character_cli.lua $(REALM) Ladimir_Lepin#9831 $(CHARACTER)

expand:
	@mkdir -p $(BUILD_SNAPSHOTS)
	@echo "Expanding $(CHARACTER)..."
	@LATEST_JSON=$$(ls -t $(POB_TOOLS)/$(CHARACTER)_*.json | head -1) && \
	uv run python build_expander.py "$$LATEST_JSON" --league $(LEAGUE) --realm $(REALM) -o $(BUILD_SNAPSHOTS)/$(CHARACTER)_`date +%Y%m%d%H%M`_expanded.json

clean:
	@rm -rf $(BUILD_SNAPSHOTS)
	@mkdir -p $(BUILD_SNAPSHOTS)

viewlatest:
	@LATEST=$$(ls -t $(BUILD_SNAPSHOTS)/*_expanded.json 2>/dev/null | head -1) && \
	if [ -n "$$LATEST" ]; then less "$$LATEST"; else echo "No expanded files in $(BUILD_SNAPSHOTS)/"; fi