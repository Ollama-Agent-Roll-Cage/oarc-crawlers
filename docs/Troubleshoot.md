# OARC-Crawlers Troubleshooting Guide

This guide provides solutions to common issues you might encounter when installing or using OARC-Crawlers.

## Table of Contents
- [Virtual Environment Issues](#virtual-environment-issues)
- [Installation Problems](#installation-problems)
- [Dependency Conflicts](#dependency-conflicts)
- [Runtime Errors](#runtime-errors)
- [Platform-Specific Issues](#platform-specific-issues)

## Virtual Environment Issues

### Python venv Cleanup and Management

Make sure to clean your python uv venv, as well as your base python environment.

Your environment should be clean and should be similar to the following example:

```bash
# try pip list
pip list

# Heres an example
PS M:\oarc_repos_git\oarc-crawlers> pip list
Package       Version Editable project location
------------- ------- -------------------------------
oarc-crawlers 0.1.2   M:\oarc_repos_git\oarc-crawlers
pip           25.0.1
setuptools    78.1.0
wheel         0.45.1
PS M:\oarc_repos_git\oarc-crawlers> pip install uv
Looking in indexes: https://pypi.org/simple, https://pypi.ngc.nvidia.com
Collecting uv
  Downloading uv-0.6.14-py3-none-win_amd64.whl.metadata (11 kB)
Downloading uv-0.6.14-py3-none-win_amd64.whl (17.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.6/17.6 MB 52.9 MB/s eta 0:00:00
Installing collected packages: uv
Successfully installed uv-0.6.14
PS M:\oarc_repos_git\oarc-crawlers>

# Clear the virtual environment and the base environment

# Make sure to do:
conda deactivate

# Then if you made a venv with "uv venv --python 3.11" you can deactivate it now:

# Now deactivate
.venv\Scripts\deactivate

PS M:\oarc_repos_git\oarc-crawlers> .venv\Scripts\activate
(oarc-crawlers) PS M:\oarc_repos_git\oarc-crawlers> .venv\Scripts\deactivate

# If you cannot deactivate with the deactivate command try killing the terminal, also make sure you are careful when working with multiple uv virtual environments at the same time, they get confused.

# Clear the uv venv made with "uv venv --python 3.11"

# activate
.venv\Scripts\activate

# Run pip list

(oarc-crawlers) PS M:\oarc_repos_git\oarc-crawlers> pip list      
Package       Version Editable project location
------------- ------- -------------------------------
oarc-crawlers 0.1.2   M:\oarc_repos_git\oarc-crawlers # WE WANT TO REMOVE THIS
pip           25.0.1
setuptools    78.1.0
uv            0.6.14
wheel         0.45.1
(oarc-crawlers) PS M:\oarc_repos_git\oarc-crawlers> pip uninstall oarc-crawlers

# Now we remove the old oarc crawlers
pip uninstall oarc-crawlers

# Now run pip list again

(oarc-crawlers) PS M:\oarc_repos_git\oarc-crawlers> pip list
Package    Version
---------- -------
pip        25.0.1
setuptools 78.1.0
wheel      0.45.1
(oarc-crawlers) PS M:\oarc_repos_git\oarc-crawlers> 

# install uv
pip install uv

# now continue with either

uv pip install oarc-crawlers

# or

# activate uv venv
.venv\Scripts\activate

# install developer package
uv pip install -e .[dev]

# Continue with your specific usage after cleaning your uv environment :)
# hope this helps!
```

### Virtual Environment Isolation Issues

If you're encountering issues with package conflicts, it may be because your virtual environment isn't properly isolated from your system Python. Here's how to verify and fix:

```bash
# Check where your Python is running from
which python  # On Unix/MacOS
where python  # On Windows

# The output should point to your virtual environment
# If not, deactivate and reactivate:
.venv\Scripts\deactivate
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Unix/MacOS
```

## Installation Problems

### Package Not Found Errors

If you receive a "Package not found" error when installing oarc-crawlers:

1. Verify your internet connection
2. Check that you're using the latest version of uv and pip:
   ```bash
   pip install --upgrade pip uv
   ```
3. Try installing with pip directly if uv is having issues:
   ```bash
   pip install oarc-crawlers
   ```

### Permission Issues

If you encounter permission errors during installation:

**Windows:**
```bash
# Run as administrator (PowerShell)
Start-Process PowerShell -Verb RunAs
```

**Unix/MacOS:**
```bash
sudo pip install uv
sudo uv pip install oarc-crawlers
```

## Dependency Conflicts

### Common Dependency Issues

If you encounter dependency conflicts:

1. Create a clean virtual environment
2. Install packages in the correct order
3. Use specific versions if needed:
   ```bash
   uv pip install oarc-crawlers==0.1.2
   ```

### Python Version Compatibility

OARC-Crawlers is designed to work with Python 3.11. If you're using a different version, you may encounter compatibility issues:

```bash
# Check your Python version
python --version

# If not 3.11, create a venv with the correct version
uv venv --python 3.11
```

## Runtime Errors

### YouTube Download Issues

If YouTube downloads fail:

1. Check for updates to the package
2. Verify the URL is valid and accessible
3. Check for regional restrictions on the content
4. Look for errors in the YouTube API response

### Web Crawler Connection Problems

If web crawling fails:

1. Check your internet connection
2. Verify the target website is online
3. Some websites may block automated crawling
4. Try adding a user-agent header to appear as a browser:
   ```python
   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
   crawler = BSWebCrawler(data_dir="./data", headers=headers)
   ```

### GitHub API Rate Limiting

GitHub has API rate limits that may affect crawling:

1. Use authenticated requests when possible
2. Implement backoff strategies for retrying requests
3. Cache results to reduce API calls

## Platform-Specific Issues

### Windows

Common issues on Windows:

1. Path length limitations can break deep directory crawls
2. PowerShell execution policy may prevent scripts from running
3. File locking may prevent modifying files that are in use

### MacOS

Common issues on MacOS:

1. SSL certificate validation issues with older Python versions
2. Permission issues with system directories
3. XCode command line tools may be required for some packages

### Linux

Common issues on Linux:

1. Missing development libraries needed for compilation
2. System package conflicts with Python packages
3. Distribution-specific package management conflicts

## Getting Help

If you're still experiencing issues after going through this troubleshooting guide:

1. Check existing issues on our [GitHub repository](https://github.com/oarc/oarc-crawlers/issues)
2. Submit a new issue with detailed steps to reproduce the problem
3. Include error messages and your environment details (OS, Python version, package versions)
