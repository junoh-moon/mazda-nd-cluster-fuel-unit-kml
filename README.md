# Mazda MX-5 ND: switching the cluster fuel-economy unit to km/L with FORScan

One car, one result: a **2019 Mazda MX-5 ND2 built for the Mexican market** (imported to Korea)
showed fuel economy in **L/100km** on the instrument cluster. Changing one As-Built line in the
instrument cluster with FORScan made it show **km/L**.

| | 720-01-01 |
|---|---|
| Original (L/100km) | `27E1 E226 80B9` |
| **Working (km/L)** | **`2BE1 E2E6 807D`** |

Two earlier attempts that changed only the "fuel unit" bits did nothing. The change that worked
needed **both** the fuel-unit field **and** the region code. Details, failures, and the evidence
behind the bit interpretation are in `docs/`.

> This is a write-up of what happened on one car. It is not an official procedure. Writing
> As-Built data can change other cluster behaviour and can leave the module in a bad state if the
> write is interrupted. Read `docs/safety.md` first. You do this at your own risk.

## What was changed

Line `720-01-01` of the IC (instrument cluster, address 0x720) As-Built block 01.
Five bits in two bytes moved; everything else stayed as it was.

| Byte | Bits | Meaning | Before | After |
|---|---|---|---|---|
| B0 | b3 b2 b1 | Region code | `011` Canada | `101` South America / Asia |
| B3 | b7 b6 | Fuel-economy unit field | `00` | `11` |
| B5 | | Line checksum | `B9` | `7D` |

Bit labels come from the SergSlim "Mazda SkyActiv OBD-II calc (FORScan)" spreadsheet v7.14
(IC tab). That sheet documents only B3 **b6** ("Fuel Consumption Units: 0 = L/100 km, 1 = MPG",
noted as tested on Mazda6 GJ / CX-5 KE with TomTom units) and marks b7 as unknown.
The two-bit interpretation and the region interaction come from comparing dumps of other cars,
see `docs/unit-model.md`.

## Why the region code mattered

Observed across ~20 dumps from JDM, EU, US, Asian, Mexican and Taiwanese cars:

- B3 b7b6 = `00` → L/100km, in every region.
- B3 b7b6 = `01` (`66`) → mpg (US cars).
- B3 b7b6 = `11` (`E6`) → km/L on JDM cars, on EU-region Mazda6/ND, on Gulf and Israeli cars.
- Changing the region code alone never changed the unit (Thai cars set to AUS, JDM set to EU,
  Taiwanese Mazda3 in region 101 with `26` still shows L/100km).

On this car, region `011` (Canada, which is how a Mexican-market ND leaves the factory) with
`E6` showed no change twice, even after a verified write and a full sleep cycle.
Region `101` with `E6` switched to km/L. The working model is therefore:
**the region selects a unit-mapping table, and b7b6 selects an entry in it**.
Entry `11` maps to km/L in table 101 but not in table 011.

Whether b7 is actually required (i.e. whether `2BE1 E266 80FD` would also give km/L)
was not tested. No km/L car in the collected dumps has `66`, so `E6` was used from the start.

## Procedure that was used

Full version with rationale: `docs/safety.md`. Short version:

1. Save the IC As-Built (`Save All` → `.abt`) and a DTC scan of all modules before touching anything.
2. Ignition ON, engine OFF, battery ≥ 12.3 V, all loads off, keep the session short.
3. In *IC Module configuration (AS BUILT format)*, edit only `720-01-01`. Recompute the
   checksum (`tools/asbuilt_line_checksum.py`). Press the **Write** button on the
   `720-01-09` row (it writes block 01). Never use *Write All*; `720-03-01` is read-only.
4. Disconnect FORScan, ignition OFF, **unplug the OBD adapter**, close the doors, wait ≥ 5 min so
   the modules actually sleep. The adapter keeps the bus awake if left plugged in.
5. Ignition ON. Check the trip display and the Mazda Connect Fuel Economy screen.
   Re-read the line in FORScan to confirm it persisted.
6. If anything looks wrong, write the original line back the same way.

## What happened

| Date | Line written | Result |
|---|---|---|
| 2026-09-06 | `27E1 E2E6 8079` (E6 only) | No change. Write/read-back and sleep cycle were not verified. Rolled back. |
| 2026-09-09 | `27E1 E2E6 8079` (E6 only) | No change. Read-back confirmed `E2E6` persisted. |
| 2026-09-09 | `2BE1 E2E6 807D` (region 101 + E6) | **km/L on the cluster.** |

All modules scanned clean afterwards except one pre-existing CMU code unrelated to the change
(`docs/dtc-b1252.md`). No side effects seen in the checks right after the change: temperature stays in °C, English UI,
Android Auto works.

## Car

- 2019 Mazda MX-5 ND2 2.0 (PE), manual, Mexican market, no Forward Sensing Camera.
- IC part `ND6N-55430-0`, strategy `ND6A-554K2-A`.
- CMU (Mazda Connect) firmware `74.00.324`. This older CMU has no km/L option in Settings;
  its fuel-economy screen follows the cluster unit.
- FORScan 2.3.71 with extended license, vLinker FS USB adapter.

## Status

This repository is an archived write-up of one car. It is not maintained and does not collect
reports. The dump table in `docs/unit-model.md` is what could be found as of September 2026;
gaps (factory hex from Gulf, Israeli, Latin-American or South-East-Asian km/L cars) remain.

## Repository layout

- `docs/unit-model.md` – all collected 720-01-01 dumps and the region × b7b6 model.
- `docs/experiments.md` – the three attempts on this car, what was verified each time, and why the first two are inconclusive.
- `docs/safety.md` – voltage, sleep cycle, what not to write, rollback.
- `docs/dtc-b1252.md` – the CMU USB-hub code seen afterwards and why it is unrelated.
- `tools/asbuilt_line_checksum.py` – computes/verifies the per-line checksum.
- `images/` – FORScan screenshots (identifying data cropped out).

## Credits and sources

- SergSlim, *Mazda SkyActiv OBD-II calc (FORScan)* spreadsheet (v7.14 used here). Not redistributed here;
  the author's walkthrough is at https://www.youtube.com/watch?v=N9si40XZbcg and an older IC-tab PDF is attached
  in the mazda3revolution As-Built thread: https://www.mazda3revolution.com/threads/change-configuration-explore-different-functions-asbuilt.169393/
- Owner reports the dump table is built from, each linked per row in `docs/unit-model.md` (Sources section). Main ones:
  - mazda3revolution, Mazda6 GJ km/L ↔ L/100km: https://www.mazda3revolution.com/threads/change-info-avg-km-l-to-l-100km.236721/
  - forscan.org (Russian section), CX-5 recipe: https://forum.forscan.org/viewtopic.php?t=11329
  - drive2.ru, JDM ND 2020 experiments: https://www.drive2.ru/l/689735739805552790/
  - drive2.ru, Israeli CX-5 2022: https://www.drive2.ru/l/692968303991209399/
  - fnoji.com, ND RF dump: https://fnoji.com/2021/03/mazda-roadsterrf-nderc-as-built-run/
  - minkara, ND 990S: https://minkara.carview.co.jp/userid/615186/car/3285399/7444118/note.aspx
  - Mobile01, Taiwan Mazda3: https://www.mobile01.com/topicdetail.php?f=276&t=4888385
- ND workshop-manual mirror used for the DTC analysis: https://www.mx5manual.com/ (see `docs/dtc-b1252.md`).
- Adversarial reviews of the plan were run with several LLMs before writing; their objections shaped `docs/safety.md`.

## License

Text and images: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Code in `tools/`: MIT. See `LICENSE`.
