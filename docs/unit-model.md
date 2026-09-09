# 720-01-01 dumps and the region × unit-field model

All values are IC As-Built line `720-01-01` as shown by FORScan: `B0B1 B2B3 B4CS`
(five data bytes, then the line checksum). "Region" is B0 bits 3..1; "B3 field" is B3 bits 7..6.

## Byte layout (SergSlim v7.14 sheet, IC tab, plus dump comparison)

| Byte | Bit | Meaning |
|---|---|---|
| B0 | b7 | Rear seat-belt warning |
| B0 | b6 | Temperature unit (0 = °C, 1 = °F) |
| B0 | b5 | fixed 1 |
| B0 | b4 | unknown |
| B0 | b3 b2 b1 | Region code (table below) |
| B0 | b0 | TPMS |
| B1 | b7 | 1 = America / Singapore |
| B1 | b6..b0 | model/engine flags (washer warning, CX-4, 3MZ, 2.2D, 4WD...) |
| B2 | b7 | fuel-tank-level related (CX-5/9) |
| B2 | b6 b5 | seat-belt beepers |
| B2 | b4 | i-Stop |
| B2 | b3 | speed alarm |
| B2 | b0 | ambient-temperature warning |
| B3 | b7 | unknown in the sheet – behaves as the high bit of the fuel-unit field |
| B3 | b6 | "Fuel Consumption Units: 0 = L/100 km, 1 = MPG" (sheet comment: tested on Mazda6 GJ / CX-5 KE with TomTom) |
| B3 | b5 | fixed 1 |
| B3 | b4 | Parking brake (0 mechanical, 1 EPB) |
| B3 | b3..b0 | fixed 0,1,1,0 |
| B5 | | line checksum, see `tools/asbuilt_line_checksum.py` |

Region code, B0 low nibble (b3 b2 b1 b0, where b0 is TPMS):

| b3b2b1 | Nibble | Market (sheet label) |
|---|---|---|
| 000 | 0/1 | Japan / UK |
| 001 | 2/3 | Europe |
| 010 | 4/5 | USA |
| 011 | 6/7 | Canada (also Mexican-market cars) |
| 100 | 8/9 | Australia |
| 101 | A/B | South America / Asia |
| 110 | C/D | China |
| 111 | E/F | Saudi Arabia |

## Collected dumps

| Car / market | Displayed unit | 720-01-01 | Region | B3 (b7b6) | Notes / source |
|---|---|---|---|---|---|
| JDM ND Roadster 2020 | km/L | `6000 22E6 8011` | 000 JPN | E6 (11) | factory; drive2.ru (kirixon) |
| same, region set to EU | still km/L (mpg only when CMU language = English) | `6200 22E6 8013` | 001 EU | E6 (11) | region alone does not change the unit |
| same, EU + b6 = 0 | L/100km | `6200 22A6 80D3` | 001 EU | A6 (10) | photo in the same thread |
| JDM ND RF (NDERC) | km/L | `6001 72E6 8062` | 000 | E6 (11) | factory; fnoji.com |
| JDM ND 990S | km/L restored in EU region by setting b7b6 = 11 | (no hex) | 001 EU | 00 → 11 | minkara (berumiya); ND1/ND2 in JPN region show km/L regardless of B3 |
| Mazda6 GJ, EU | km/L → L/100km | `A323 73E6 80C8` → `A323 73A6 8088` | 001 EU | E6 → A6 | mazda3revolution (apih) |
| Israel CX-5 KF 2022, CMU 74.00.324 | km/L → L/100km by changing B3 only | (no hex) | ? | ? | drive2.ru; Mazda Connect generation |
| Russia CX-5 2019/2022/2025 | km/L → L/100km | (no hex) | → 001 | b6 = 0 | forscan.org t=11329 |
| US CX-5 2015 | mpg → L/100km | `65A0 6066 8074` → `A5A0 6006 8054` | 010 US | 66 (01) → 06 (00) | forscan.org t=17339 |
| JDM CX-5 KF 2017 | km/L | `2023 72E6 8044` | 000 | E6 (11) | mazda3revolution |
| JDM CX-3 | km/L | `2004 72F6 8035` | 000 | F6 (11) | mazda3revolution |
| JDM Axela 2014 | km/L | `2000 72E6 8021` | 000 | E6 (11) | mazda3revolution |
| Thailand Mazda3 2014 / Mazda2 2015 (×2) | L/100km | `2A06 6226 8061`, `2A80 7226 80EB`, `2A01 7226 806C` | 101 Asia | 26 (00) | still L/100km after region → AUS |
| Vietnam Mazda3 2015, Philippines Mazda3 2016 | L/100km | `2A00 7226 806B` | 101 | 26 | |
| Taiwan Mazda3 BM 2016 | L/100km | `2B00 7226 806C` | 101 | 26 (00) | Mobile01; region 101 + `26` = L/100km |
| EU Mazda3 BM, Russia CX-5 2018, CIS CX-5 | L/100km | `A321 7B26 800E`, `2361 7B26 80CE`, `A321 7926 800C` | 001 | 26 | factory |
| China / Asia CX-5 | L/100km | `A320 6B26 80FD`, `2C28 7226 8095` | 001 / 110 | 26 | mazda3revolution |
| Saudi Mazda6 2022 | km/L, English cluster UI | (no hex) | 111? | ? | YouTube walk-through |
| JDM CX-5 in NZ with English CMU firmware | cluster km/L, CMU screen L/100km | (no hex) | 000 | E6 | skykiwi forum; cluster unit is independent of CMU language |
| **This car: Mexico-market ND2 2019** | L/100km | `27E1 E226 80B9` | **011 Canada** | 26 (00) | factory |
| **This car, working** | **km/L** | **`2BE1 E2E6 807D`** | **101** | **E6 (11)** | 2026-09-09 |

Not found despite searching in English, Russian, Japanese, Spanish, Portuguese, Thai, Chinese,
Arabic and Hebrew sources: a factory `720-01-01` hex from a Gulf, Israeli, Latin-American or
South-East-Asian km/L car. Those would confirm or refine the model below.

## Model that fits every row

1. **b7b6 = `00` → L/100km** regardless of region.
2. **b7b6 = `01` (`66`) → mpg** (US cars).
3. **b7b6 = `11` (`E6`/`F6`) → "distance per fuel" mode.** Within it, the region table decides
   between km/L and mpg. Observed:
   - JPN (000): km/L.
   - EU (001): km/L with Russian/Japanese CMU language, mpg with English (UK mapping).
   - Gulf (111) and Israel: km/L with English UI.
   - **Canada (011): no change from L/100km** (this car, twice, write verified).
   - **South America / Asia (101): km/L** (this car).
4. Region code alone never switched the unit.
5. Exception: ND1/ND2 JDM clusters force km/L in JPN region regardless of B3.
6. The cluster unit does not depend on the CMU language; the CMU's own fuel-economy screen follows the cluster.
7. `10` (`A6`) has only been observed as a result of clearing b6 on a JDM car; it displayed L/100km.

Untested: region 101 with `66` (b6 only). Untested: whether the sheet's fixed bits in B3 matter.
The sheet's note that b6 applies to TomTom-era head units is contradicted by the Israeli CX-5 2022
and JDM ND 2020 reports, both Mazda Connect.

## Things that do not work or were rejected

- `27E1 E22E 80C1` (B3 b3): an early forum post says "bit 3"; the attached sheet capture in the
  same post labels b3 as a fixed value and b6 as the unit bit. Do not write it.
- Changing the CMU language: the cluster unit is set by the IC, not by the CMU.
- Old-CMU Settings → System has no km/L option (newer Mazda Connect on 2019+ Mazda3 BP / CX-30 does).
- Hidden cluster service mode (trip-reset held + IGN ON, codes 50/60) is documented for 2010–2013
  Mazda3 clusters; nothing equivalent was confirmed for SkyActiv/ND clusters.
