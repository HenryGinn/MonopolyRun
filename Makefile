PYTHON := .venv/bin/python
LATEX := lualatex
BIBER := biber

PAPER := Essay/MonopolyRun.pdf

.PHONY: all
all: $(PAPER)

# ----------------------------------------------------------------------
# Virtual environment
# ----------------------------------------------------------------------

.venv/bin/python:
	python3 -m venv .venv

.venv/.installed: .venv/bin/python requirements.txt
	$(PYTHON) -m pip install -r requirements.txt
	touch $@

# ----------------------------------------------------------------------
# Python-generated files
# ----------------------------------------------------------------------

STYLE_OUTPUT := Sources/style.json

SETUP_2025_STAMP := Data/2025/.setup
SETUP_2026_STAMP := Data/2026/.setup

SETUP_OUTPUT_2025 := \
	Data/2025/Places.csv \
	Data/2025/Routes.json

SETUP_OUTPUT_2026 := \
	Data/2026/Places.csv \
	Data/2026/Routes.json

ELEVATION_OUTPUT := Output/Elevation.csv

PLACES_2025_OUTPUT := Output/2025/Places.tex
PLACES_2026_OUTPUT := Output/2026/Places.tex

GROUPS_2025_OUTPUT := Output/2025/Groups.tex
GROUPS_2026_OUTPUT := Output/2026/Groups.tex

GROUP_PROPORTION_2025_OUTPUT := Output/2025/GroupProportion.csv
GROUP_PROPORTION_2026_OUTPUT := Output/2026/GroupProportion.csv

ROUTES_2025_OUTPUT := \
	Output/2025/PlottingPlaces/* \
	Output/2025/PlottingRoutes/*

ROUTES_2026_OUTPUT := \
	Output/2026/PlottingPlaces/* \
	Output/2026/PlottingRoutes/*


$(STYLE_OUTPUT): Scripts/style_maker.py .venv/.installed
	cd Scripts && ../$(PYTHON) style_maker.py

Output/:
	mkdir $@

$(SETUP_2025_STAMP): Scripts/setup.py | .venv/.installed
	cd Scripts && ../$(PYTHON) setup.py "2025"
	touch $@

$(SETUP_2026_STAMP): Scripts/setup.py | .venv/.installed
	cd Scripts && ../$(PYTHON) setup.py "2026"
	touch $@

$(SETUP_OUTPUT_2025): $(SETUP_2025_STAMP)
$(SETUP_OUTPUT_2026): $(SETUP_2026_STAMP)

$(ELEVATION_OUTPUT): Scripts/output_elevation.py | Output/ .venv/.installed
	cd Scripts && ../$(PYTHON) output_elevation.py

$(PLACES_2025_OUTPUT): Scripts/output_places.py $(SETUP_OUTPUT_2025) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_places.py "2025"

$(PLACES_2026_OUTPUT): Scripts/output_places.py $(SETUP_OUTPUT_2026) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_places.py "2026"

$(GROUPS_2025_OUTPUT): Scripts/output_groups.py $(SETUP_OUTPUT_2025) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_groups.py "2025"

$(GROUPS_2026_OUTPUT): Scripts/output_groups.py $(SETUP_OUTPUT_2026) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_groups.py "2026"

$(GROUP_PROPORTION_2025_OUTPUT): Scripts/output_group_proportion.py $(SETUP_OUTPUT) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_group_proportion.py "2025"

$(GROUP_PROPORTION_2026_OUTPUT): Scripts/output_group_proportion.py $(SETUP_OUTPUT) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_group_proportion.py "2026"

$(ROUTES_2025_OUTPUT): Scripts/output_routes.py $(SETUP_OUTPUT) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_routes.py "2025"

$(ROUTES_2026_OUTPUT): Scripts/output_routes.py $(SETUP_OUTPUT) | .venv/.installed
	cd Scripts && ../$(PYTHON) output_routes.py "2026"

# ----------------------------------------------------------------------
# LaTeX
# ----------------------------------------------------------------------

PYTHON_OUTPUTS := \
	$(STYLE_OUTPUT) \
	$(SETUP_OUTPUT_2025) \
	$(SETUP_OUTPUT_2026) \
	$(ELEVATION_OUTPUT) \
	$(PLACES_2025_OUTPUT) \
	$(PLACES_2026_OUTPUT) \
	$(GROUPS_2025_OUTPUT) \
	$(GROUPS_2026_OUTPUT) \
	$(GROUP_PROPORTION_2025_OUTPUT) \
	$(GROUP_PROPORTION_2026_OUTPUT) \
	$(ROUTES_2025_OUTPUT) \
	$(ROUTES_2026_OUTPUT)

$(PAPER): Essay/MonopolyRun.tex $(PYTHON_OUTPUTS)
	cd Essay && latexmk \
		-lualatex \
		-synctex=0 \
		-interaction=nonstopmode \
		-shell-escape \
		MonopolyRun.tex

# ----------------------------------------------------------------------
# Convenience targets
# ----------------------------------------------------------------------

.PHONY: pdf
pdf: $(PAPER)

.PHONY: figures
figures: $(PYTHON_OUTPUTS)

.PHONY: clean
clean:
	cd Essay && latexmk -C MonopolyRun.tex
	rm -f $(PYTHON_OUTPUTS)

.PHONY: distclean
distclean: clean
	rm -rf .venv
	rm -f .venv/.installed
