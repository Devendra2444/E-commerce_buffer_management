"""
analyzer.py  -  reads the event log and decides which buffer problem happened.

Rules (based on what actually happened, not on the inputs):
  OVERFLOW  : stock went above capacity, and there was NO capacity check.
  UNDERFLOW : stock went below 0, and there was NO stock check.
  RACE      : stock still broke the limits even though checks were ON,
              because several actors looked at the same moment.
"""


def analyze(w):
    """Return a list of (key, title, why). Empty list = no buffer problem."""
    ev = w.events
    over = [e for e in ev if e["kind"] == "ship" and e["after"] > w.capacity]
    under = [e for e in ev if e["kind"] == "buy" and e["after"] < 0]
    problems = []

    if over and not w.check:
        peak = max(e["after"] for e in over)
        problems.append((
            "OVERFLOW", "BUFFER OVERFLOW",
            f"The warehouse holds {w.capacity} items but reached {peak}. "
            f"Sellers kept shipping and nobody checked if there was free space."))

    if under and not w.check:
        low = min(e["after"] for e in under)
        problems.append((
            "UNDERFLOW", "BUFFER UNDERFLOW",
            f"{len(under)} order(s) were accepted for items that were not in "
            f"stock (stock dropped to {low}). Buyers clicked 'Buy' and nobody "
            f"checked if anything was left, so ghost orders were created."))

    race = []
    if over and w.check:
        race.append(
            f"{len(over)} shipment(s) pushed stock above {w.capacity}: several "
            f"sellers looked, all saw free space, and all shipped at the same time.")
    if under and w.check:
        race.append(
            f"{len(under)} order(s) were confirmed for items that were already "
            f"gone: several buyers looked, all saw stock available, and all "
            f"bought at the same time.")
    if race:
        problems.append((
            "RACE", "RACE CONDITION",
            " ".join(race) + " Each check was correct on its own, but nothing "
            "stopped others from acting between the check and the change."))
    return problems
