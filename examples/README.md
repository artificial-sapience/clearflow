# ClearFlow Examples

Learn ClearFlow through working examples.

## Examples

### [Chat](./chat/)
A conversational AI with OpenAI - demonstrates predictable routing and state management for LLM-powered conversations.

```bash
cd chat
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python main.py
```

### [Structured Output](./structured_output/)
Extract structured data from unstructured text - showcases type-safe Pydantic integration and validation flows.

```bash
cd structured_output
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python main.py
```

## Requirements

- Python 3.13+
- ClearFlow: `pip install clearflow`