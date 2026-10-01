"""
warehouse.py  -  the simulation engine.

Seller = Producer (adds stock) | Buyer = Consumer (removes stock)
Warehouse = Bounded Buffer (holds 0..capacity items)

Protection levels:
  1 = None            (no checks, no lock)
  2 = Checks only     (look before acting, but no lock)
  3 = Full protection (checks + lock, one actor at a time)
"""
import threading
import time

LATENCY = 0.05  # small delay between "looking at stock" and "changing stock"

PROTECTION_NAMES = {1: "None", 2: "Checks only", 3: "Full (checks + lock)"}


class Warehouse:
    def __init__(self, capacity, stock, protection):
        self.capacity = capacity
        self.stock = stock
        self.check = protection in (2, 3)      # look before acting
        self.use_lock = protection == 3        # one at a time
        self.biz = threading.Lock()            # the "business" lock
        self.meta = threading.Lock()           # bookkeeping only
        self.events = []                       # everything that happened

    def _record(self, actor, kind, seen, before, after):
        self.events.append(dict(actor=actor, kind=kind, seen=seen,
                                before=before, after=after))

    def ship_one(self, actor):
        if self.use_lock:
            self.biz.acquire()
        try:
            seen = None
            if self.check:
                seen = self.stock
                if seen >= self.capacity:
                    with self.meta:
                        self._record(actor, "ship_refused", seen, seen, seen)
                    return
            time.sleep(LATENCY)
            with self.meta:
                before = self.stock
                self.stock += 1
                self._record(actor, "ship", seen, before, self.stock)
        finally:
            if self.use_lock:
                self.biz.release()

    def buy_one(self, actor):
        if self.use_lock:
            self.biz.acquire()
        try:
            seen = None
            if self.check:
                seen = self.stock
                if seen <= 0:
                    with self.meta:
                        self._record(actor, "buy_refused", seen, seen, seen)
                    return
            time.sleep(LATENCY)
            with self.meta:
                before = self.stock
                self.stock -= 1
                self._record(actor, "buy", seen, before, self.stock)
        finally:
            if self.use_lock:
                self.biz.release()


def simulate(capacity, stock, sellers, per_seller, buyers, per_buyer, protection):
    """Run all sellers and buyers at the same time. Returns the Warehouse."""
    w = Warehouse(capacity, stock, protection)
    barrier = threading.Barrier(max(1, sellers + buyers))

    def seller(name):
        barrier.wait()
        for _ in range(per_seller):
            w.ship_one(name)

    def buyer(name):
        barrier.wait()
        for _ in range(per_buyer):
            w.buy_one(name)

    threads = [threading.Thread(target=seller, args=(f"Seller #{i}",))
               for i in range(1, sellers + 1)]
    threads += [threading.Thread(target=buyer, args=(f"Buyer #{i}",))
                for i in range(1, buyers + 1)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return w
