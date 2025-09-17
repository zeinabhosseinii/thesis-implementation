from collections import defaultdict, deque
from itertools import permutations
from graphviz import Digraph, Graph
from typing import List, Tuple, Dict, Optional

from src.erdg_nodes import RebecNode, MessageServerNode, ActivationNode, TestCase


# ======== ERDG Builder with Algorithm Implementation ========
class ERDGTestGenerator:
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

        # Algorithm-specific data structures
        self.AG = None  # Actor Dependency Graph
        self.HAG = None  # Hierarchical Actor Group graph
        self.actor_groups = []
        self.test_cases: List[TestCase] = []

        # Create a mapping from instance names to their details
        self.instance_map = {inst["name"]: inst for inst in analysis_result["main_instances"]}

    def build_erdg(self):
        """Build the complete ERDG graph"""
        print("\n=== Building ERDG ===")

        # Step 1: Create rebec instance nodes (N_R)
        self._create_rebec_nodes()

        # Step 2: Create message server nodes (N_M)
        self._create_message_server_nodes()

        # Step 3: Create activation nodes (N_A) and related edges
        self._create_activation_nodes()

        # Step 4: Create intra-rebec dependency edges (E_I)
        self._create_intra_rebec_dependencies()

        print(f"ERDG built successfully!")
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
    def has_self_send_in_constructor(self, actor_class: str) -> bool:
        """Check if the constructor method of actor_class sends message to self"""
        if actor_class not in self.analysis["actors"]:
            return False

        methods = self.analysis["actors"][actor_class]["methods"]
        if actor_class.lower() not in [m.lower() for m in methods.keys()]:
            return False

        constructor_name = actor_class.lower()
        constructor_info = None
        for m_name, m_info in methods.items():
            if m_name.lower() == constructor_name:
                constructor_info = m_info
                break

        if not constructor_info:
            return False

    # check sends
        for (target, msg) in constructor_info["sends"]:
            if target.lower() == "self":
                return True
        return False

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

    # ======== Algorithm Implementation ========

    def are_actor_dependent(self, r1: str, r2: str) -> bool:
        """Check if two rebec actors are actor dependent (Definition from algorithm)"""
        # Find all activations where r1 and r2 send to the same target
        r1_targets = set()
        r2_targets = set()

        for activation in self.N_A:
            if activation.sender_rebec == r1:
                r1_targets.add(activation.target_rebec)
            elif activation.sender_rebec == r2:
                r2_targets.add(activation.target_rebec)

        # Check for common targets
        common_targets = r1_targets.intersection(r2_targets)

        for target in common_targets:
            # Check if there's no causal path between the two senders
            if not self._has_causal_path_between_actors(r1, r2, target):
                return True

        return False

    def _has_causal_path_between_actors(self, r1: str, r2: str, target: str) -> bool:
        """Check if there's a causal path between r1 and r2 through target"""
        # Simplified: assume no causal path for now
        # This could be enhanced with proper causality analysis
        return False

    def messages_may_interfere(self, group_i: List[str], group_j: List[str]) -> bool:
        """Check if messages from group_i may interfere with group_j via send message"""
        for sender in group_i:
            for activation in self.N_A:
                if activation.sender_rebec == sender and activation.target_rebec in group_j:
                    return True
        return False
    def draw_erdg(self, filename="ERDG"):
        dot = Digraph(comment="ERDG", format="png")
        dot.attr(rankdir="TB")

        # Rebec nodes
        for r in self.N_R:
            dot.node(r.name, shape="box", style="filled", color="lightblue")

        # Message server nodes
        for m in self.N_M:
            dot.node(str(m), shape="ellipse", style="filled", color="lightgreen")

        # Activation nodes
        for a in self.N_A:
            dot.node(str(a), shape="diamond", style="filled", color="orange")

        # Draw edges
        for (src, dst) in self.E_RM:
            dot.edge(src, dst, color="gray")
        for (src, dst) in self.E_MA:
            dot.edge(src, dst, color="green")
        for (src, dst) in self.E_AR:
            dot.edge(src, dst, color="red")
        for (src, dst) in self.E_AM:
            dot.edge(src, dst, color="orange")
        for (src, dst) in self.E_I:
            dot.edge(src, dst, color="purple", style="dashed")

        dot.render(f"outputs/images/{filename}", view=False)
        print(f"✅ ERDG graph saved as {filename}.png")


    def step1_build_actor_dependency_graph(self):
        """Step 1: Build Actor Dependency Graph"""
        print("\n=== Step 1: Building Actor Dependency Graph ===")

        # Initialize undirected graph AG = (N_R, E_D)
        self.AG = {"nodes": [r.name for r in self.N_R], "edges": []}

        # Check all pairs of rebecs
        rebec_names = [r.name for r in self.N_R]
        for i, r1 in enumerate(rebec_names):
            for j, r2 in enumerate(rebec_names):
                if i < j:  # Avoid duplicate pairs and self-loops
                    if self.are_actor_dependent(r1, r2):
                        self.AG["edges"].append((r1, r2))
                        print(f"Added actor dependency edge: {r1} <-> {r2}")

        print(f"Actor Dependency Graph: {len(self.AG['edges'])} edges")

        # 👉 Draw the graph here
        self.draw_actor_dependency_graph("AG")

    def draw_actor_dependency_graph(self, filename="AG"):
        dot = Graph(comment="Actor Dependency Graph", format="png")
        dot.attr(rankdir="LR")

        # Add nodes
        for node in self.AG["nodes"]:
            dot.node(node, shape="ellipse", style="filled", color="lightblue")

        # Add undirected edges
        for r1, r2 in self.AG["edges"]:
            dot.edge(r1, r2)

        dot.render(f"outputs/images/{filename}", view=False)
        print(f"✅ Actor Dependency Graph saved as {filename}.png")
        
    def step2_identify_actor_groups_and_build_hag(self):
        """Step 2: Identify Actor Groups and Build Group-Level Dependency Graph (HAG)"""
        print("\n=== Step 2: Identifying Actor Groups and Building HAG ===")

        # Find connected components using DFS
        self.actor_groups = self._find_connected_components(self.AG)

        print(f"Found {len(self.actor_groups)} actor groups:")
        for i, group in enumerate(self.actor_groups):
            print(f"  Group {i+1}: {group}")

        # Initialize directed graph HAG = (G, E_H)
        self.HAG = {"groups": self.actor_groups, "edges": []}

        # Check interference between groups
        for i, group_i in enumerate(self.actor_groups):
            for j, group_j in enumerate(self.actor_groups):
                if i != j and self.messages_may_interfere(group_i, group_j):
                    self.HAG["edges"].append((i, j))
                    print(f"Added HAG edge: Group {i+1} -> Group {j+1}")

        # 🔥 Resolve cycles (bidirectional edges)
        for (src, dst) in self.HAG["edges"]:
            if (dst, src) in self.HAG["edges"]:
                g1 = self.actor_groups[src]
                g2 = self.actor_groups[dst]

                # بررسی شرط constructor
                g1_has_self = any(self.has_self_send_in_constructor(self.instance_map[a]["class"]) for a in g1)
                g2_has_self = any(self.has_self_send_in_constructor(self.instance_map[a]["class"]) for a in g2)

                if g1_has_self and not g2_has_self:
                    self.topological_order = [src, dst]
                elif g2_has_self and not g1_has_self:
                    self.topological_order = [dst, src]
                else:
                    # پیش‌فرض (اگر هر دو یا هیچ‌کدوم نداشتن)
                    self.topological_order = [src, dst]

                print(f"⚠️ Cycle detected between groups {src+1} and {dst+1}, "
                      f"resolved order: {[i+1 for i in self.topological_order]}")
                self.draw_hag("HAG")
                return  

        # Apply topological sort on HAG (only if no cycle)
        self.topological_order = self._topological_sort(self.HAG)
        print(f"Topological order of groups: {[i+1 for i in self.topological_order]}")

        # 👉 Draw HAG
        self.draw_hag("HAG")

    def _find_connected_components(self, graph):
        """Find connected components in undirected graph using DFS"""
        visited = set()
        components = []

        def dfs(node, component):
            visited.add(node)
            component.append(node)
            # Find neighbors
            for edge in graph["edges"]:
                if edge[0] == node and edge[1] not in visited:
                    dfs(edge[1], component)
                elif edge[1] == node and edge[0] not in visited:
                    dfs(edge[0], component)

        for node in graph["nodes"]:
            if node not in visited:
                component = []
                dfs(node, component)
                components.append(component)

        return components

    def _topological_sort(self, hag):
        """Topological sort using Kahn's algorithm"""
        in_degree = [0] * len(hag["groups"])

        # Calculate in-degrees
        for src, dst in hag["edges"]:
            in_degree[dst] += 1

        # Initialize queue with nodes having 0 in-degree
        queue = deque([i for i in range(len(hag["groups"])) if in_degree[i] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Reduce in-degree of neighbors
            for src, dst in hag["edges"]:
                if src == node:
                    in_degree[dst] -= 1
                    if in_degree[dst] == 0:
                        queue.append(dst)

        return result

    def draw_hag(self, filename="HAG"):
        dot = Digraph(comment="Hierarchical Actor Group Graph", format="png")
        dot.attr(rankdir="TB")

        # Add group nodes
        for i, group in enumerate(self.actor_groups):
            label = f"Group {i+1}\\n" + ", ".join(group)
            dot.node(f"G{i}", label=label, shape="box", style="filled", color="lightgreen")

        # Add directed edges
        for src, dst in self.HAG["edges"]:
            dot.edge(f"G{src}", f"G{dst}")

        dot.render(f"outputs/images/{filename}", view=False)
        print(f"✅ HAG saved as {filename}.png")

    def step3_assign_priorities_to_actors(self):
        """Step 3: Assign Priorities to Actors Based on Group Ordering"""
        print("\n=== Step 3: Assigning Priorities to Actors ===")

        self.actor_priority_assignments = [ {} ]  # شروع با یه دیکشنری خالی
        priority = 1

        for group_idx in self.topological_order:
            group = self.actor_groups[group_idx]
            print(f"Processing group {group_idx+1}: {group}")

            if len(group) == 1:
                # فقط یه actor → اولویت ثابت
                actor = group[0]
                for assignment in self.actor_priority_assignments:
                    assignment[actor] = priority
                print(f"  Fixed assignment for {actor} -> Priority {priority}")
                priority += 1
                continue

            # چند actor → همه permutation ها
            new_assignments = []
            for perm in permutations(group):
                for assignment in self.actor_priority_assignments:
                    new_assignment = assignment.copy()
                    current_priority = priority
                    for actor in perm:
                        new_assignment[actor] = current_priority
                        current_priority += 1
                    new_assignments.append(new_assignment)
                    print(f"  Permutation: {perm} -> Priorities: {new_assignment}")
            self.actor_priority_assignments = new_assignments
            priority += len(group)

        print(f"Generated {len(self.actor_priority_assignments)} actor priority assignments")


    def step4_identify_message_dependency_components(self):
        """Step 4: Identify Message Server Dependency Components (Class Level)"""
        print("\n=== Step 4: Identifying Message Dependency Components ===")

        self.class_message_permutations = {}

        for actor_class, class_info in self.analysis["actors"].items():
            print(f"Processing class {actor_class}")

            # همه‌ی متدهای این کلاس
            methods = list(class_info["methods"].keys())

            # همه‌ی یال‌های E_I مربوط به این کلاس
            intra_edges = []
            for src, dst in self.E_I:
                src_inst, src_method = src.split('.')
                dst_inst, dst_method = dst.split('.')

                src_cls = self.instance_map.get(src_inst, {}).get("class")
                dst_cls = self.instance_map.get(dst_inst, {}).get("class")

                if src_cls == actor_class and dst_cls == actor_class:
                    intra_edges.append((src_method, dst_method))

            # گروه‌بندی متدها بر اساس E_I (هر گروه باید permute بشه)
            grouped = self._group_priority_assignment(intra_edges)

            # متدهایی که داخل گروه‌ها هستند
            used_methods = set(x for g in grouped for x in g)

            # متدهای بدون E_I (مستقل) → گروه تک‌عضوی ثابت
            for m in methods:
                if m not in used_methods and m.lower() != actor_class.lower():
                    grouped.append([m])

            all_permutations = []
            from itertools import product, permutations

            for group_perm in product(*[list(permutations(g)) for g in grouped]):
                final_ordering = []
                for g in group_perm:
                    final_ordering.extend(g)
                all_permutations.append(final_ordering)

            self.class_message_permutations[actor_class] = all_permutations
            print(f"  Class {actor_class}: {len(all_permutations)} permutations")

    def _group_priority_assignment(self, intra_edges: List[Tuple[str, str]]) -> List[List[str]]:
        """گروه‌بندی متدها بر اساس یال‌های E_I"""
        # گراف بدون جهت از intra_edges
        neighbors = defaultdict(set)
        for u, v in intra_edges:
            neighbors[u].add(v)
            neighbors[v].add(u)

        visited = set()
        groups = []

        def dfs(node, group):
            visited.add(node)
            group.append(node)
            for nei in neighbors[node]:
                if nei not in visited:
                    dfs(nei, group)

        for node in neighbors:
            if node not in visited:
                group = []
                dfs(node, group)
                groups.append(group)

        return groups

    def step5_generate_prioritized_test_cases(self):
        """Step 5: Generate Prioritized Test Cases"""
        print("\n=== Step 5: Generating Prioritized Test Cases ===")

        self.test_cases = []
        test_id = 1

        # For each combination of actor priority assignments
        for actor_assignment in self.actor_priority_assignments:

            # Generate all combinations of message server permutations across all classes
            class_names = list(self.class_message_permutations.keys())
            class_permutations = [self.class_message_permutations[cls] for cls in class_names]

            from itertools import product
            for msg_combination in product(*class_permutations):
                # Build method priorities for this combination
                method_priorities = {}

                for i, class_name in enumerate(class_names):
                    method_ordering = msg_combination[i]
                    method_priorities[class_name] = {}

                    for priority, method in enumerate(method_ordering, 1):
                        method_priorities[class_name][method] = priority

                # Create test case
                test_case = TestCase(
                    id=test_id,
                    actor_priorities=actor_assignment.copy(),
                    method_priorities=method_priorities
                )

                self.test_cases.append(test_case)
                test_id += 1

        print(f"Generated {len(self.test_cases)} test cases")



    def generate_dependency_guided_tests(self) -> List[TestCase]:
        """Main method implementing the complete algorithm"""
        print("\n=== Dependency-Guided Test Generation using ERDG ===")

        # Build ERDG first
        self.build_erdg()

        # Algorithm steps
        self.step1_build_actor_dependency_graph()
        self.step2_identify_actor_groups_and_build_hag()
        self.step3_assign_priorities_to_actors()
        self.step4_identify_message_dependency_components()
        self.step5_generate_prioritized_test_cases()

        return self.test_cases

    def print_test_cases(self):
        """Print all generated test cases"""
        print(f"\n=== Generated Test Cases ({len(self.test_cases)}) ===")

        for i, test_case in enumerate(self.test_cases[:10]):  # Show first 10
            print(f"\nTest Case {test_case.id}:")
            print(f"  Actor Priorities: {test_case.actor_priorities}")
            print(f"  Method Priorities:")
            for class_name, methods in test_case.method_priorities.items():
                print(f"    {class_name}: {methods}")

        if len(self.test_cases) > 10:
            print(f"\n... and {len(self.test_cases) - 10} more test cases")
