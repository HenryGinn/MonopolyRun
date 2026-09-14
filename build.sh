echo "Build virtual environment."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Building necessary files for working with Monopoly class
cd Scripts
python style_maker.py
python build.py

# Building files for PDF compilation
python output_elevation.py
python -c "import output_places; output_places.main(2025)"
python -c "import output_places; output_places.main(2026)"
python -c "import output_groups; output_groups.main(2025)"
python -c "import output_groups; output_groups.main(2026)"
python -c "import output_group_proportion; output_group_proportion.main(2025)"
python -c "import output_group_proportion; output_group_proportion.main(2026)"
python -c "import output_routes; output_routes.main(2025)"
python -c "import output_routes; output_routes.main(2026)"
cd ..

deactivate

# Building PDF
cd Essay
lualatex -synctex=0 -interaction=nonstopmode "MonopolyRun".tex
biber "MonopolyRun"
lualatex -synctex=0 -interaction=nonstopmode "MonopolyRun".tex
lualatex -synctex=0 -interaction=nonstopmode "MonopolyRun".tex
cd ..
echo "Done!"
