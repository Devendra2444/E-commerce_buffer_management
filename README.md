# Buffer Problem Detector
**Producer-Consumer problem, explained with an e-commerce warehouse**

## 1. Overview

The Producer-Consumer problem is about two groups sharing a limited storage area (a *bounded buffer*):

- **Producers** put items in.
- **Consumers** take items out.
- The storage can hold only a fixed number of items, and it can never go below zero.

This project shows the problem using an online store. You enter the numbers, the program simulates sellers and buyers acting at the same time, and then it tells you **whether a buffer problem happened, which one, and why**, in simple words. If nothing went wrong, it says so.

| Computer science term | E-commerce meaning |
|---|---|
| Producer | Seller (ships products to the warehouse) |
| Consumer | Buyer (orders products) |
| Bounded buffer | Warehouse with a maximum capacity |
| Buffer size | Warehouse capacity |
| Items in buffer | Stock |

### The three buffer cases

| Case | In simple words | Store example |
|---|---|---|
| **Overflow** | Items added when there is no space, and nobody checked | Warehouse is full (5/5) but sellers still ship more, so stock reaches 8 |
| **Underflow** | Items taken when there is nothing left, and nobody checked | 1 item left, 2 buyers click Buy, the second gets a ghost order (stock -1) |
| **Race condition** | Everyone checked correctly, but at the same moment, so all went ahead | 1 iPhone left, two buyers both see "1 in stock", both buy it |

## 2. Project structure

```
buffer_demo/
├── main.py        Menu and program flow (run this file)
├── warehouse.py   Simulation engine: warehouse, sellers, buyers, protection levels
├── analyzer.py    Reads what happened and decides: overflow, underflow, race, or none
├── display.py     Prints the input summary, timeline, numbers, result, verification table
├── examples.py    Ready-made inputs for each case, with the expected outcome
├── web/           Web simulator (same logic, runs in the browser)
│   ├── index.html   Page layout: inputs, warehouse shelf, timeline, result, examples
│   ├── style.css    Styling (light and dark theme)
│   └── script.js    Simulation engine, analyzer, examples, and page behaviour
└── README.md      This file
```

How the pieces connect:

```
 your input ──> warehouse.py ──> event log ──> analyzer.py ──> display.py ──> screen
                (simulate)       (what         (which problem   (explain in
                                 happened)      and why)         simple words)
```

## 3. How to run

```
cd buffer_demo
python3 main.py
```

Only the Python standard library is used. Menu:

1. **Enter my own input** (you type the 7 inputs below)
2. **Run a ready-made example** (pick one of the 6 examples)
3. **Verify all examples** (runs all 6 and prints a PASS/FAIL table)

### Web simulator

Open `web/index.html` in any browser (double-click it). No server or install is needed. It has the same 7 inputs, the same six examples, and the same detection rules as the Python version, plus a live warehouse shelf and an animated timeline. The "Verify all examples" button shows the same PASS/FAIL table.

## 4. Inputs

| # | Input | Meaning | Rules |
|---|---|---|---|
| 1 | **Warehouse capacity** | Maximum items the warehouse can hold | Whole number, at least 1 |
| 2 | **Starting stock** | Items in the warehouse at the start | 0 up to the capacity |
| 3 | **Number of sellers** | Sellers shipping at the same time | 0 or more |
| 4 | **Products each seller ships** | How many items each seller adds, one by one | 0 or more (asked only if sellers > 0) |
| 5 | **Number of buyers** | Buyers ordering at the same time | 0 or more |
| 6 | **Items each buyer buys** | How many items each buyer takes, one by one | 0 or more (asked only if buyers > 0) |
| 7 | **Protection level** | What safety the store has (see below) | 1, 2 or 3 |

### Protection levels

| Level | Name | What it means | Which problem it allows |
|---|---|---|---|
| 1 | **None** | No checks, no lock | Overflow and Underflow |
| 2 | **Checks only** | Looks at stock/space before acting, but anyone can act at the same time | Race condition |
| 3 | **Full protection** | Checks plus a lock, so one actor works at a time | None |

## 5. Outputs

| Section | What it shows |
|---|---|
| **YOUR INPUT** | A recap of the 7 values you entered |
| **WHAT HAPPENED** | Every shipment and order in order, with the stock after each step. A warning marks steps where stock went above capacity or below 0 |
| **NUMBERS** | Capacity, starting stock, final stock, shipments done, orders done, and how many were refused safely |
| **RESULT** | `✓ NO BUFFER PROBLEM`, or `✗` followed by each problem found with a **Why** explanation |

Result meanings:

- **BUFFER OVERFLOW:** stock went above capacity and no capacity check was used.
- **BUFFER UNDERFLOW:** an order was accepted when stock was 0 and no stock check was used.
- **RACE CONDITION:** stock still broke the limits even though checks were on, because several actors acted at the same time.
- **NO BUFFER PROBLEM:** stock always stayed between 0 and capacity. "Refused safely" shipments or orders are correct behaviour, not a problem.

## 6. Example inputs for the three buffer cases

Enter these under menu option 1, or pick them under option 2.

| Example | Capacity | Stock | Sellers | Each ships | Buyers | Each buys | Protection | Expected result |
|---|---|---|---|---|---|---|---|---|
| **1. Overflow** | 5 | 5 | 3 | 1 | 0 | 0 | 1 (None) | BUFFER OVERFLOW (stock reaches 8) |
| **2. Underflow** | 5 | 1 | 0 | 0 | 2 | 1 | 1 (None) | BUFFER UNDERFLOW (stock -1) |
| **3a. Race (oversell)** | 5 | 1 | 0 | 0 | 2 | 1 | 2 (Checks only) | RACE CONDITION (2 orders for 1 item) |
| **3b. Race (overflow)** | 5 | 4 | 3 | 1 | 0 | 0 | 2 (Checks only) | RACE CONDITION (stock above 5) |
| **4. Fixed** | 5 | 1 | 0 | 0 | 2 | 1 | 3 (Full) | NO BUFFER PROBLEM (1 order, 1 refused) |
| **5. Light traffic** | 10 | 2 | 2 | 2 | 1 | 1 | 1 (None) | NO BUFFER PROBLEM |

Tips for presenting:

- Run examples 2, then 3a, then 4. They use the same numbers, and only the protection level changes: ghost order, then race, then fixed.
- A race needs a gap. With checks on and a completely full warehouse (stock = capacity), every seller sees "full" and is refused, so there is no race. Use stock 4 of 5, as in 3b.

### Verifying all three cases at once

Choose menu option 3. Expected output:

```
--- VERIFICATION OF ALL EXAMPLES ---
  Example                         Expected      Detected      Status
  --------------------------------------------------------------------
  Overflow                        OVERFLOW      OVERFLOW      PASS ✓
  Underflow                       UNDERFLOW     UNDERFLOW     PASS ✓
  Race condition (oversell)       RACE          RACE          PASS ✓
  Race condition (overflow)       RACE          RACE          PASS ✓
  No problem (full protection)    NONE          NONE          PASS ✓
  No problem (light traffic)      NONE          NONE          PASS ✓
  --------------------------------------------------------------------
  ✓ All three buffer cases (Overflow, Underflow, Race) were triggered and detected correctly.
```

## 7. How detection works

The simulation records every shipment and order with the stock after it. The analyzer then applies these rules:

1. Stock went **above capacity** and there was **no capacity check** (level 1): **Overflow**.
2. Stock went **below 0** and there was **no stock check** (level 1): **Underflow**.
3. Stock broke either limit **even though checks were on** (level 2): **Race condition**.
4. Stock stayed within 0 and capacity: **no problem**.

If more than one type happens in one run, all of them are reported.

## 8. Simple fix for each problem

| Problem | Fix |
|---|---|
| Overflow | Check free space before shipping (or make the seller wait) |
| Underflow | Check stock before selling (or make the buyer wait) |
| Race condition | Use a lock so check-and-change happens as one step; semaphores for waiting |
# E-commerce_buffer_management
