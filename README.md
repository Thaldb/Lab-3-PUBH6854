# PUBH 6854 Lab 3: Parsing Messy Health and Genomic Data

## Project overview

This repository completes the graduate version of Lab 3. It compares regular-expression-based cleaning with generative-AI-assisted extraction for two synthetic datasets:

- Clinical sample records with inconsistent dates, categories, site names, units, missing values, and annotations
- DNA sequences with inconsistent FASTA header formats

The project also transforms the cleaned clinical records into a samples × features × metadata table for analysis.

## Data

The raw data comes from the PUBH 6854 course repository:

https://github.com/gwcbi/applied-computing-HDS/tree/main/data/raw/lab3-messy-data

The data is synthetic and contains no real protected health information. The course generator uses fixed random seeds, making the files reproducible.

The raw inputs are:

- `data/raw/messy_samples.csv`: 60 synthetic clinical records
- `data/raw/messy_sequences.fasta`: 8 synthetic DNA sequences
- `data/raw/generate_data.py`: course-provided deterministic generator

The raw files are preserved unchanged. Cleaning scripts write separate files under `data/processed/`.

## Repository structure

```text
.
├── README.md
├── AI_USAGE.md
├── environment.yml
├── data/
│   ├── raw/
│   │   ├── generate_data.py
│   │   ├── messy_samples.csv
│   │   └── messy_sequences.fasta
│   └── processed/
│       ├── ai/
│       │   ├── clean_samples_ai.csv
│       │   └── clean_sequences_ai.csv
│       ├── comparison/
│       │   ├── agreement_summary.csv
│       │   ├── samples_comparison.csv
│       │   └── sequences_comparison.csv
│       ├── regex/
│       │   ├── clean_samples_regex.csv
│       │   └── clean_sequences_regex.csv
│       └── analytic_samples.csv
├── src/
│   ├── build_analytic_table.py
│   ├── clean_samples_regex.py
│   ├── clean_sequences_regex.py
│   └── compare_outputs.py
└── writeup/
    └── comparison.md
```

## Requirements and setup

The scripts use only the Python standard library. Create the Conda environment from the repository root:

```bash
conda env create -f environment.yml
conda activate pubh6854-lab3
```

## Run the regex cleaners

Run all commands from the repository root.

Clean the clinical sample data:

```bash
python src/clean_samples_regex.py
```

Input:

```text
data/raw/messy_samples.csv
```

Output:

```text
data/processed/regex/clean_samples_regex.csv
```

The script should report:

```text
Wrote 60 records to data/processed/regex/clean_samples_regex.csv
```

Parse the FASTA data:

```bash
python src/clean_sequences_regex.py
```

Input:

```text
data/raw/messy_sequences.fasta
```

Output:

```text
data/processed/regex/clean_sequences_regex.csv
```

The script should report:

```text
Wrote 8 records to data/processed/regex/clean_sequences_regex.csv
```

## Cleaning rules

The clinical cleaner:

- Normalizes sample identifiers to `S####`
- Converts dates to ISO `YYYY-MM-DD`
- Standardizes sex as `Male`, `Female`, or `Unknown`
- Standardizes sites as `Site A`, `Site B`, or `Site C`
- Standardizes glucose to `mg/dL`
- Converts glucose labeled `mmol/L` using a factor of 18.0182
- Preserves missing and asterisk-annotated results with explicit statuses
- Retains notes

The glucose conversion is consistent with the NIDDK conversion of `mg/dL × 0.0555 = mmol/L`:

https://www.niddk.nih.gov/-/media/Files/Strategic-Plans/Diabetes-in-America-3rd-Edition/DIA_Conversions.pdf

The FASTA cleaner:

- Normalizes identifiers to `sample_###`
- Standardizes organism and gene names
- Extracts reported lengths and notes
- Joins multiline DNA sequences
- Calculates sequence lengths
- Compares reported lengths with calculated lengths
- Validates DNA characters

## AI-assisted extraction

The AI-assisted outputs are:

```text
data/processed/ai/clean_samples_ai.csv
data/processed/ai/clean_sequences_ai.csv
```

These were created in a separate Codex task using only the raw files. The exact prompts, output requirements, and verification steps are documented in [`AI_USAGE.md`](AI_USAGE.md).

Because generative-AI output may vary between runs, the resulting tables are committed to this repository. The prompts provide the procedure for repeating the extraction.

## Compare the outputs

Run:

```bash
python src/compare_outputs.py
```

This creates:

```text
data/processed/comparison/agreement_summary.csv
data/processed/comparison/samples_comparison.csv
data/processed/comparison/sequences_comparison.csv
```

The current outputs show:

```text
samples: 60/60 exact record matches; 0 disagreeing cells
sequences: 8/8 exact record matches; 0 disagreeing cells
```

The two methods had 100% field-level agreement. This agreement shows consistent application of the specified rules, but it does not establish that ambiguous source values are correct.

## Build the analytic table

Run:

```bash
python src/build_analytic_table.py
```

This creates:

```text
data/processed/analytic_samples.csv
```

The table contains one row for each of 60 samples. It separates the glucose feature from sample metadata and includes an explicit missingness indicator. Two samples have missing glucose values, and neither was silently dropped or converted to zero.

## Main findings

Both methods handled the observed formatting variants and produced identical structured tables. Important source-data issues remain:

- `S0006` converts to an implausible `2544.2 mg/dL` because the source labels `141.2` as `mmol/L`.
- The century in `s-0003` value `11.24.53` is not explicit.
- The asterisks in `S0032` and `S0043` are not defined by the source.
- `sample_003` reports 150 bp but contains 157 bases.
- `sample_005` reports 130 bp but contains 144 bases.

The full comparison, failure-mode analysis, trust assessment, and graduate analytic-readiness discussion are in [`writeup/comparison.md`](writeup/comparison.md).

## Reproduce the complete workflow

After activating the environment, run:

```bash
python src/clean_samples_regex.py
python src/clean_sequences_regex.py
python src/compare_outputs.py
python src/build_analytic_table.py
```

All commands should complete without errors and reproduce the committed regex, comparison, and analytic tables.

## AI assistance

Generative AI assistance and the exact extraction prompts are documented in [`AI_USAGE.md`](AI_USAGE.md).
