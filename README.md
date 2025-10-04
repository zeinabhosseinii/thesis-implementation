# ERDG-Based Scheduling for Timed Rebeca Models
Implementation of the Essential Rebeca Dependency Graph (ERDG) for dependency-guided scheduling order generation in Timed Rebeca actor models.
The tool extracts actor and message-server dependencies from Rebeca models and produces a reduced state space by assigning execution priorities.

## Project Structure

```
thesis-implementation/
├── src/
│   ├── grammar.py          # Rebeca-like language grammar definition
│   ├── erdg_nodes.py       # Core data structures
│   ├── ast_analyzer.py     # AST analyzer
│   ├── erdg_builder.py     # ERDG construction and scheduling generation
│   └── main.py             # Application entry point
├── outputs/
│   ├── images/             # Generated graphs (AST, ERDG, AG, HAG)
│   └── reduced_schedule.txt  # Final reduced scheduling order
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
  
## Notes
- The tool implements the step-by-step algorithm described in the thesis.
- Unlike older approaches that generate multiple scenarios or test cases, this implementation produces a single dependency-aware scheduling order representing the reduced state space.
- The reduced state space can be directly explored in Afra or other model checking tools.


## Contact

**Email:** zeinab.hosseinii78@gmail.com
