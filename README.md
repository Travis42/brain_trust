# Brain Trust CLI

A multi-agent deliberation system powered by LangGraph and OpenRouter. Brain Trust simulates a panel of expert advisors who analyze your question from different perspectives, providing comprehensive insights through parallel reasoning and executive summarization.

## Features

- **Parallel Advisor Execution**: Multiple AI personas analyze your question simultaneously, each with their own private scratchpad for reasoning
- **Diverse Perspectives**: Six specialized advisor personas provide strategic, technical, critical, risk-focused, and ethical viewpoints
- **Executive Summarization**: A dedicated Summarizer synthesizes insights from all advisors, highlighting convergences, divergences, and actionable next steps
- **Flexible Configuration**: Select specific personas or use all advisors, with options for verbose output and summary control
- **Rich Terminal Output**: Beautifully formatted results using Rich library with color-coded panels

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd brain-trust
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with your OpenRouter API credentials:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and set your API key:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
MODEL=anthropic/claude-3.5-sonnet
TEMPERATURE=0.7
TOP_P=1.0
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | Your OpenRouter API key |
| `OPENROUTER_API_BASE` | No | `https://openrouter.ai/api/v1` | OpenRouter API base URL |
| `MODEL` | No | `anthropic/claude-3.5-sonnet` | Model name to use |
| `TEMPERATURE` | No | `0.7` | Sampling temperature (0.0-2.0) |
| `TOP_P` | No | `1.0` | Nucleus sampling parameter (0.0-1.0) |
| `EXEMPLARS_DIR` | No | `data/exemplars` | Directory containing persona exemplar JSON files |

## Usage

### Basic Usage

Run with all advisors:

```bash
python -m src.cli "Should we adopt a microservices architecture?"
```

### Selecting Specific Personas

Use only specific advisors:

```bash
python -m src.cli "What's the best approach for data migration?" --personas strategist,domain_expert
```

Or use the short form:

```bash
python -m src.cli "How should we prioritize technical debt?" -p strategist,risk_officer
```

### Verbose Mode

Show detailed transcript including private scratchpads:

```bash
python -m src.cli "Should we invest in AI capabilities?" --verbose
```

### Skip Summary

Show only advisor outputs without executive summary:

```bash
python -m src.cli "What's our go-to-market strategy?" --no-summary
```

### Custom Exemplars Directory

Use a custom directory for exemplar files:

```bash
python -m src.cli "What's our go-to-market strategy?" --exemplars-dir /path/to/custom/exemplars
```

Or set the `EXEMPLARS_DIR` environment variable:

```bash
export EXEMPLARS_DIR=/path/to/custom/exemplars
python -m src.cli "What's our go-to-market strategy?"
```

### Combined Options

You can combine multiple options:

```bash
python -m src.cli "Should we open source our project?" -p strategist,ethicist -v
```

## Exemplars System

Brain Trust uses exemplars—real people with proven track records—to ground each advisor's recommendations in established expertise. Each persona is associated with exemplars whose expertise aligns with that advisor's perspective.

### How Exemplars Work

- **Simplified Format**: Exemplars are stored as simple name lists in JSON files under [`data/exemplars/`](data/exemplars/)
- **Knowledge-Based Reasoning**: Rather than pre-defining specific actions for each exemplar, the LLM researches each individual from its knowledge base to find novel, contextually relevant precedents
- **Dynamic Citations**: This approach enables more diverse and tailored recommendations, as the model can cite different actions or decisions depending on the specific question

### Customizing Exemplars

You can customize exemplars for each persona by editing the JSON files in [`data/exemplars/`](data/exemplars/):

```json
{
  "persona": "strategist",
  "exemplars": ["Reid Hoffman", "Andy Walsh", "Brian Chesky"]
}
```

To use a custom exemplars directory, set the `EXEMPLARS_DIR` environment variable or use the `--exemplars-dir` CLI option.

## Available Personas

Brain Trust includes six specialized advisor personas:

| Persona | Role |
|---------|------|
| **Strategist** | Provides high-level strategic analysis, frames problems in strategic terms, considers long-term implications and trade-offs |
| **Domain Expert** | Delivers deep technical and domain-specific knowledge, identifies constraints and best practices |
| **Devil's Advocate** | Challenges assumptions, identifies failure modes, surfaces counter-arguments and blind spots |
| **Risk Officer** | Identifies, assesses, and mitigates risks across technical, operational, financial, and reputational dimensions |
| **Ethicist** | Considers ethical implications, stakeholder impact, fairness, and potential unintended consequences |
| **Summarizer** | Synthesizes insights from all advisors, identifies convergences and divergences, recommends next actions |

## How It Works

1. **Question Input**: You provide a question or topic for deliberation
2. **Parallel Analysis**: Selected advisor personas analyze the question simultaneously, each with their own private scratchpad for reasoning
3. **Independent Reasoning**: Advisors work independently without collusion, following specific guardrails
4. **Structured Responses**: Each advisor provides a brief answer, key bullet points, and open questions
5. **Executive Summary**: The Summarizer synthesizes all advisor responses into an executive summary with:
   - Executive summary (3-5 sentences)
   - Convergences (areas of agreement)
   - Divergences (areas of disagreement)
   - Recommended next actions

## Output Format

The CLI displays results in a structured, color-coded format:

- **Question Panel**: Your original question
- **Executive Summary Panel**: Synthesized insights (unless `--no-summary`)
- **Key Disagreements Panel**: Areas where advisors disagree (if any)
- **Advisor Panels**: Individual outputs from each advisor
- **Verbose Transcript** (optional): Detailed execution trace including private scratchpads

## Adding Custom Personas

You can extend Brain Trust by adding custom personas. See [`PERSONAS.md`](PERSONAS.md) for detailed instructions on creating and configuring new advisor personas.

## Requirements

- Python 3.10+
- OpenRouter API key
- Dependencies listed in [`requirements.txt`](requirements.txt)

## License

[Specify your license here]
