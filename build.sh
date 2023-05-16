rm -r env/
rm -r build/
rm -r dist/
rm *.spec
python -m venv env
pip install -r requirements.txt
source env/bin/activate
python -m PyInstaller --onefile --noconsole --windowed wiregui.py
cp installer.sh dist/
rm *.tar
tar -cvf wiregui.tar dist/*
rm -r dist/
rm -r build/
rm *.spec
