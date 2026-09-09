# Before you write anything

These notes come from what went wrong or nearly went wrong here, and from adversarial reviews of
the plan. None of it is Mazda guidance.

## What can actually go wrong

- **Interrupted write.** The only realistic way to damage the cluster is losing power or the
  adapter mid-write. FORScan refuses to program below about 11.5 V, but do not rely on that.
- **Wrong block.** *Write All* writes every block including `720-03-01`, which is read-only on this
  cluster, and block 04, which holds VIN-related data and its own CCC checksum. Only press the
  **Write** button on the `720-01-09` row (it writes block 01).
- **Region-code side effects.** The region byte selects more than the fuel unit: language list,
  warning text, indicator logic. The SergSlim sheet notes that EU region on US-wired cars can
  raise airbag-indicator DTCs. Region 101 caused nothing visible on this car, but check.
- **Confusing yourself.** Two failed attempts here were partly self-inflicted: no read-back, no
  sleep cycle, no DTC baseline. See the protocol.

## Battery and power

- Ignition ON, engine OFF. The write takes seconds; the whole session should stay under about 5 min
  of key-on time. The engine must be off so nothing on the bus is busy during the write and so the
  cluster can reset cleanly.
- Battery at rest ≥ 12.3 V (FORScan shows it). Headlights, HVAC blower, seat heaters off.
- A regulated 13.x V supply is nice to have, not required for a single-line write.
- Key-OFF waiting (the sleep cycle) drains nothing meaningful.

## Protocol used for attempts 2 and 3

1. **Baseline.** Read DTCs on all modules and save the report. Save the IC As-Built (`Save All`,
   `.abt`). Write down the original line.
2. **Edit one line only.** Change `720-01-01`, recompute the checksum with
   `tools/asbuilt_line_checksum.py`, double-check the data bytes (the checksum cannot tell you
   which byte you changed).
3. **Write block 01.** Leave *Don't reset module after programming* unchecked. Press Write on
   the `720-01-09` row. Watch whether the cluster blanks/resets.
4. **Read back.** Close and reopen the As-Built screen, read the line again. If it shows the old
   value, the module rejected it: stop and investigate rather than retry blindly.
5. **Sleep cycle.** FORScan *Disconnect* → ignition OFF → **unplug the OBD adapter** → close the
   doors (locking helps) → do not touch the brake pedal, doors or remote for ≥ 5 min.
   With the adapter plugged in the bus never sleeps and some modules never reload As-Built.
6. **Check.** Ignition ON. Cluster trip display unit, Mazda Connect Fuel Economy screen,
   temperature unit, language, warning text. No average reset needed.
7. **DTC compare.** Scan again, compare against the baseline. A history code on the CMU or BCM
   from the reset itself is normal; a new confirmed code is not.
8. **Rollback** if anything is off: write the original line the same way, sleep cycle, re-check.

## Things that are not evidence

- "No change" 30 seconds after the write.
- "No change" without confirming the line persisted.
- A DTC that was already there before the write. Take the baseline.

## Do not

- Do not write `720-03-01` or block 04 for this purpose.
- Do not write `27E1 E22E 80C1` (B3 b3); that bit is a fixed value.
- Do not change more than one variable per attempt; you will not know what did what.
