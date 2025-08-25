from lark import Lark
from grammar import grammar
from ast_analysis import ASTAnalyzer
from trdg_builder import TRDGBuilder
from priority_assignment import generate_priority_text
import pprint


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

actorclass Dealer {
  statevars
      Boolean sent;

  method dealer {
      sent = false;
      self!star;
  } end

  method star {
      agent!ask;
      sent = true;
  } end

  method dior {
      if (sent) {
          sent = false;
      } else {
          sent = true;
      }
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
      dealer!dior;
  } end
}

main {
  customer actor: (Customer) priority 3;
  dealer actor: (Dealer) priority 3;
  agent actor: (Agent) priority 3;
  ticketService actor: (TicketService) priority 3;
}
"""

    try:
        # Step 1 & 2: Parse and analyze
        parser = Lark(grammar, start="model", parser="lalr")
        tree = parser.parse(code)
        
        analyzer = ASTAnalyzer()
        analyzer.visit(tree)
        analysis_result = analyzer.get_summary()
        
        print("\n=== Analysis Result ===")
        pprint.pprint(analysis_result)
        
        # Step 3: Build TRDG
        trdg_builder = TRDGBuilder(analysis_result)
        trdg_builder.build_trdg()
        
        # Step 4: Find and display dependencies
        dependencies = trdg_builder.find_actor_dependencies()
        print("\n=== Actor Dependencies ===")
        for sender1, sender2, target in dependencies:
            print(f"{sender1} و {sender2} نسبت به {target} وابستگی زمانی دارند")
        
        # Step 5: Visualizations
        trdg_builder.visualize_trdg("rebeca_trdg")
        trdg_builder.visualize_dependencies("actor_deps")
        
        # Step 6: Print summary
        print("\n=== TRDG Summary ===")
        summary = trdg_builder.get_trdg_summary()
        pprint.pprint(summary)
        
        # Display intra-rebec dependencies
        print("\n=== Intra-Rebec Dependencies ===")
        for src, dst in trdg_builder.E_I:
            print(f"{src} → {dst}")
            
        # Step 7: Generate priority assignment text
        print("\n=== Priority Assignment Text ===")
        priority_text = generate_priority_text(trdg_builder)
        print(priority_text)
        
        with open("priority_assignment.txt", "w") as f:
            f.write(priority_text)
            
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        