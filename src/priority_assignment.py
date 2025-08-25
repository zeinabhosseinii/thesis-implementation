from typing import Dict, List, Tuple


# ======== Priority Assignment Functions ========
def group_priority_assignment(pairs):
    from collections import defaultdict, deque

    adj = defaultdict(set)
    for a, b in pairs:
        adj[a].add(b)
        adj[b].add(a)

    visited = set()
    groups = []

    for node in adj:
        if node not in visited:
            group = []
            queue = deque([node])
            visited.add(node)
            while queue:
                curr = queue.popleft()
                group.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            groups.append(group)

    all_nodes = set(x for pair in pairs for x in pair)
    isolated_nodes = [n for n in adj.keys() if n not in all_nodes]
    for node in isolated_nodes:
        groups.append([node])

    return groups

def generate_priority_text(trdg_builder):
    # Step 1: Group actors based on actor dependencies
    actor_deps = trdg_builder.find_actor_dependencies()
    actor_pairs = [(a1, a2) for a1, a2, _ in actor_deps]
    actor_groups = group_priority_assignment(actor_pairs)

    # Include independent actors
    all_actors = [r.name for r in trdg_builder.N_R]
    flat_grouped = set(x for g in actor_groups for x in g)
    independent_actors = [a for a in all_actors if a not in flat_grouped]
    for actor in independent_actors:
        actor_groups.append([actor])

    # Step 2: Group methods separately per class
    class_method_groups: Dict[str, List[List[str]]] = {}

    for instance in trdg_builder.N_R:
        instance_name = instance.name
        actor_class = instance.actor_class

        method_names = [
            m.method_name
            for m in trdg_builder.N_M
            if m.rebec_name == instance_name
        ]

        intra_edges = [
            (src.split(".")[1], dst.split(".")[1])  # extract only method names
            for (src, dst) in trdg_builder.E_I
            if src.startswith(f"{instance_name}.") and dst.startswith(f"{instance_name}.")
        ]

        grouped = group_priority_assignment(intra_edges)
        used_methods = set(x for g in grouped for x in g)

        class_method_groups.setdefault(actor_class, [])
        class_method_groups[actor_class].extend(grouped)

        for m in method_names:
            if m not in used_methods and m.lower() != actor_class.lower():
                class_method_groups[actor_class].append([m])

    # Step 3: Build output text
    text_lines = []

    text_lines.append("Actor Priorities:")
    for i, group in enumerate(actor_groups, start=1):
        text_lines.append(f"  Group {i} (priority = {i}): {', '.join(group)}")

    text_lines.append("\nMethod Priorities:")

    for actor_class, groups in class_method_groups.items():
        text_lines.append(f"\nClass {actor_class}:")
        for i, group in enumerate(groups, start=1):
            text_lines.append(f"  Group {i} (priority = {i}): {', '.join(group)}")

    return "\n".join(text_lines)
