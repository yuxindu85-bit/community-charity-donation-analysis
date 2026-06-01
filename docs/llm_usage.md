# Optional GPT and DeepSeek Usage

This project includes an optional LLM review helper in `src/llm_review.py`.
It is not part of the core analysis pipeline, and the project still runs
without any API keys.

The purpose is modest: generate a short operations reflection draft from the
existing summary tables. The LLM does not replace the data cleaning, analysis,
charts, reports, dashboard, or tests.

## Why It Is Optional

- The project should remain a data operations and Python analysis project.
- API keys should never be committed to GitHub.
- LLM output should be reviewed before being used in a report.
- The output is not an official financial report or official event record.

## Offline Mode

Offline mode does not call an external API. It creates a local Markdown draft
using the same event context that would be sent to a model.

```bash
python src/llm_review.py --provider offline
```

The default output path is:

```text
reports/llm_operation_review.md
```

## GPT Mode

Set an OpenAI API key in your shell environment before running the command.

```bash
export OPENAI_API_KEY="your_openai_key_here"
export OPENAI_MODEL="gpt-5-mini"
python src/llm_review.py --provider openai
```

You can also pass a model directly:

```bash
python src/llm_review.py --provider openai --model gpt-5-mini
```

## DeepSeek Mode

DeepSeek provides an OpenAI-compatible API endpoint. Set a DeepSeek key before
running the command.

```bash
export DEEPSEEK_API_KEY="your_deepseek_key_here"
export DEEPSEEK_MODEL="deepseek-v4-flash"
python src/llm_review.py --provider deepseek
```

You can also pass a model directly:

```bash
python src/llm_review.py --provider deepseek --model deepseek-v4-flash
```

## Privacy Notes

The prompt is built from anonymized summary tables. It should not include real
donor names, student names, school names, phone numbers, emails, addresses,
QR codes, payment account details, or private notes.

Before sharing any generated text, review it manually and remove anything that
sounds too official, exaggerated, or unsupported by the data.

## Suggested Use

Use the generated draft as a starting point for reflection, not as a final
report. The strongest version is still a student-written explanation that
connects the data analysis to the charity sale operations work.
