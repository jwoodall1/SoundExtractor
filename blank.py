import graphviz

# Create DFA diagram
dfa = graphviz.Digraph("DFA_B_reverse", format="png")
dfa.attr(rankdir="LR", size="8")

# States
dfa.attr("node", shape="circle")
dfa.node("q0", "q0\n(start, accept)")
dfa.node("q1", "q1")
dfa.node("dead", "dead", shape="doublecircle")

# Mark accepting state (q0)
dfa.node("q0", shape="doublecircle")

# Transitions from q0
dfa.edge("q0", "q0", label="[0 0 0], [0 1 1], [1 0 1]")
dfa.edge("q0", "q1", label="[1 1 0]")

# Transitions from q1
dfa.edge("q1", "q0", label="[0 0 1]")
dfa.edge("q1", "q1", label="[0 1 0], [1 0 0], [1 1 1]")

# Dead state transitions (all other columns)
dfa.edge("q0", "dead", label="others")
dfa.edge("q1", "dead", label="others")
dfa.edge("dead", "dead", label="all")

dfa.render("/mnt/data/dfa_b_reverse", format="png", cleanup=True)
"/mnt/data/dfa_b_reverse.png"
