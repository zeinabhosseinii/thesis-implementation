content = """# Thesis Implementation: ERDG-Based Test Generation for Rebeca Models

This repository contains the implementation of **Extended Rebeca Dependency Graph (ERDG)** for dependency-guided test generation of Rebeca actor models.  
The project provides a complete pipeline including grammar specification, abstract syntax tree (AST) analysis, ERDG construction, actor/message dependency detection, and systematic generation of prioritized test cases.

---

## 📂 Project Structure
thesis-implementation/
├── src/
│ ├── grammar.py # Grammar definition of the Rebeca-like language
│ ├── erdg_nodes.py # Core data structures (RebecNode, MessageServerNode, ActivationNode, TestCase)
│ ├── ast_analyzer.py # AST analyzer for extracting actors, state variables, and methods
│ ├── erdg_builder.py # ERDG construction, dependency analysis, and test generation algorithm
│ └── main.py # Entry point; demonstrates parsing, ERDG building, and test generation
├── outputs/
│ ├── images/ # Generated graphs (AST, ERDG, Actor Dependency Graph, HAG)
│ └── generated_test_cases.txt # Prioritized test cases produced by the algorithm
└── README.md

---

## 🚀 Usage
1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/thesis-implementation.git
   cd thesis-implementation
Run the main script:
python -m src.main
Inspect the outputs:
Graphical outputs (in .png format) are stored in the outputs/images/ folder:
AST.png – Abstract Syntax Tree of the input model
ERDG.png – Extended Rebeca Dependency Graph
AG.png – Actor Dependency Graph
HAG.png – Hierarchical Actor Group Graph
The file outputs/generated_test_cases.txt contains all generated prioritized test cases with assigned actor and method priorities.
📬 Contact
For questions, discussions, or collaboration opportunities, feel free to contact:
📧 zeinab.hosseinii78@gmail.com
"""
