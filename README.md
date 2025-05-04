# Project setup

1. Go to the project directory
2. Activate the python environment: `uv venv`
3. Install dependencies from the project file: `uv sync`
4. Provide the `OPENAI_API_KEY` in the `.env`
5. Run the project in development mode: `uv run fastapi dev`

# NOTES:

- The agent is quite lengthly to run, but it produce the output. A lot of optimisation can be done, still, such as manual state and context management to direct the flow and output of the LLM.

- An example of agent output is in example_output.json
