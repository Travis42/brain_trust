# Adding Custom Personas

This guide explains how to add new advisor personas to the Brain Trust CLI application.

## Understanding Personas

Each persona in Brain Trust is an AI advisor with a specific role, perspective, and system prompt. Personas analyze questions independently and provide structured insights that the Summarizer synthesizes into an executive summary.

## Persona Structure

A persona is defined using the [`Persona`](src/personas.py:11) Pydantic model with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `str` | Yes | Unique identifier for the persona (e.g., `"strategist"`, `"risk_officer"`) |
| `display_name` | `str` | Yes | Human-readable name displayed in output (e.g., `"Strategist"`, `"Risk Officer"`) |
| `system_prompt` | `str` | Yes | The system prompt that defines the persona's behavior and focus areas |
| `is_summarizer` | `bool` | No | Set to `True` only for the Summarizer persona (default: `False`) |

## Adding a New Advisor Persona

### Step 1: Define the Persona

Add your new persona to the [`PERSONAS`](src/personas.py:41) dictionary in [`src/personas.py`](src/personas.py):

```python
PERSONAS: Dict[str, Persona] = {
    # ... existing personas ...
    
    "your_persona": Persona(
        name="your_persona",
        display_name="Your Persona Name",
        system_prompt=f"""You are the Your Persona Name advisor. Your role is to [describe the role].

Focus areas:
- [Focus area 1]
- [Focus area 2]
- [Focus area 3]
- [Focus area 4]
- [Focus area 5]

When analyzing:
- [Analysis guideline 1]
- [Analysis guideline 2]
- [Analysis guideline 3]
- [Analysis guideline 4]
- [Analysis guideline 5]{ADVISOR_GUARDRAILS}""",
        is_summarizer=False
    ),
}
```

### Step 2: Include Guardrails

All advisor personas (except the Summarizer) must include the [`ADVISOR_GUARDRAILS`](src/personas.py:28) constant at the end of their system prompt:

```python
ADVISOR_GUARDRAILS = """

IMPORTANT INSTRUCTIONS:
1. You have a private scratchpad for your reasoning. Update it as needed, but do not reveal its contents in your final response.
2. Do not assume or reference what other advisors might say. Work independently without collusion.
3. Structure your response as:
   - Brief answer (2-3 sentences)
   - Key bullet points (3-5 points)
   - Open questions (2-3 questions that need further exploration)
"""
```

These guardrails ensure:
- Each advisor has a private scratchpad for reasoning (visible in verbose mode)
- Advisors work independently without colluding
- Responses follow a consistent structure

### Step 3: Use the New Persona

Once added, you can use your new persona immediately:

```bash
# Use only your new persona
python -m src.cli "Your question here?" --personas your_persona

# Use your persona alongside others
python -m src.cli "Your question here?" -p strategist,your_persona,risk_officer
```

## Complete Example

Here's a complete example of adding a "Financial Analyst" persona:

```python
"financial_analyst": Persona(
    name="financial_analyst",
    display_name="Financial Analyst",
    system_prompt=f"""You are the Financial Analyst advisor. Your role is to provide financial analysis and cost-benefit evaluation.

Focus areas:
- Analyze financial implications and costs
- Evaluate return on investment (ROI) and payback periods
- Identify budget constraints and financial risks
- Consider cash flow implications and funding requirements
- Highlight financial metrics and key performance indicators

When analyzing:
- Use quantitative financial analysis where possible
- Consider both short-term and long-term financial impact
- Identify cost drivers and potential savings
- Evaluate financial feasibility and sustainability
- Highlight assumptions in financial calculations{ADVISOR_GUARDRAILS}""",
    is_summarizer=False
),
```

## Best Practices

### 1. Choose a Clear, Unique Name

- Use lowercase with underscores: `financial_analyst`, `compliance_officer`
- Keep it descriptive but concise
- Ensure it doesn't conflict with existing personas

### 2. Define a Specific Role

Each persona should have a distinct perspective:
- **Strategist**: High-level strategic framing
- **Domain Expert**: Technical depth and domain knowledge
- **Devil's Advocate**: Critical questioning and challenge
- **Risk Officer**: Risk identification and mitigation
- **Ethicist**: Ethical implications and stakeholder impact

Consider what unique perspective your persona brings that isn't already covered.

### 3. Structure the System Prompt

Follow the template used by existing personas:

```
You are the [Display Name] advisor. Your role is to [describe the role].

Focus areas:
- [Focus area 1]
- [Focus area 2]
- [Focus area 3]
- [Focus area 4]
- [Focus area 5]

When analyzing:
- [Analysis guideline 1]
- [Analysis guideline 2]
- [Analysis guideline 3]
- [Analysis guideline 4]
- [Analysis guideline 5]{ADVISOR_GUARDRAILS}
```

### 4. Be Specific About Focus Areas

List 5 focus areas that define what the persona should consider. These guide the AI's attention and ensure comprehensive coverage.

### 5. Provide Clear Analysis Guidelines

Give 5 specific instructions for how the persona should approach analysis. These help the AI understand the expected depth and style.

### 6. Include Guardrails

Always append `{ADVISOR_GUARDRAILS}` to the system prompt for advisor personas. This ensures consistent output structure and independent reasoning.

## Testing Your Persona

After adding a new persona, test it with a relevant question:

```bash
# Test with verbose mode to see the scratchpad
python -m src.cli "Test question relevant to your persona" -p your_persona -v
```

Check that:
- The persona provides a brief answer (2-3 sentences)
- The persona includes 3-5 key bullet points
- The persona lists 2-3 open questions
- The persona uses the private scratchpad for reasoning
- The output aligns with the defined role and focus areas

## Modifying Existing Personas

You can also modify existing personas by editing their entries in the [`PERSONAS`](src/personas.py:41) dictionary. The same principles apply:

- Keep the `name` and `is_summarizer` fields unchanged
- Update `display_name` if you want to change how it appears in output
- Modify `system_prompt` to adjust behavior, focus areas, or analysis guidelines
- Always include `{ADVISOR_GUARDRAILS}` for advisor personas

## Important Notes

- **Do not create multiple summarizers**: Only one persona should have `is_summarizer=True`
- **Maintain independence**: The guardrails ensure advisors work independently—don't design personas that reference each other
- **Keep prompts focused**: Longer prompts don't necessarily produce better results—be concise and specific
- **Test thoroughly**: Try your persona with various questions to ensure it behaves as expected

## Example Use Cases

Here are some ideas for additional personas you might consider:

- **Compliance Officer**: Legal and regulatory considerations
- **User Experience Designer**: UX and usability implications
- **Security Specialist**: Security vulnerabilities and best practices
- **Sustainability Advisor**: Environmental and sustainability impact
- **Change Management Expert**: Organizational change and adoption considerations

Each should follow the same structure and include the advisor guardrails.
