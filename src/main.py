from lark import Lark
import pprint

from src.grammar import grammar
from src.erdg_nodes import RebecNode
from src.ast_analyzer import ASTAnalyzer
from src.erdg_builder import ERDGTestGenerator

# ======== Example Usage ========
if __name__ == "__main__":
    code = """
actorclass Customer {
 statevars
     Boolean sent;

 method customer {
     sent = false;
     self!start;
 } end

 method start {
     agent!ask;
     sent = true;
 } end

 method done {
     sent = false;
 } end
}


actorclass Agent {
 statevars
     Boolean dummy;

 method agent {
 } end

 method ask {
     ticketService!process;
 } end
}

actorclass TicketService {
 statevars
     Boolean dummy;

 method ticketService {
 } end

 method process {
     customer!done;
 } end
}

main {
   c1 actor: (Customer);
   c2  actor: (Customer);
   agent    actor: (Agent);
   ticketService actor: (TicketService);

}
"""
    try:
        # Step 1 & 2: Parse and analyze
        parser = Lark(grammar, start="model", parser="lalr")
        tree = parser.parse(code)

        analyzer = ASTAnalyzer()
        analyzer.visit(tree)
        analysis_result = analyzer.get_summary()
        analyzer.draw_ast_graph("AST")


        print("\n=== Analysis Result ===")
        pprint.pprint(analysis_result)

        # Step 3: Build ERDG and Generate Test Cases
        test_generator = ERDGTestGenerator(analysis_result)
        test_cases = test_generator.generate_dependency_guided_tests()
        test_generator.draw_erdg("ERDG")

        # Print results
        test_generator.print_test_cases()

        # Save results to file inside outputs/
        with open("outputs/generated_scenario_cases.txt", "w") as f:
            f.write(f"Generated {len(test_cases)} test cases\n\n")
            for test_case in test_cases:
                f.write(f"Test Case {test_case.id}:\n")
                f.write(f"  Actor Priorities: {test_case.actor_priorities}\n")
                f.write(f"  Method Priorities: {test_case.method_priorities}\n\n")

        print(f"\n✅ Results saved to generated_test_cases.txt")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

