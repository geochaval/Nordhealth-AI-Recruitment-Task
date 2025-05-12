# Nordhealth Discharge Note Generator

Automatically generates veterinary discharge notes from Provet Cloud consultation data using LangChain and OpenAI's GPT-4o-mini model.

## Setup

1. Clone:
   ```bash
   git clone https://github.com/geochaval/nordhealth-discharge-generator.git
   cd nordhealth-discharge-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file in the root directory and configure API key: 

```ini
OPENAI_API_KEY = your_openai_key
```

## Usage

```bash
python generate_discharge_note.py path/to/consultation.json
```

## Files

- `data/`: sample inputs
- `generate_note.py`: LangChain-based script
- `solution/`: generated outputs
- `requirements.txt`: dependencies