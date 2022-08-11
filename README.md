# Do gamers on Reddit constitute a small world network?

The following repository contains my unprocessed LaTeX, my rendered thesis, my scraped data, and my code for my thesis.

My analysis is promising but flawed due to the difficulty of analyzing a large network data set via NetworkX. However, my results show that my thesis isn't completely bunk which in turn means that repeating my study with more data and more computing power would be worthwhile.

I submitted my thesis in December, 2020. Any updates post-2020 are for maintenance. 

[Adviser: Charles Gomez](https://charliegomez.com/)

# Running the code

Repeating the experiment is as simple as cloning the repository, installing the dependencies via [poetry](https://github.com/python-poetry/poetry), and finally running `main.py` via `poetry`.

`Poetry` is most likely available via your package manager.

For example, for Arch Linux:
```sh
pacman -S python-poetry
```

Gentoo:
```sh
emerge --ask dev-python/poetry-core
```

Or Anaconda:
```sh
conda install poetry
```

Next, clone the repository using `git`:

```sh
git clone https://github.com/joshuamegnauth54/GamerDistributionThesis2020
```

Install dependencies using `poetry`:
```sh
poetry install
```

And finally run the code:
```sh
poetry run python joshnettools/main.py
```

# Licenses
My code is licensed under `GPL-3.0-or-later`.

Any documentation or writing (i.e. my thesis) is licensed under `CC-BY-4.0`.

Copies of these licenses are provided in [LICENSE.code](LICENSE.code) and [LICENSE.thesis](LICENSE.thesis).

`SPDX-License-Identifier: CC-BY-4.0 AND GPL-3.0-or-later`
