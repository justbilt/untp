rm -rf dist
mkdir -p dist
python setup.py bdist_wheel
twine upload dist/*