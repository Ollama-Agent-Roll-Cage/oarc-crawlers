# envCreation Cheat Sheet

## create env

```bash
uv venv -p 3.11 oarc-crawlers
.venv\Scripts\activate
```

##  Uninstall all packages from your Python environment

```bash
uv pip freeze > requirements.txt
uv pip uninstall -r requirements.txt -y
```

```bash
uv pip install pip
uv pip install wheel
uv pip install setuptools
uv pip install build twine
```

```bash
# Install in development mode with dev dependencies
uv pip install -e ".[dev]"

# Clean build artifacts (Windows PowerShell)
Remove-Item -Path "dist","build","*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue

# Build package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```