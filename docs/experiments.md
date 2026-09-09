# Experiments on this car

Car: 2019 MX-5 ND2 2.0, Mexican market, IC `ND6N-55430-0` / `ND6A-554K2-A`, CMU `74.00.324`,
FORScan 2.3.71 extended, vLinker FS USB. Factory `720-01-01` = `27E1 E226 80B9`
(region 011 Canada, B3 `26`, L/100km on the cluster and on the Mazda Connect fuel-economy screen).

## Attempt 1 – 2026-09-06 – `27E1 E2E6 8079` – no change (inconclusive)

- Changed B3 `26` → `E6` (b7b6 = 11), the value every km/L car in the dump table has.
- Wrote block 01, cycled ignition with a ~30 s wait, saw L/100km, rolled back.
- Not recorded: whether the line read back as `E2E6` after reconnecting, whether the cluster reset
  after the write, and no sleep cycle with the adapter unplugged. So this attempt cannot separate
  "wrong value" from "write not applied".

Lesson: without a read-back and a real sleep cycle, "no change" is not a result.

## Attempt 2 – 2026-09-09 – `27E1 E2E6 8079` – no change (write verified)

- Same value, this time with the protocol in `safety.md`.
- Read-back after reconnecting showed `27E1 E2E6 8079`, so the cluster accepted and kept the write.
- Cluster and CMU still L/100km after the sleep cycle.

Conclusion: the write path works; `E6` under region 011 does not map to km/L on this cluster.

## Attempt 3 – 2026-09-09 – `2BE1 E2E6 807D` – km/L

- From the attempt-2 state, changed only B0 `27` → `2B` (region 011 → 101). Checksum `79` + 4 = `7D`.
- Cluster trip display switched to km/L. Mazda Connect fuel-economy screen followed.
- Temperature still °C, CMU still English, Android Auto still working.
- DTC scan afterwards: all modules clean except a CMU USB-hub code that pre-dates this work
  (`dtc-b1252.md`). The IC itself reported nothing.

## Why region 101 and not the others

Candidates that were considered, in the order they were ranked before attempt 3:

| Value | Region | Reason for / against |
|---|---|---|
| `2BE1 E2E6 807D` | 101 South America / Asia | Likely factory configuration of km/L Latin-American cars. No hex evidence, but no known side effects for a metric NA-wiring car. **Worked.** |
| `2FE1 E2E6 8081` | 111 Saudi | Gulf cars show km/L with English UI. Unknown language list / RTL effects. Not tried. |
| `23E1 E2E6 8075` | 001 Europe | Proven km/L on JDM ND and Mazda6 GJ, but with English CMU language EU maps to mpg. Also the sheet warns that EU region on NA wiring can raise airbag-indicator DTCs. Not tried. |
| `21E1 E2E6 8073` | 000 Japan | JDM ND forces km/L, but reports of garbled characters on non-JDM clusters. Not tried. |

## Not tested

- `2BE1 E266 80FD` (region 101, b6 only). Would tell whether b7 is needed. Expected mpg based on
  US dumps, but the region table may differ.
- `67E1 E226 80F9` (temperature °C → °F) as a write-path check. Became unnecessary once the read-back
  confirmed persistence.
- Any hidden cluster service mode on the ND.

## Practical notes

- The Write button on the `720-01-09` row writes the whole block 01. Block 01 has no block-level
  checksum: `720-01-09` (`0858 5252 35`) is identical on an unrelated Mazda3 BM and is all zeros on a
  JDM ND RF, so it is not a function of the block data. Only block 04 carries a CCC checksum in
  `720-04-01`.
- Line checksum = `(0x07 + 0x20 + block + line + sum of the five data bytes) mod 256`, where
  `line` is the two decimal digits read as hex (line 10 → 0x10). Verified against all 32 lines of this cluster.
- The average-economy value did not need a reset for the unit label to change.
- A 30 s key-off is not a sleep cycle. With the OBD adapter unplugged and the doors closed, the bus
  sleeps in a few minutes; 5 min was used.
