.PHONY: help snapshot download expand clean viewlatest snapshot2 download2 expand2 listchars2 logout2

CHARACTER ?= MiragMaraBatato
LEAGUE ?= Mirage
REALM ?= SONY
ACCOUNT ?= Ladimir_Lepin#9831
POESESSID ?=
POB_TOOLS := pob/PathOfBuilding-2.59.2/tools
POB2_TOOLS := PathOfBuilding-PoE2/tools
BUILD_SNAPSHOTS := build_snapshots
BUILD_SNAPSHOTS2 := build_snapshots_poe2

help:
	@echo "PoE1 targets:"
	@echo "  make snapshot CHARACTER=<name> LEAGUE=<league> REALM=<realm>  - Download and expand a PoE1 character"
	@echo "  make download CHARACTER=<name> REALM=<realm>                 - Download PoE1 character (lua)"
	@echo "  make expand FILE=<file> LEAGUE=<league> REALM=<realm>        - Expand downloaded PoE1 JSON"
	@echo "  make viewlatest                                              - View latest expanded file with less"
	@echo "  make clean                                                   - Clean build_snapshots/"
	@echo "PoE2 targets (OAuth, one-time browser login):"
	@echo "  make listchars2                        - List your PoE2 characters"
	@echo "  make snapshot2 CHARACTER=<name>        - Download + expand a PoE2 character"
	@echo "  make download2 CHARACTER=<name>        - Download PoE2 character (OAuth)"
	@echo "  make expand2 CHARACTER=<name>          - Expand downloaded PoE2 JSON"
	@echo "  make logout2                           - Forget saved PoE2 OAuth token"

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

# ---- PoE2 ----

snapshot2: download2 expand2

listchars2:
	@uv run python poe2_import.py

logout2:
	@uv run python poe2_import.py --logout

download2:
	@echo "Downloading $(CHARACTER) (PoE2, OAuth)..."
	@uv run python poe2_import.py "$(CHARACTER)"

expand2:
	@mkdir -p $(BUILD_SNAPSHOTS2)
	@echo "Expanding $(CHARACTER) (PoE2)..."
	@LATEST_JSON=$$(ls -t $(POB2_TOOLS)/$(CHARACTER)_*.json | head -1) && \
	uv run python build_expander_poe2.py "$$LATEST_JSON" -o $(BUILD_SNAPSHOTS2)/$(CHARACTER)_`date +%Y%m%d%H%M`_expanded.json