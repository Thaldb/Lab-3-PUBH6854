# Regex and AI-Assisted Cleaning Comparison

## Methods

I cleaned both Lab 3 datasets using two approaches. The first approach used Python functions and regular expressions to recognize the observed formats. The clinical cleaner standardized sample identifiers, patient names, dates, sex values, enrollment sites, glucose units, missing values, and annotated values. The FASTA parser extracted identifiers, organisms, genes, reported lengths, and notes while also assembling and validating each DNA sequence.

For the second approach, I opened a separate Codex task and supplied only the raw files and explicit output requirements. I instructed it not to inspect the regex scripts or outputs. The exact prompts are recorded in `AI_USAGE.md`. I then used `src/compare_outputs.py` to compare corresponding records and fields from the two approaches.

## Agreement and disagreement

The regex and AI approaches agreed on all fields in both datasets. The clinical comparison found 60 of 60 complete record matches. Each clinical field had 100.0% agreement, including dates, sex categories, site names, glucose values, glucose statuses, and notes. The FASTA comparison found eight of eight complete record matches, with 100.0% agreement for the organism, gene, reported length, calculated length, length-match indicator, notes, and assembled sequence.

There were no field-level disagreements. This high agreement was partly expected because both approaches received the same explicit cleaning standards. For example, both were instructed to treat `U`, `unknown`, and blank sex values as `Unknown` and to convert glucose labeled `mmol/L` to `mg/dL` using the same factor. Agreement therefore shows that both methods applied the stated rules consistently, but it does not prove that every rule or source value was correct.

Both approaches handled the deliberately messy formatting. For example, record `s-0003` became `S0003`, its date `11.24.53` became `1953-11-24`, and `MG/DL` became the standard glucose unit. Records `S0012` and `S0056` remained in the table with blank glucose values and a `missing` status. Records `S0032` and `S0043` retained their numeric glucose values after the asterisks were removed, while their status was recorded as `annotated`.

The FASTA approaches also recognized several delimiter and key-name variations. They treated `organism` and `species` as equivalent fields, treated `gene` and `target` as equivalent, and recognized pipes, semicolons, colons, equals signs, spaces, underscores, and hyphens. Both methods assembled multiline sequences before calculating their lengths.

## Edge cases and failure modes

The first important failure mode appears in clinical record `S0006`. Its raw glucose value is `141.2 mmol/L`. Both approaches followed the stated unit and converted it to `2544.2 mg/dL`. The calculation is consistent with the cleaning rule, but the result is implausibly high for blood glucose. The raw generator created values in the same numerical range before assigning either `mg/dL` or `mmol/L`, so a correctly executed conversion can still produce a questionable analytic value. Neither regex nor AI can determine whether the unit label or the number should be corrected without external information.

The date in record `s-0003` is another ambiguity. Its raw value is `11.24.53`. Both methods interpreted it as November 24, 1953 because the cleaning instructions treated two-digit years as dates of birth that could not be in the future relative to 2026. That is a reasonable documented rule for this dataset, but the text `53` does not contain its century. A different dataset or reference year could require a different interpretation.

Records `S0032` and `S0043` contain the values `112.3*` and `223.1*`. Both methods removed the asterisk and marked the records as `annotated`. This preserves the fact that the source included a special marker, but neither method knows what the asterisk means because the raw data contains no definition. It could represent a laboratory flag, a corrected result, or another condition. These values should not be treated as ordinary observations until the source documentation explains the marker.

The FASTA data contains two direct conflicts between header metadata and sequence content. The `sample_003` header reports `length=150bp`, but the assembled sequence contains 157 bases. The `sample_005` header reports 130 bp, but its sequence contains 144 bases. Both approaches detected these conflicts by keeping reported and calculated lengths separate. They reveal the problem but cannot determine whether the header or the sequence is authoritative.

## Time, effort, and trust

The regex approach required more initial work. I had to inspect the variants, design expressions for each format, write separate parsing functions, and test the output. Its advantage is that every transformation is visible, deterministic, and repeatable. When a value changes, I can identify the exact rule responsible for it.

The AI-assisted approach produced the structured tables more quickly after I supplied a detailed prompt. It was especially convenient for interpreting the different FASTA header styles. However, writing a sufficiently precise prompt and validating all outputs still required effort. I did not record exact completion times, so this is a qualitative comparison rather than a timed benchmark.

For a real health or genomic dataset, I would trust the tested regex workflow as the primary reproducible pipeline when the known input formats are limited and stable. I would use AI to identify possible patterns, draft rules, or review unusual records. I would not use either method without validation because deterministic code can consistently apply a bad assumption, while AI can produce plausible-looking output without exposing a repeatable decision rule.

## Graduate addendum: samples × features × metadata

The analytic table in `data/processed/analytic_samples.csv` contains 60 rows, with one row per unique sample. `feature_glucose_mg_dl` is the measurement feature, and `feature_glucose_missing` explicitly records whether that feature is missing. The remaining columns contain the sample identifier and metadata: patient name, date of birth, sex, enrollment site, glucose status, and notes.

The table has consistent identifiers, ISO dates, categories, and nominal glucose units, and its two missing glucose values are documented rather than dropped or converted to zero. Before modeling, I would verify the implausible converted glucose values and determine the meaning of the asterisks; I would also exclude the patient-name identifier, define an analysis reference date before converting birth dates to age, and encode categorical variables appropriately. The table is structurally ready for analysis, but those data-quality and modeling decisions remain unresolved.
