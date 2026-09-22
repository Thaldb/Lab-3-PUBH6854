# AI Usage Disclosure

## Tool used

I used OpenAI Codex in the Codex desktop app on September 21–22, 2026. I used it as an interactive guide for planning the repository, understanding the regular expressions, checking output files, and conducting a separate AI-assisted cleaning pass.

I reviewed the generated files, ran the scripts, checked record counts, and compared specific records rather than accepting the output without verification.

## Regex-cleaning assistance

Codex helped me identify the format variations in the raw files and understand regex patterns for:

- Sample identifiers
- Four date formats
- Sex and site categories
- Numeric glucose values with optional asterisks
- FASTA identifiers, organisms, genes, lengths, and notes
- Multiline DNA sequences

I entered and ran the Python scripts and inspected their outputs.

## AI-assisted clinical extraction

I started a separate Codex task so the AI-assisted pass would not inherit the regex implementation or its output. I used this exact prompt:

```text
Use only data/raw/messy_samples.csv. Do not inspect anything in src/ or data/processed/regex because this must be an independent generative-AI cleaning pass.

Directly interpret and clean all 60 clinical records. Save the result as data/processed/ai/clean_samples_ai.csv.

Use exactly these columns:
sample_id,patient_name,dob,sex,enrollment_site,glucose_mg_dl,glucose_status,notes

Apply these standards:
- Normalize sample IDs to S followed by four digits.
- Use title case for patient names.
- Convert dates to YYYY-MM-DD. Interpret the two-digit years as dates of birth that are not in the future relative to 2026.
- Standardize sex as Male, Female, or Unknown. Treat U, unknown, and blank as Unknown.
- Standardize sites as Site A, Site B, or Site C.
- Standardize glucose to mg/dL. Treat all case variants of mg/dL as equivalent. Convert values labeled mmol/L to mg/dL by multiplying by 18.0182 and round to one decimal place.
- For N/A glucose, leave glucose_mg_dl blank and set glucose_status to missing.
- Remove a trailing asterisk from a numeric glucose value and set glucose_status to annotated.
- Set all other numeric glucose records to reported.
- Preserve the existing notes text.
- Write a plain CSV file with one header row and exactly 60 data rows.
- Do not write a regex parser or copy the regex-derived output. This file should represent your direct AI interpretation of the raw records.
```

The resulting file was saved as:

```text
data/processed/ai/clean_samples_ai.csv
```

## AI-assisted FASTA extraction

In the same independent task, I used this exact follow-up prompt:

```text
Now use only data/raw/messy_sequences.fasta. Do not inspect src/ or data/processed/regex.

Directly interpret all eight FASTA records and save the structured result as data/processed/ai/clean_sequences_ai.csv.

Use exactly these columns:
sample_id,organism,gene,reported_length,sequence_length,length_match,notes,sequence

Apply these standards:
- Normalize the numeric identifier in each header to sample_001 through sample_008.
- Standardize all organism spelling variants to Homo sapiens.
- Standardize gene names as BRCA1, TP53, or EGFR.
- Put a numeric header-reported sequence length in reported_length. Leave it blank if no numeric reported length is present, including len:NA.
- Join multiline sequence text into one uppercase uninterrupted DNA string.
- Calculate sequence_length from the assembled sequence.
- Set length_match to True or False when reported_length is available. Leave it blank otherwise.
- Extract an explicit note when present; otherwise leave notes blank.
- Write a plain CSV file with one header row and exactly eight data rows.
- Do not write a regex parser or copy the regex-derived output. This file should represent your direct AI interpretation of the raw FASTA records.
```

The resulting file was saved as:

```text
data/processed/ai/clean_sequences_ai.csv
```

## Verification performed

I verified that:

- The regex and AI clinical tables each contain 60 records.
- The regex and AI FASTA tables each contain eight records.
- The output tables use the requested columns.
- Clinical sample IDs and FASTA IDs follow their standardized formats.
- Calculated FASTA sequence lengths equal the lengths of the assembled sequence strings.
- Missing and asterisk-annotated glucose records were retained rather than silently removed.
- Reported and calculated FASTA lengths remain separate fields.

The record-level agreement and failure modes are discussed in `writeup/comparison.md`.
