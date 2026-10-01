"""
examples.py  -  ready-made inputs that trigger each buffer case.

Each example has the 7 inputs and the problem we EXPECT to see.
expect = set of keys: "OVERFLOW", "UNDERFLOW", "RACE"; empty set = no problem.
"""

EXAMPLES = [
    dict(name="Overflow",
         about="Warehouse is full (5/5) and 3 sellers ship 1 item each. No checks.",
         capacity=5, stock=5, sellers=3, per_seller=1, buyers=0, per_buyer=0,
         protection=1, expect={"OVERFLOW"}),

    dict(name="Underflow",
         about="Only 1 item left and 2 buyers click Buy. No checks.",
         capacity=5, stock=1, sellers=0, per_seller=0, buyers=2, per_buyer=1,
         protection=1, expect={"UNDERFLOW"}),

    dict(name="Race condition (oversell)",
         about="1 iPhone left, 2 buyers look at the same time. Checks on, no lock.",
         capacity=5, stock=1, sellers=0, per_seller=0, buyers=2, per_buyer=1,
         protection=2, expect={"RACE"}),

    dict(name="Race condition (overflow)",
         about="Room for 1 more (4/5) and 3 sellers look at the same time. Checks on, no lock.",
         capacity=5, stock=4, sellers=3, per_seller=1, buyers=0, per_buyer=0,
         protection=2, expect={"RACE"}),

    dict(name="No problem (full protection)",
         about="Same as the iPhone case but with checks + lock.",
         capacity=5, stock=1, sellers=0, per_seller=0, buyers=2, per_buyer=1,
         protection=3, expect=set()),

    dict(name="No problem (light traffic)",
         about="Plenty of room and plenty of stock, so nothing can break.",
         capacity=10, stock=2, sellers=2, per_seller=2, buyers=1, per_buyer=1,
         protection=1, expect=set()),
]
