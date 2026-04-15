# py-boletus

Library and scripts for checking Bonoloto combinations against historical draws.

## What Is Bonoloto?

Bonoloto is a Spanish lotto game operated by Loterias y Apuestas del Estado. A standard bet is based on choosing 6 numbers from 1 to 49, and draws are held every day of the week. In practice, it sits in the family of frequent, low-ticket, national number-draw games rather than the very large multi-country jackpot games.

Official results page:

- https://www.loteriasyapuestas.es/es/resultados/bonoloto

Rough international references:

- United States: there is no exact national equivalent. The closest family is state-run lotto games such as California Fantasy 5 or New York Lotto, while Powerball and Mega Millions are less similar because they use extra balls and larger matrices.
- United Kingdom: the closest mainstream reference is National Lottery Lotto, another pick-numbers draw game, although it uses 6 numbers from 1 to 59 and runs on Wednesdays and Saturdays.
- Sweden: Svenska Spel Lotto is a close conceptual match, but it uses a different structure with 7 numbers from 35 and additional side mechanics such as Joker.
- Europe: EuroMillions is probably the best-known cross-border cousin, but it is not the closest mechanical equivalent to Bonoloto because it uses 5 numbers from 50 plus 2 Lucky Stars and runs twice a week.

## Why Bonoloto Is Interesting

Bonoloto is often compared with its better-known sibling, La Primitiva. La Primitiva usually offers larger headline prizes, but the game structure is different at the very top end.

In Bonoloto, the top category is simply `6 matches`, and that is the category that receives the main rollover. In La Primitiva, the highest tier is an `Especial` category that requires `6 matches + Reintegro`, above the regular `1st category` of `6 matches`. So a player interested specifically in the simplest possible path to the top rollover may find Bonoloto easier to reason about.

Bonoloto is also cheaper per bet. The official ticket price is `€0.50 per bet`, with a minimum ticket spend of `€1` if the ticket only participates in a single draw. La Primitiva costs `€1 per bet`. Because of that, Bonoloto can be viewed as a very efficient low-cost / upside game within the Spanish lottery family, although "best cost/benefit" is still an inference rather than an official metric.

From a combinatorial point of view, both Bonoloto and La Primitiva are based on choosing `6 numbers from 49`. That means the search space is:

```text
C(49, 6) = 13,983,816
```

So there are `13,983,816` distinct simple combinations. That combinatorial scale is exactly why filtering, historical comparison, wheeling, and coverage analysis are interesting for projects like this one.

## Requirements

- `mise` to pin project tooling
- `uv` to create the environment and resolve dependencies

This repository pins:

- `python 3.14.4`
- the latest available `uv`

## Installation

```bash
mise install
uv sync
```

This creates `.venv/` and installs the dependencies declared in [pyproject.toml](pyproject.toml).

## Quick Start

Run the included scripts:

```bash
uv run python update_data.py
uv run python test_data.py
uv run python reducida_test.py
uv run python oh_fortuna.py
```

If you prefer activating the virtual environment first:

```bash
source .venv/bin/activate
python oh_fortuna.py
```

## Data Format

Historical draws CSV:

```text
DATE,N1,N2,N3,N4,N5,N6,NC,R
21/08/2021,02,14,15,19,21,31,30,3
20/08/2021,02,14,15,45,46,47,48,0
```

Combinations to test CSV:

```text
2,14,15,19,21,31
2,12,15,19,21,31
```

Relevant output columns:

- `draw`: evaluated combination, serialized as `N1-N2-N3-N4-N5-N6`
- `max_success`: number of matches against the 6 main numbers
- `comp`: `1` if the complementary number (`NC`) is part of the tested draw, `0` otherwise

## Library API

The main API lives in [lib/scrutiny.py](lib/scrutiny.py).

### `draw_to_str(draw, sep='-')`

Converts a combination into a readable string.

Example:

```python
from lib.scrutiny import draw_to_str

draw_to_str([2, 14, 15, 19, 21, 31])
# "2-14-15-19-21-31"
```

### `check_draw(df_historical, draw, sort=True)`

Evaluates a single combination against a historical `DataFrame` and returns a copy of the historical data with these computed columns:

- `draw`
- `max_success`
- `comp`

Parameters:

- `df_historical`: `pandas.DataFrame` with columns `DATE,N1,N2,N3,N4,N5,N6,NC,R`
- `draw`: iterable with 6 numbers
- `sort`: present in the function signature, but currently does not change behavior

Example:

```python
import pandas as pd
from lib.scrutiny import check_draw

historical = pd.read_csv("data/ES-bonoloto.csv", parse_dates=["DATE"], dayfirst=True)
result = check_draw(historical, [2, 14, 15, 19, 21, 31])

print(result[["DATE", "draw", "max_success", "comp"]].head())
```

### `scrutiny(f_test, f_historical, f_out, fmt='csv', success_filter=3, order_date_only=False, verbose=True)`

This is the main library function. It reads a file with combinations, compares them against the historical dataset, sorts the results, writes them to disk, and returns a `DataFrame`.

Parameters:

- `f_test`: path to the CSV file containing the combinations to evaluate
- `f_historical`: path to the CSV file containing historical draws
- `f_out`: output path template. The code formats it with `f_out.format(max_num_success, 'boletus', 'M')`
- `fmt`: legacy parameter; output is currently always written as CSV
- `success_filter`: legacy parameter; the current implementation filters with `max_success > 2`
- `order_date_only`: if `True`, sort only by descending date
- `verbose`: enables informational logging

Return value:

- `pandas.DataFrame` containing the matching results

Minimal example:

```python
from lib.scrutiny import scrutiny

df = scrutiny(
    f_test="./test/oh_fortuna.csv",
    f_historical="./data/ES-bonoloto.csv",
    f_out="./out/{0}_{1}_fortuna_{2}.csv",
    fmt="csv",
    success_filter=3,
    order_date_only=False,
    verbose=True,
)

print(df.head())
```

Example using custom files:

```python
from lib.scrutiny import scrutiny

df = scrutiny(
    f_test="./my_combinations.csv",
    f_historical="./data/ES-bonoloto.csv",
    f_out="./out/{0}_{1}_my_combinations_{2}.csv",
)
```

## Auxiliary Configuration

[lib/config.py](lib/config.py) exposes a minimal global configuration object:

- `config.verbose(True | False)`
- `config.debug(True | False)`

Example:

```python
from lib import config

config.verbose(True)
config.debug(False)
```

The internal logger lives in [lib/logger.py](lib/logger.py).

## Included Scripts

- [update_data.py](update_data.py): downloads new historical rows from Google Sheets and updates `data/ES-bonoloto.csv`
- [test_data.py](test_data.py): minimal validation example using a small dataset
- [reducida_test.py](reducida_test.py): runs the sample from `test/reducida_test.csv`
- [oh_fortuna.py](oh_fortuna.py): runs the sample from `test/oh_fortuna.csv`

## Troubleshooting

### `mise install` fails with `Python installation is missing a lib directory`

This error appears with older versions of `mise` when installing some precompiled Python 3.14 builds on macOS.

Update `mise` and try again:

```bash
brew upgrade mise
mise --version
mise install
uv sync
```

If your `mise` version is still older than `v2026.3.10`, update it before debugging anything else.

### `ModuleNotFoundError` after `uv sync`

`uv sync` installs dependencies into `.venv/`. If you run `python3 script.py`, you may still be using the system Python instead of the project's virtual environment.

Use one of these two options:

```bash
uv run python oh_fortuna.py
```

```bash
source .venv/bin/activate
python oh_fortuna.py
```
