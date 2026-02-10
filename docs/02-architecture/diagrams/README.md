# Architecture Diagrams

This folder contains the source code for all system architecture diagrams. They are written in **MermaidJS** syntax (`.mmd`), which allows them to be version-controlled and edited as text.

## Diagram Index

### 1. Core Logic
- [State Machine](./source/core_state_machine.mmd): Trade lifecycle transitions
- [Request Lifecycle](./source/full_request_lifecycle.mmd): End-to-end data flow

### 2. Data Models
- [ER Diagram](./source/models_entity_relations.mmd): Entity relationships

### 3. Services & Workflows
- [Bond Trade Flow](./source/service_bond_flow.mmd): Deal capture logic
- [Repo Sequence](./source/service_repo_sequence.mmd): Repo trade logic
- [Settlement Flow](./source/service_settlement_flow.mmd): T+n settlement logic
- [Approval Sequence](./source/router_four_eyes_sequence.mmd): Four-eyes principle check

## How to Use

1. **Viewing**: Open these `.mmd` files in VS Code with the "Mermaid Preview" extension.
2. **Editing**: Edit the text directly. Diagrams update automatically.
3. **Exporting**: Use the Mermaid CLI (`mmdc`) to convert these to PNG/SVG if needed.

   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i ./source/core_state_machine.mmd -o ./output/core_state_machine.png
   ```
