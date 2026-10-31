<!--
  This file is injected into the context every time an Agent session starts.
  handler.js listens for the agent:bootstrap event, reads the whole file, and appends it to messages.

  You can put anything the Agent should know in every session here; there is no format restriction:

  ## Role
  You are xxx, responsible for xxx.

  ## Project Rules
  - Rule 1
  - Rule 2

  ## Workflow
  1. Step one
  2. Step two

  ## State Conventions
  State file path: xxx
  Field schema: xxx

  ## Prohibitions
  - Do not xxx

  Use {{PLACEHOLDER}} for runtime dynamic values.
-->
