# AutoEditor

## Installation
**Required python version:** `>=3.10`. Check with `python --version`.

1. Clone this repo.
2. Navigate to the project directory: `cd ~/Documents/Git-Projects/AutoEditor`.
3. Create a virtual environment: `python3 -m venv env`.
4. Activate the virtual environment:
   - On Unix or MacOS: `source env/bin/activate`.
   - On Windows: `.\env\Scripts\activate`.
5. Install the dependencies: `pip install -r requirements.txt`. ***Downloading dependecies and microlibrary Editor***
6. Create a `config.json` file at the root of your project and provide your OpenAI, Pexels and Pixabay API keys. Here is a sample structure of `config.json`:
```json
{
"OPENAI_API_KEY": "your_openai_api_key",
"PEXELS_API_KEY": "your_pexels_api_key",
"PIXABAY_API_KEY": "your_pixabay_api_key"
}
```

Replace `"your_openai_api_key"`, `"your_pexels_api_key"` and `"your_pixabay_api_key"` with your actual API keys. Make sure to secure the `config.json` file to avoid any unauthorized use of your API keys and do not commit this file to a public repository.