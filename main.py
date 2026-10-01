"""
main.py  -  entry point.   Run:  python3 main.py

1) Enter your own input
2) Run one ready-made example
3) Verify all examples (PASS/FAIL table)
"""
from warehouse import simulate
from analyzer import analyze
from examples import EXAMPLES
from display import show_inputs, show_timeline, show_result, show_verification


def ask_int(prompt, lo=0):
    while True:
        try:
            v = int(input(prompt).strip())
            if v >= lo:
                return v
            print(f"   Please enter a number >= {lo}")
        except ValueError:
            print("   Please enter a whole number.")


def run_and_show(capacity, stock, sellers, per_seller, buyers, per_buyer, protection):
    show_inputs(capacity, stock, sellers, per_seller, buyers, per_buyer, protection)
    if sellers + buyers == 0:
        print("\nNobody is shipping or buying, so nothing can go wrong.")
        return
    print("\nRunning simulation...")
    w = simulate(capacity, stock, sellers, per_seller, buyers, per_buyer, protection)
    show_timeline(w, stock)
    show_result(w, stock, analyze(w))


def custom_input():
    cap = ask_int("\nWarehouse capacity: ", 1)
    while True:
        stock = ask_int("Starting stock: ")
        if stock <= cap:
            break
        print(f"   Starting stock cannot be more than capacity ({cap}).")
    sellers = ask_int("Number of sellers: ")
    per_seller = ask_int("Products each seller ships: ") if sellers else 0
    buyers = ask_int("Number of buyers: ")
    per_buyer = ask_int("Items each buyer buys: ") if buyers else 0
    print("\nProtection level:")
    print("  1) None            (no checks, no lock)")
    print("  2) Checks only     (look before acting, no lock)")
    print("  3) Full protection (checks + lock)")
    protection = 0
    while protection not in (1, 2, 3):
        protection = ask_int("Choose 1, 2 or 3: ")
    run_and_show(cap, stock, sellers, per_seller, buyers, per_buyer, protection)


def pick_example():
    print("\nExamples:")
    for i, ex in enumerate(EXAMPLES, 1):
        print(f"  {i}) {ex['name']}\n       {ex['about']}")
    n = ask_int("Choose example number: ", 1)
    if n > len(EXAMPLES):
        print("   No such example.")
        return
    ex = EXAMPLES[n - 1]
    run_and_show(ex["capacity"], ex["stock"], ex["sellers"], ex["per_seller"],
                 ex["buyers"], ex["per_buyer"], ex["protection"])
    exp = " + ".join(sorted(ex["expect"])) or "NO PROBLEM"
    print(f"  (Expected for this example: {exp})")


def verify_all():
    print("\nRunning all examples...")
    rows = []
    for ex in EXAMPLES:
        w = simulate(ex["capacity"], ex["stock"], ex["sellers"], ex["per_seller"],
                     ex["buyers"], ex["per_buyer"], ex["protection"])
        got = {key for key, _, _ in analyze(w)}
        rows.append((ex["name"],
                     "+".join(sorted(ex["expect"])) or "NONE",
                     "+".join(sorted(got)) or "NONE",
                     got == ex["expect"]))
    show_verification(rows)


def main():
    print("=" * 56)
    print("  BUFFER PROBLEM DETECTOR  (Seller / Buyer / Warehouse)")
    print("=" * 56)
    while True:
        print("\n1) Enter my own input")
        print("2) Run a ready-made example")
        print("3) Verify all examples (PASS/FAIL)")
        print("q) Quit")
        c = input("Choose: ").strip().lower()
        if c == "1":
            custom_input()
        elif c == "2":
            pick_example()
        elif c == "3":
            verify_all()
        elif c == "q":
            break
        else:
            print("Invalid choice.")
    print("Bye!")


if __name__ == "__main__":
    main()
