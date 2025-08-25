from lark import Visitor, Tree
from typing import Dict


# ======== AST Analyzer ========
class ASTAnalyzer(Visitor):
    def __init__(self):
        self.actors = {}  # actor_name -> {statevars, methods}
        self.main_actors = []
        self.current_actor = None
        self.current_method = None

    def class_def(self, tree):
        actor_name = tree.children[0].value
        print(f"Processing class: {actor_name}")
        self.current_actor = actor_name
        self.actors[actor_name] = {
            "statevars": set(),
            "methods": {}
        }
        
        # Manually process children to maintain context
        for child in tree.children[1:]:  # Skip the class name
            if isinstance(child, Tree):
                if child.data == "vars":
                    self.visit_vars(child)
                elif child.data == "method":
                    self.visit_method(child)
        
        self.current_actor = None
        
    def visit_vars(self, tree):
        print(f"Processing vars for actor: {self.current_actor}")
        for child in tree.children:
            if isinstance(child, Tree) and child.data == "var_decl":
                self.visit_var_decl(child)
    
    def visit_var_decl(self, tree):
        if self.current_actor is None:
            print(f"Error: var_decl called without current_actor set")
            return
            
        var_name = tree.children[1].value
        print(f"Adding statevar {var_name} to {self.current_actor}")
        self.actors[self.current_actor]["statevars"].add(var_name)

    def visit_method(self, tree):
        if self.current_actor is None:
            print(f"Error: method called without current_actor set")
            return
            
        method_name = None
        method_priority = None

        # Find method name and priority
        for child in tree.children:
            if hasattr(child, 'type') and child.type == 'NAME':
                method_name = child.value
                break
                
        for child in tree.children:
            if isinstance(child, Tree) and child.data == "priority_block":
                method_priority = int(child.children[0].value)
                break

        print(f"Processing method {method_name} for actor {self.current_actor}")
        self.current_method = method_name
        self.actors[self.current_actor]["methods"][method_name] = {
            "priority": method_priority,
            "sends": [],
            "reads": set(),
            "writes": set()
        }

        # Process method body - visit all statements
        for child in tree.children:
            if isinstance(child, Tree):
                self.visit(child)

        self.current_method = None

    def assign_stmt(self, tree):
        if self.current_actor is None or self.current_method is None:
            return
            
        var_name = tree.children[0].value
        print(f"Method {self.current_method} writes to {var_name}")
        self.actors[self.current_actor]["methods"][self.current_method]["writes"].add(var_name)
        
        # Visit RHS expression to find reads
        if len(tree.children) > 1:
            self.visit_expr(tree.children[1])

    def visit_expr(self, tree):
        if self.current_actor is None or self.current_method is None:
            return
            
        # Handle different expression types
        if isinstance(tree, Tree):
            if tree.data in ["add", "sub", "mul", "div"]:
                # Visit both operands
                for child in tree.children:
                    self.visit_expr(child)
            # For terminals, check if it's a variable reference
        elif hasattr(tree, 'type') and tree.type == 'CNAME':
            # Only add to reads if it's actually a state variable
            if tree.value in self.actors[self.current_actor]["statevars"]:
                print(f"Method {self.current_method} reads from {tree.value}")
                self.actors[self.current_actor]["methods"][self.current_method]["reads"].add(tree.value)

    def send_stmt(self, tree):
        if self.current_actor is None or self.current_method is None:
            return
        
        target = tree.children[0].value
        message = tree.children[1].value
        print(f"Method {self.current_method} sends {message} to {target}")
        self.actors[self.current_actor]["methods"][self.current_method]["sends"].append((target, message))

    def main_block(self, tree):
        print("Processing main block")
        for child in tree.children:
            if isinstance(child, Tree) and child.data == "actor_instance":
                self.visit_actor_instance(child)
                
    def visit_actor_instance(self, tree):
        try:
            instance_name = tree.children[0].value  # First CNAME (instance name)
            actor_class = tree.children[1].value    # Second CNAME (class name in parentheses)
            priority = None

            # Search for priority_block
            for child in tree.children:
                if isinstance(child, Tree) and child.data == "priority_block":
                    priority = int(child.children[0].value)
                    break

            print(f"Found actor instance: {instance_name} of class {actor_class}, priority {priority}")
            self.main_actors.append({
                "name": instance_name,
                "class": actor_class,
                "arg": actor_class,  # Using class name as arg for now
                "priority": priority
            })
        except Exception as e:
            print(f"❌ Failed to parse actor_instance: {tree}")
            print(tree.pretty())
            raise

    
    def get_summary(self):
        return {
            "actors": self.actors,
            "main_instances": self.main_actors
        }