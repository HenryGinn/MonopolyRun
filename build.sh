echo "Build virtual environment."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "Building necessary files for working with Monopoly class."
python Scripts/style_maker.py
python Scripts/build.py

echo "Building files for PDF compilation."
cd Scripts
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

echo "Building PDF"
cd Essay
mkdir Data
lualatex -synctex=0 -interaction=nonstopmode -output-directory=Essay "MonopolyRun".tex
biber -output-directory=Essay "MonopolyRun"
lualatex -synctex=0 -interaction=nonstopmode -output-directory=Essay "MonopolyRun".tex
lualatex -synctex=0 -interaction=nonstopmode -output-directory=Essay "MonopolyRun".tex
cd ..
echo "Done!"
