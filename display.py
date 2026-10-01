"""display.py  -  everything that prints to the screen."""
from warehouse import PROTECTION_NAMES


def show_inputs(capacity, stock, sellers, per_seller, buyers, per_buyer, protection):
    print("\n--- YOUR INPUT ---")
    print(f"  Capacity            : {capacity}")
    print(f"  Starting stock      : {stock}")
    print(f"  Sellers             : {sellers} (each ships {per_seller})")
    print(f"  Buyers              : {buyers} (each buys {per_buyer})")
    print(f"  Protection          : {protection} = {PROTECTION_NAMES[protection]}")


def show_timeline(w, start, limit=40):
    print("\n--- WHAT HAPPENED (in order) ---")
    print(f"  Start: stock = {start}")
    for i, e in enumerate(w.events[:limit], 1):
        who = e["actor"]
        if e["kind"] == "ship":
            msg = f"{who} shipped 1 -> stock {e['after']}"
            if e["after"] > w.capacity:
                msg += "   <-- over capacity!"
        elif e["kind"] == "buy":
            msg = f"{who} sold 1 -> stock {e['after']}"
            if e["after"] < 0:
                msg += "   <-- item did not exist!"
        elif e["kind"] == "ship_refused":
            msg = f"{who} shipment refused (warehouse full)"
        else:
            msg = f"{who} order refused (sold out)"
        print(f"  {i:>2}. {msg}")
    if len(w.events) > limit:
        print(f"  ... and {len(w.events) - limit} more events")


def show_result(w, start, problems):
    shipped = sum(1 for e in w.events if e["kind"] == "ship")
    sold = sum(1 for e in w.events if e["kind"] == "buy")
    ref_s = sum(1 for e in w.events if e["kind"] == "ship_refused")
    ref_b = sum(1 for e in w.events if e["kind"] == "buy_refused")

    print("\n--- NUMBERS ---")
    print(f"  Capacity: {w.capacity}   Start: {start}   Final stock: {w.stock}")
    print(f"  Shipments done: {shipped}   Orders done: {sold}")
    if ref_s or ref_b:
        print(f"  Refused safely: {ref_s} shipment(s), {ref_b} order(s)")

    print("\n--- RESULT ---")
    if not problems:
        print(f"  ✓ NO BUFFER PROBLEM. Stock always stayed between 0 and {w.capacity}.")
        if ref_s or ref_b:
            print("    Extra shipments/orders were refused, which is the correct, "
                  "safe behaviour.")
    else:
        print(f"  ✗ {len(problems)} problem type(s) found:\n")
        for _, title, why in problems:
            print(f"  >> {title}")
            print(f"     Why: {why}\n")


def show_verification(rows):
    print("\n--- VERIFICATION OF ALL EXAMPLES ---")
    print(f"  {'Example':<32}{'Expected':<14}{'Detected':<14}Status")
    print("  " + "-" * 68)
    for name, exp, got, ok in rows:
        print(f"  {name:<32}{exp:<14}{got:<14}{'PASS ✓' if ok else 'FAIL ✗'}")
    print("  " + "-" * 68)
    seen = {k for _, _, got, ok in rows if ok for k in got.split("+")}
    covered = [k for k in ("OVERFLOW", "UNDERFLOW", "RACE") if k in seen]
    if all(ok for *_, ok in rows) and len(covered) == 3:
        print("  ✓ All three buffer cases (Overflow, Underflow, Race) were "
              "triggered and detected correctly.")
    else:
        print("  ✗ Something did not match. Run again or check the inputs.")
