# ERDG-Based Scenario Generation for Timed Rebeca Models

Implementation of Essentional Rebeca Dependency Graph (ERDG) for dependency-guided Scenario generation of Timed Rebeca actor models.

## Project Structure

```
thesis-implementation/
├── src/
│   ├── grammar.py          # Rebeca-like language grammar definition
│   ├── erdg_nodes.py       # Core data structures
│   ├── ast_analyzer.py     # AST analyzer
│   ├── erdg_builder.py     # ERDG construction and scenario generation
│   └── main.py             # Application entry point
├── outputs/
│   ├── images/             # Generated graphs
│   └── generated_scenario_cases.txt  # Prioritized test cases
└── README.md
```

## Usage

1. **Clone and run:**
   ```bash
   git clone https://github.com/zeinabhosseinii/thesis-implementation.git
   cd thesis-implementation
   python -m src.main
   ```

2. **View outputs:**
   - Graphs: `outputs/images/` (AST.png, ERDG.png, AG.png, HAG.png)
   - Test cases: `outputs/generated_scenario_cases.txt`

## Contact

**Email:** zeinab.hosseinii78@gmail.com
