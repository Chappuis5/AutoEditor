# AutoEditor

## Installation
**Required python version:** `>=3.10` Check with `python --version`

1. Clone this repo.
2. Navigate to the project directory: `cd ~/Documents/Git-Projects/AutoEditor`.
3. Create a virtual environment: `python3 -m venv env`.
4. Activate the virtual environment:
   - On Unix: `source env/bin/activate`.
   - On Windows: `.\env\Scripts\activate`.
5. Install the dependencies: `pip install -r requirements.txt`. ***Will only be used when tox gets implemented***
6. Set the OpenAI API key as an environment variable:
   - On Unix: `export OPENAI_API_KEY="votre_clé_openai"`.
   - On Windows: `set OPENAI_API_KEY="votre_clé_openai"`.
   Replace `"votre_clé_openai"` with your own OpenAI API key.
7. Generate the distribution package: `python setup.py sdist`.
8. Install the 'AutoEditor' package: `pip install dist/AutoEditor-0.1.tar.gz`.

## Testing
Not implemented yet.

To run the tests, you can use `tox`. If it's not installed, you can install it with `pip install tox`, and then simply run `tox` in the project's root directory.
