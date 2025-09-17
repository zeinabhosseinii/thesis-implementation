# ======== Grammar Definition ========
grammar = r"""
?start: model

model: class_def* main_block?

main_block: "main" "{" actor_instance* "}"

actor_instance: CNAME "actor" ":" "(" CNAME ")" priority_block? ";"

priority_block: "priority" NUMBER

class_def: "actorclass" CNAME "{" vars? method+ "}"

vars: "statevars" var_decl*
var_decl: TYPE CNAME ";"

method: "method" NAME priority_block? "{" stmt* "}" "end"

?stmt: assign_stmt ";"
    | send_stmt ";"
    | "skip" ";"
    | "++" ";"
    | if_stmt

assign_stmt: CNAME "=" expr
send_stmt: CNAME "!" NAME
if_stmt: "if" "(" expr ")" "{" stmt* "}" "else" "{" stmt* "}"

?expr: expr "+" expr   -> add
    | expr "-" expr   -> sub
    | expr "*" expr   -> mul
    | expr "/" expr   -> div
    | CNAME
    | NUMBER
    | ESCAPED_STRING
    | "true"
    | "false"

TYPE: /[A-Z][a-zA-Z0-9_]*/
NAME: /[a-z_][a-zA-Z0-9_]*/

%import common.CNAME
%import common.NUMBER
%import common.WS
%import common.ESCAPED_STRING
%ignore WS
"""