Last login: Wed Sep 17 13:38:30 on ttys000
➜  ~ cd ~/Desktop/thesis-implementation

➜  thesis-implementation git:(main) ✗ git add .gitignore

➜  thesis-implementation git:(main) ✗ git commit -m "Update .gitignore to exclude logs and terminal outputs"

On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   src/Terminal Saved Output.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore.save

no changes added to commit (use "git add" and/or "git commit -a")
➜  thesis-implementation git:(main) ✗ git push origin main

Everything up-to-date
➜  thesis-implementation git:(main) ✗ python3 -m src.main
Processing class: Customer
Processing vars for actor: Customer
Adding statevar sent to Customer
Processing method customer for actor Customer
Method customer writes to sent
Method customer sends start to self
Processing method start for actor Customer
Method start sends ask to agent
Method start writes to sent
Processing method done for actor Customer
Method done writes to sent
Processing class: Agent
Processing vars for actor: Agent
Adding statevar dummy to Agent
Processing method agent for actor Agent
Processing method ask for actor Agent
Method ask sends process to ticketService
Processing class: TicketService
Processing vars for actor: TicketService
Adding statevar dummy to TicketService
Processing method ticketService for actor TicketService
Processing method process for actor TicketService
Method process sends done to customer
Processing main block
Found actor instance: c1 of class Customer, priority None
Found actor instance: c2 of class Customer, priority None
Found actor instance: agent of class Agent, priority None
Found actor instance: ticketService of class TicketService, priority None
✅ AST graph saved as AST.png

=== Analysis Result ===
{'actors': {'Agent': {'methods': {'agent': {'priority': None,
                                            'reads': set(),
                                            'sends': [],
                                            'writes': set()},
                                  'ask': {'priority': None,
                                          'reads': set(),
                                          'sends': [('ticketService',
                                                     'process')],
                                          'writes': set()}},
                      'statevars': {'dummy'}},
            'Customer': {'methods': {'customer': {'priority': None,
                                                  'reads': set(),
                                                  'sends': [('self', 'start')],
                                                  'writes': {'sent'}},
                                     'done': {'priority': None,
                                              'reads': set(),
                                              'sends': [],
                                              'writes': {'sent'}},
                                     'start': {'priority': None,
                                               'reads': set(),
                                               'sends': [('agent', 'ask')],
                                               'writes': {'sent'}}},
                         'statevars': {'sent'}},
            'TicketService': {'methods': {'process': {'priority': None,
                                                      'reads': set(),
                                                      'sends': [('customer',
                                                                 'done')],
                                                      'writes': set()},
                                          'ticketService': {'priority': None,
                                                            'reads': set(),
                                                            'sends': [],
                                                            'writes': set()}},
                              'statevars': {'dummy'}}},
 'main_instances': [{'arg': 'Customer',
                     'class': 'Customer',
                     'name': 'c1',
                     'priority': None},
                    {'arg': 'Customer',
                     'class': 'Customer',
                     'name': 'c2',
                     'priority': None},
                    {'arg': 'Agent',
                     'class': 'Agent',
                     'name': 'agent',
                     'priority': None},
                    {'arg': 'TicketService',
                     'class': 'TicketService',
                     'name': 'ticketService',
                     'priority': None}]}

=== Dependency-Guided Test Generation using ERDG ===

=== Building ERDG ===
Created rebec node: c1 (Customer)
Created rebec node: c2 (Customer)
Created rebec node: agent (Agent)
Created rebec node: ticketService (TicketService)
Created message server: c1.customer
Created message server: c1.start
Created message server: c1.done
Created message server: c2.customer
Created message server: c2.start
Created message server: c2.done
Created message server: agent.agent
Created message server: agent.ask
Created message server: ticketService.ticketService
Created message server: ticketService.process
Created activation: c1.customer -> c1.start
Created activation: c1.start -> agent.ask
Created activation: c2.customer -> c2.start
Created activation: c2.start -> agent.ask
Created activation: agent.ask -> ticketService.process
Created activation: ticketService.process -> c2.done
Skipping E_I edge for constructor method: customer in class Customer
Added E_I edge (write-after-write): c1.start → c1.done for variable sent
Skipping E_I edge for constructor method: customer in class Customer
Added E_I edge (write-after-write): c2.start → c2.done for variable sent
ERDG built successfully!
- Rebec nodes: 4
- Message server nodes: 10
- Activation nodes: 6
- Total edges: 30

=== Step 1: Building Actor Dependency Graph ===
Added actor dependency edge: c1 <-> c2
Added actor dependency edge: c2 <-> ticketService
Actor Dependency Graph: 2 edges
✅ Actor Dependency Graph saved as AG.png

=== Step 2: Identifying Actor Groups and Building HAG ===
Found 2 actor groups:
  Group 1: ['c1', 'c2', 'ticketService']
  Group 2: ['agent']
Added HAG edge: Group 1 -> Group 2
Added HAG edge: Group 2 -> Group 1
⚠️ Cycle detected between groups 1 and 2, resolved order: [1, 2]
✅ HAG saved as HAG.png

=== Step 3: Assigning Priorities to Actors ===
Processing group 1: ['c1', 'c2', 'ticketService']
  Permutation: ('c1', 'c2', 'ticketService') -> Priorities: {'c1': 1, 'c2': 2, 'ticketService': 3}
  Permutation: ('c1', 'ticketService', 'c2') -> Priorities: {'c1': 1, 'ticketService': 2, 'c2': 3}
  Permutation: ('c2', 'c1', 'ticketService') -> Priorities: {'c2': 1, 'c1': 2, 'ticketService': 3}
  Permutation: ('c2', 'ticketService', 'c1') -> Priorities: {'c2': 1, 'ticketService': 2, 'c1': 3}
  Permutation: ('ticketService', 'c1', 'c2') -> Priorities: {'ticketService': 1, 'c1': 2, 'c2': 3}
  Permutation: ('ticketService', 'c2', 'c1') -> Priorities: {'ticketService': 1, 'c2': 2, 'c1': 3}
Processing group 2: ['agent']
  Fixed assignment for agent -> Priority 4
Generated 6 actor priority assignments

=== Step 4: Identifying Message Dependency Components ===
Processing class Customer
  Class Customer: 2 permutations
Processing class Agent
  Class Agent: 1 permutations
Processing class TicketService
  Class TicketService: 1 permutations

=== Step 5: Generating Prioritized Test Cases ===
Generated 12 test cases
✅ ERDG graph saved as ERDG.png

=== Generated Test Cases (12) ===

Test Case 1:
  Actor Priorities: {'c1': 1, 'c2': 2, 'ticketService': 3, 'agent': 4}
  Method Priorities:
    Customer: {'start': 1, 'done': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 2:
  Actor Priorities: {'c1': 1, 'c2': 2, 'ticketService': 3, 'agent': 4}
  Method Priorities:
    Customer: {'done': 1, 'start': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 3:
  Actor Priorities: {'c1': 1, 'ticketService': 2, 'c2': 3, 'agent': 4}
  Method Priorities:
    Customer: {'start': 1, 'done': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 4:
  Actor Priorities: {'c1': 1, 'ticketService': 2, 'c2': 3, 'agent': 4}
  Method Priorities:
    Customer: {'done': 1, 'start': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 5:
  Actor Priorities: {'c2': 1, 'c1': 2, 'ticketService': 3, 'agent': 4}
  Method Priorities:
    Customer: {'start': 1, 'done': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 6:
  Actor Priorities: {'c2': 1, 'c1': 2, 'ticketService': 3, 'agent': 4}
  Method Priorities:
    Customer: {'done': 1, 'start': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 7:
  Actor Priorities: {'c2': 1, 'ticketService': 2, 'c1': 3, 'agent': 4}
  Method Priorities:
    Customer: {'start': 1, 'done': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 8:
  Actor Priorities: {'c2': 1, 'ticketService': 2, 'c1': 3, 'agent': 4}
  Method Priorities:
    Customer: {'done': 1, 'start': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 9:
  Actor Priorities: {'ticketService': 1, 'c1': 2, 'c2': 3, 'agent': 4}
  Method Priorities:
    Customer: {'start': 1, 'done': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

Test Case 10:
  Actor Priorities: {'ticketService': 1, 'c1': 2, 'c2': 3, 'agent': 4}
  Method Priorities:
    Customer: {'done': 1, 'start': 2}
    Agent: {'ask': 1}
    TicketService: {'process': 1}

... and 2 more test cases

✅ Results saved to generated_test_cases.txt
➜  thesis-implementation git:(main) ✗ git rm --cached "Terminal Saved Output.txt"

fatal: pathspec 'Terminal Saved Output.txt' did not match any files
➜  thesis-implementation git:(main) ✗ ls -l

total 0
-rw-r--r--  1 phone  staff    0 Sep 16 22:26 README.md
drwxr-xr-x  5 phone  staff  160 Sep 17 13:29 outputs
drwxr-xr-x  9 phone  staff  288 Sep 17 13:40 src
➜  thesis-implementation git:(main) ✗ git rm --cached "src/Terminal Saved Output.txt"

rm 'src/Terminal Saved Output.txt'
➜  thesis-implementation git:(main) ✗ git commit -m "remove Terminal Saved Output.txt from repo"

[main f02c5aa] remove Terminal Saved Output.txt from repo
 1 file changed, 1432 deletions(-)
 delete mode 100644 src/Terminal Saved Output.txt
➜  thesis-implementation git:(main) ✗ git push origin main

Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 316 bytes | 316.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
To github.com:zeinabhosseinii/thesis-implementation.git
   dc4ed80..f02c5aa  main -> main
➜  thesis-implementation git:(main) ✗ git add README.md

➜  thesis-implementation git:(main) ✗ git commit -m "add README with project description and usage"

On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   .DS_Store

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore.save
	src/.DS_Store

no changes added to commit (use "git add" and/or "git commit -a")
➜  thesis-implementation git:(main) ✗ nano README.md


  UW PICO 5.09                    File: README.md                     Modified  

Graphical outputs (in .png format) are stored in the outputs/images/ folder:
AST.png – Abstract Syntax Tree of the input model
ERDG.png – Extended Rebeca Dependency Graph
AG.png – Actor Dependency Graph
HAG.png – Hierarchical Actor Group Graph
The file outputs/generated_test_cases.txt contains all generated prioritized te$
📬 Contact
For questions, discussions, or collaboration opportunities, feel free to contac$
📧 zeinab.hosseinii78@gmail.com
"""










^G Get Help  ^O WriteOut  ^R Read File ^Y Prev Pg   ^K Cut Text  ^C Cur Pos   
^X Exit      ^J Justify   ^W Where is  ^V Next Pg   ^U UnCut Text^T To Spell  
