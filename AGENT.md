# Project Specific Agent Instructions

## Traceability and Documentation

- **USERINPUT.md**: For every session, the agent MUST maintain a `USERINPUT.md` file at the project root. This file should contain a verbatim or "close to verbose" copy of the user's instructions for that session, followed by the agent's interpretation of each command.
- **Commit Signatures**: Every commit made by an agent MUST include a signature in the commit message. The signature must include:
    - **Model**: The model name used.
    - **Harness**: The version of the harness/CLI.
    - **Tokens**: Approximate cumulative token usage for the session.
    - **Reference**: A reference to the corresponding entries in `USERINPUT.md`.

Example Signature:
```text
Model: gemini-3-flash-preview
Harness: Gemini CLI 0.35.3
Tokens: approx. 50,000
Reference: Instruction 3 in USERINPUT.md
```
