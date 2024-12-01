# Echo Chamber Simulation

This project simulates an echo chamber on social media using AI agents with different personas. The simulation involves agents interacting with a given social media post, providing insights into public reception and message refinement.

## Personas

The personas are defined in the `config.json` file. Each persona represents a unique viewpoint and character:

- **Jordan Blake** (*The Skeptic*): Skeptical of mainstream vaccine narratives, distrusts large institutions, and seeks transparency. Expresses doubts thoughtfully using stories or data to support concerns. Avoids hostile language, focusing on critical thinking and personal choice.

- **Dr. Alex Morgan** (*The Medical Professional*): A medical expert with 15 years in public health. Advocates for vaccines using evidence and empathy. Addresses concerns professionally, emphasizing public health benefits and informed decision-making.

- **Sophie Lee** (*The Supportive Friend*): A supportive friend who values community health. Encourages others to get vaccinated with positive language and personal anecdotes. Shares personal vaccination experiences and expresses hope for a safer future.

- **Blake Anderson** (*The Conspiracy Theorist*): Distrustful of institutions and vaccine motives. References alternative theories and unverified claims. Resists contradictory information, viewing it as part of a cover-up.

- **Emily Carter** (*The Concerned Parent*): A cautious parent seeking reassurance from trusted sources about vaccine safety and necessity. Prefers empathetic explanations over scientific data.

## Running the Command Line Simulation

To run the echo chamber simulation using `echo_chamber.py`:

1. **Install Dependencies**:

   Ensure all required packages are installed: `uagents langchain-openai langchain-core langchain flask`

2. **Set Environment Variables**:

   Export the necessary API keys and secrets:
```bash
export AGENT_MAILBOX_KEY=<your_agent_mailbox_key>
export AGENT_SECRET=<your_agent_secret>
export GROQ_API_KEY=<your_groq_api_key>
export TOGETHER_API_KEY=<your_together_api_key>
```

3. **Run the Script**:

Execute the script with optional arguments:

```bash
python echo_chamber.py [topic] [web_address] [provider] [max_iterations]
```

**Arguments**:

- `topic` (optional): The social media post topic. If not provided, the default from `config.json` is used.
- `web_address` (optional): Address of the Flask server to send messages to (e.g., `localhost:5000`).
- `provider` (optional): Index to select the LLM provider (default is 3).
- `max_iterations` (optional): Maximum number of simulation iterations (default is 5).

Example:
`python echo_chamber.py "Latest vaccine rollout announced!" "localhost:5000" 3 5`

## Running the Web Service

`python app.py`
