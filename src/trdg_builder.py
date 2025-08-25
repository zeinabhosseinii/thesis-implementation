from model_nodes import RebecNode, MessageServerNode, ActivationNode
from typing import Dict, List, Tuple
from graphviz import Digraph


# ======== TRDG Builder ========
class TRDGBuilder:
    def __init__(self, analysis_result: Dict):
        self.analysis = analysis_result
        self.N_R: List[RebecNode] = []
        self.N_M: List[MessageServerNode] = []
        self.N_A: List[ActivationNode] = []
        self.E_RM: List[Tuple[str, str]] = []
        self.E_MA: List[Tuple[str, str]] = []
        self.E_AR: List[Tuple[str, str]] = []
        self.E_AM: List[Tuple[str, str]] = []
        self.E_I: List[Tuple[str, str]] = []
        # Create a mapping from instance names to their details
        self.instance_map = {inst["name"]: inst for inst in analysis_result["main_instances"]}

    def build_trdg(self):
        """Build the complete TRDG graph"""
        print("\n=== Building TRDG ===")
        
        # Step 1: Create rebec instance nodes (N_R)
        self._create_rebec_nodes()
        
        # Step 2: Create message server nodes (N_M)
        self._create_message_server_nodes()
        
        # Step 3: Create activation nodes (N_A) and related edges
        self._create_activation_nodes()
        
        # Step 4: Create intra-rebec dependency edges (E_I)
        self._create_intra_rebec_dependencies()
        
        print(f"TRDG built successfully!")
        print(f"- Rebec nodes: {len(self.N_R)}")
        print(f"- Message server nodes: {len(self.N_M)}")
        print(f"- Activation nodes: {len(self.N_A)}")
        print(f"- Total edges: {len(self.E_RM) + len(self.E_MA) + len(self.E_AR) + len(self.E_AM) + len(self.E_I)}")

    def _create_rebec_nodes(self):
        """Create N_R: rebec instance nodes"""
        for instance in self.analysis["main_instances"]:
            actor_class = instance["class"]
            instance_name = instance["name"]
            
            node = RebecNode(
                name=instance_name,
                actor_class=actor_class,
                arg=str(instance["arg"]) if instance["arg"] else "",
                priority=instance["priority"]
            )
            self.N_R.append(node)
            print(f"Created rebec node: {instance_name} ({actor_class})")

    def _create_message_server_nodes(self):
        """Create N_M: message server nodes and E_RM edges"""
        for instance in self.analysis["main_instances"]:
            instance_name = instance["name"]
            actor_class = instance["class"]
            
            if actor_class not in self.analysis["actors"]:
                print(f"Warning: Actor class {actor_class} not found in analysis")
                continue
                
            actor_info = self.analysis["actors"][actor_class]
            
            for method_name, method_info in actor_info["methods"].items():
                # Create message server node
                ms_node = MessageServerNode(
                    rebec_name=instance_name,
                    method_name=method_name,
                    priority=method_info["priority"]
                )
                self.N_M.append(ms_node)
                self.E_RM.append((instance_name, str(ms_node)))
                print(f"Created message server: {ms_node}")

    def _create_activation_nodes(self):
        """Create N_A: activation nodes and related edges"""
        for instance in self.analysis["main_instances"]:
            instance_name = instance["name"]
            actor_class = instance["class"]
            
            if actor_class not in self.analysis["actors"]:
                continue
                
            actor_info = self.analysis["actors"][actor_class]
            
            for method_name, method_info in actor_info["methods"].items():
                sender_method = f"{instance_name}.{method_name}"

                for target, message in method_info["sends"]:
                    # Resolve target to actual instance name
                    target_rebec = None
                    if target == "self":
                        target_rebec = instance_name
                    else:
                        # First try direct instance name lookup
                        if target in self.instance_map:
                            target_rebec = target
                        else:
                            # Try case-insensitive match for instance names
                            for inst_name in self.instance_map.keys():
                                if inst_name.lower() == target.lower():
                                    target_rebec = inst_name
                                    break
                            
                            # If still not found, try to match by class name
                            if not target_rebec:
                                for inst in self.analysis["main_instances"]:
                                    if inst["class"].lower() == target.lower():
                                        target_rebec = inst["name"]
                                        break
                            
                            if not target_rebec:
                                print(f"Warning: Unknown target actor '{target}' in send statement from {instance_name}.{method_name}")
                                continue

                    # Verify target method exists
                    target_class = None
                    for inst in self.analysis["main_instances"]:
                        if inst["name"] == target_rebec:
                            target_class = inst["class"]
                            break
                    
                    if target_class and target_class in self.analysis["actors"]:
                        target_methods = self.analysis["actors"][target_class]["methods"]
                        if message not in target_methods:
                            print(f"Warning: Method '{message}' not found in target actor '{target_rebec}' (class: {target_class})")
                            continue

                    # Create activation node
                    activation = ActivationNode(
                        sender_rebec=instance_name,
                        sender_method=method_name,
                        target_rebec=target_rebec,
                        message_name=message
                    )
                    self.N_A.append(activation)

                    # Create edges
                    self.E_MA.append((sender_method, str(activation)))
                    self.E_AR.append((str(activation), target_rebec))
                    target_ms = f"{target_rebec}.{message}"
                    self.E_AM.append((str(activation), target_ms))

                    print(f"Created activation: {activation}")

    def _create_intra_rebec_dependencies(self):
        """Create intra-rebec data dependencies (E_I edges)"""
        for instance in self.analysis["main_instances"]:
            instance_name = instance["name"]
            actor_class = instance["class"]
            
            if actor_class not in self.analysis["actors"]:
                continue
                
            actor_info = self.analysis["actors"][actor_class]
            variables = actor_info["statevars"]
            methods = actor_info["methods"]
        
            for var in variables:
                last_writer = None
            
                # Process methods (we could sort by priority if needed)
                for method_name, method_info in methods.items():
                    ms_node = f"{instance_name}.{method_name}"
                
                    # If method writes to variable
                    if var in method_info["writes"]:
                        # اگر متد هم نام با کلاس است (constructor)، از آن صرف نظر کن
                        if method_name.lower() == actor_class.lower():
                            print(f"Skipping E_I edge for constructor method: {method_name} in class {actor_class}")
                            last_writer = ms_node  # Still update last_writer for future dependencies
                            continue
                            
                        if last_writer:  # Write-after-write dependency
                            # بررسی کن که last_writer هم constructor نباشد
                            last_writer_method = last_writer.split('.')[1]
                            if last_writer_method.lower() != actor_class.lower():
                                self.E_I.append((last_writer, ms_node))
                                print(f"Added E_I edge (write-after-write): {last_writer} → {ms_node} for variable {var}")
                        last_writer = ms_node
                
                    # If method reads from variable
                    if var in method_info["reads"] and last_writer:
                        # اگر current method constructor است، edge رسم نکن
                        if method_name.lower() == actor_class.lower():
                            print(f"Skipping E_I edge for constructor method: {method_name} in class {actor_class}")
                            continue
                            
                        # اگر last_writer constructor است، edge رسم نکن
                        last_writer_method = last_writer.split('.')[1]
                        if last_writer_method.lower() == actor_class.lower():
                            print(f"Skipping E_I edge from constructor method: {last_writer_method} in class {actor_class}")
                            continue
                            
                        self.E_I.append((last_writer, ms_node))
                        print(f"Added E_I edge (read-after-write): {last_writer} → {ms_node} for variable {var}")

    def visualize_trdg(self, filename="trdg"):
        dot = Digraph(comment="TRDG", format='png')
        dot.attr(rankdir='TB')  # Top to bottom layout
        dot.attr('graph', fontsize='14')
        
        # Add rebec nodes
        with dot.subgraph(name='cluster_0') as c:
            c.attr(style='filled', color='lightgrey', label='Rebec Instances')
            c.attr('node', shape='box', style='filled', fillcolor='lightblue')
            for rebec in self.N_R:
                c.node(rebec.name, f"{rebec.name}\\n({rebec.actor_class})")
        
        # Add message server nodes
        with dot.subgraph(name='cluster_1') as c:
            c.attr(style='filled', color='lightgreen', label='Message Servers')
            c.attr('node', shape='ellipse', style='filled', fillcolor='lightgreen')
            for ms in self.N_M:
                c.node(str(ms), f"{ms.method_name}")
        
        # Add activation nodes
        with dot.subgraph(name='cluster_2') as c:
            c.attr(style='filled', color='lightyellow', label='Activations')
            c.attr('node', shape='diamond', style='filled', fillcolor='lightyellow')
            for activation in self.N_A:
                c.node(str(activation), f"send\\n{activation.message_name}")
        
        # Add edges with different styles
        for src, dst in self.E_RM:
            dot.edge(src, dst, color='blue', label='owns')
        for src, dst in self.E_MA:
            dot.edge(src, dst, color='green', label='creates')
        for src, dst in self.E_AR:
            dot.edge(src, dst, color='red', label='targets')
        for src, dst in self.E_AM:
            dot.edge(src, dst, color='orange', label='triggers')
        for src, dst in self.E_I:
            dot.edge(src, dst, color='purple', style='dashed', label='data_dep')
        
        try:
            dot.render(filename, cleanup=True)
            print(f"✅ TRDG visualization saved as {filename}.png")
            return f"{filename}.png"
        except Exception as e:
            print(f"⚠️ Could not save visualization: {e}")
            return None

    def get_trdg_summary(self):
        """Return structured summary of TRDG"""
        return {
            "rebec_nodes": [f"{r.name} ({r.actor_class})" for r in self.N_R],
            "message_server_nodes": [str(ms) for ms in self.N_M],
            "activation_nodes": [str(a) for a in self.N_A],
            "edges": {
                "E_RM": self.E_RM,
                "E_MA": self.E_MA,
                "E_AR": self.E_AR,
                "E_AM": self.E_AM,
                "E_I": self.E_I
            }
        }

    def find_actor_dependencies(self):
        print("\n=== Finding Actor Dependencies ===")
        
        # Group activations by target
        target_to_senders = {}
        
        for activation in self.N_A:
            target = activation.target_rebec
            sender = activation.sender_rebec
            
            if target not in target_to_senders:
                target_to_senders[target] = set()
            target_to_senders[target].add(sender)
        
        print(f"Target to senders mapping: {target_to_senders}")
        
        dependencies = []
        for target, senders in target_to_senders.items():
            senders_list = list(senders)
            if len(senders_list) >= 2:
                print(f"Target {target} has multiple senders: {senders_list}")
                for i in range(len(senders_list)):
                    for j in range(i+1, len(senders_list)):
                        sender1 = senders_list[i]
                        sender2 = senders_list[j]
                        
                        # اگر target یکی از senderها باشد، dependency رسم نکن
                        if target == sender1 or target == sender2:
                            print(f"Skipping dependency between {sender1} and {sender2} because target {target} is one of the senders")
                            continue
                        
                        # Check for absence of causal path
                        if not self._has_causal_path_between_senders(sender1, sender2, target):
                            dependencies.append((sender1, sender2, target))
                            print(f"Added dependency: {sender1} <-> {sender2} (target: {target})")
        
        return dependencies

    def _has_causal_path_between_senders(self, sender1, sender2, target):
        """Check if there's a causal path between two senders"""
        # For now, simplified logic - could be enhanced with proper path analysis
        return False

    def visualize_dependencies(self, filename="actor_dependencies"):
        """Visualize actor dependencies"""
        dot = Digraph(comment="Actor Dependencies", format='png')
        dot.attr(rankdir='LR')
        
        # Add all rebec nodes
        dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
        for rebec in self.N_R:
            dot.node(rebec.name, f"{rebec.name}\\n({rebec.actor_class})")
        
        # Find and draw dependencies
        dependencies = self.find_actor_dependencies()
        
        # Draw dependency edges between senders
        for sender1, sender2, target in dependencies:
            dot.edge(sender1, sender2,
                    color='red',
                    style='dashed',
                    dir='both',
                    label=f"dependency\\n(target: {target})")
        
        try:
            dot.render(filename, cleanup=True)
            print(f"✅ Actor dependencies visualization saved as {filename}.png")
        except Exception as e:
            print(f"⚠️ Could not save dependencies visualization: {e}")
