# Lactate, Memory & Aging in Fruit Flies

Final project for **Introduction to Programming (MAT2007)**, Maastricht University.
Author: Sara Ionescu (i6375189)

This project re-analyses a public dataset from Frame et al. (2023) to find out how changing
the enzyme lactate dehydrogenase (dLdh) in the neurons of fruit flies affects their long-term
memory as they age. The analysis is written in Python and produces one figure plus a text
file with all numerical results.

## Research question

Does increasing or decreasing lactate dehydrogenase (dLdh) in the neurons of fruit flies
change their long-term memory as they age, and if so, by how much and from which age on?

## Dataset

- **Source:** Frame et al. (2023), *Aging* 15(4), 947–981. Data published on Dryad:
  [https://doi.org/10.5061/dryad.2v6wwpzsb](https://doi.org/10.5061/dryad.2v6wwpzsb)
- **File used:** `Figure2B_2C.xlsx` (the Dryad dataset contains 15 Excel files, one per figure
  of the paper; only this one is used)
  - sheet `Courtship Indexes`: courtship index of every fly (input of the analysis)
  - sheet `Memory Indexes`: the authors' memory indexes (only used to check the results)
- **Content:** 1,333 male flies, 3 genotypes (control, dLdh knockdown, dLdh overexpression)
  × 3 ages (7, 14, 21 days) × naive / trained.
- **Cleaning:** none needed. The only processing is removing the empty cells at the end of
  shorter columns, which the script does automatically (`dropna()`).

The data file is included in this repository. To download it yourself, go to the Dryad link
above, download and unzip the dataset, and place the folder as shown below.

## Repository structure

```
lactate-memory-aging/
├── README.md                  <- this file
├── final_report.pdf           <- 2-page report (LaTeX, Overleaf)
└── script/
    ├── script_plot1.py        <- the analysis code
    ├── Plot1_memory.png       <- output: figure (created by the script)
    ├── Plot1_memory.pdf       <- output: figure, vector version (created by the script)
    ├── results_plot1.txt      <- output: all numerical results (created by the script)
    └── data/
        └── doi_10_5061_dryad_2v6wwpzsb__v20230227/
            └── Figure2B_2C.xlsx
```

## Requirements

- Python 3 (tested with Python 3.14 on Windows, in Visual Studio Code)
- Python packages:

| Package | Used for |
|---|---|
| `numpy` | calculations, uncertainties, bootstrap |
| `pandas` | reading the Excel file |
| `openpyxl` | needed by pandas to open `.xlsx` files |
| `scipy` | statistical tests (Kruskal–Wallis, normal distribution) |
| `matplotlib` | the figure |

Install them with:

```bash
pip install numpy pandas openpyxl scipy matplotlib
```

On Windows, if `pip` is not found, use:

```bash
py -m pip install numpy pandas openpyxl scipy matplotlib
```

## How to run

1. Download or clone this repository.
2. Make sure `Figure2B_2C.xlsx` is in `script/data/doi_10_5061_dryad_2v6wwpzsb__v20230227/`.
3. Run the script from the `script` folder:

```bash
cd script
python script_plot1.py
```

On Windows you can also use `py script_plot1.py`, or open the file in VS Code and click the
▶ Run button.

The script takes a few seconds (10,000 bootstrap resamples). A window with the plot opens;
**close the window** to let the script finish.

## What the script does

1. Reads the courtship index of every fly from the Excel file.
2. Calculates a **memory index** for every trained fly
   (MI = 1 − CI_trained / mean CI_naive) and checks it against the authors' values.
3. Calculates the **mean memory index ± uncertainty** of each group (standard error and
   the error of the naive mean, added in quadrature).
4. Uses a **bootstrap** (10,000 resamples) to get the 95% range of "memory as % of control".
5. Runs a **Kruskal–Wallis test** per age, **Dunn's test** (each mutant vs control,
   Bonferroni-corrected) and calculates **Cliff's delta** (effect size).
6. Draws the figure and saves all results.

## Output

The script creates these files in the `script` folder:

- `Plot1_memory.png`: the figure (for the presentation)
- `Plot1_memory.pdf`: the same figure in vector format (for the LaTeX report)
- `results_plot1.txt`: all numbers (means, errors, test results, percentages)

The random seed is fixed (`np.random.seed(2023)`), so running the script again gives exactly
the same numbers.

## Reference

A. K. Frame et al., "Aging and memory are altered by genetically manipulating lactate
dehydrogenase in the neurons or glia of flies", *Aging* 15(4), 947–981 (2023).
[doi:10.18632/aging.204565](https://doi.org/10.18632/aging.204565)
