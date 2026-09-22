"""Compare regex-cleaned and AI-cleaned Lab 3 outputs."""

import csv
from pathlib import Path


DATASETS = [
    {
        "name": "samples",
        "key": "sample_id",
        "regex_path": Path(
            "data/processed/regex/clean_samples_regex.csv"
        ),
        "ai_path": Path(
            "data/processed/ai/clean_samples_ai.csv"
        ),
        "detail_path": Path(
            "data/processed/comparison/samples_comparison.csv"
        ),
    },
    {
        "name": "sequences",
        "key": "sample_id",
        "regex_path": Path(
            "data/processed/regex/clean_sequences_regex.csv"
        ),
        "ai_path": Path(
            "data/processed/ai/clean_sequences_ai.csv"
        ),
        "detail_path": Path(
            "data/processed/comparison/sequences_comparison.csv"
        ),
    },
]

SUMMARY_PATH = Path(
    "data/processed/comparison/agreement_summary.csv"
)


def read_table(path, key):
    """Read a CSV and index its rows by a unique key."""
    with path.open(newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        rows = list(reader)
        fieldnames = reader.fieldnames

    indexed = {row[key]: row for row in rows}

    if len(indexed) != len(rows):
        raise ValueError(f"Duplicate {key} values in {path}")

    return indexed, fieldnames


def compare_dataset(config):
    """Compare corresponding records and fields in one dataset."""
    regex_rows, regex_fields = read_table(
        config["regex_path"],
        config["key"],
    )
    ai_rows, ai_fields = read_table(
        config["ai_path"],
        config["key"],
    )

    if regex_fields != ai_fields:
        raise ValueError(
            f"Column mismatch for {config['name']}: "
            f"{regex_fields} versus {ai_fields}"
        )

    if set(regex_rows) != set(ai_rows):
        raise ValueError(
            f"Record ID mismatch for {config['name']}"
        )

    compared_fields = [
        field for field in regex_fields
        if field != config["key"]
    ]

    field_match_counts = {
        field: 0 for field in compared_fields
    }

    detail_rows = []
    exact_record_matches = 0
    disagreeing_cells = 0

    for record_id in sorted(regex_rows):
        regex_row = regex_rows[record_id]
        ai_row = ai_rows[record_id]
        differing_fields = []

        for field in compared_fields:
            if regex_row[field] == ai_row[field]:
                field_match_counts[field] += 1
            else:
                differing_fields.append(field)
                disagreeing_cells += 1

        all_fields_match = not differing_fields

        if all_fields_match:
            exact_record_matches += 1

        detail_rows.append(
            {
                config["key"]: record_id,
                "matching_fields": (
                    len(compared_fields) - len(differing_fields)
                ),
                "total_fields": len(compared_fields),
                "all_fields_match": str(all_fields_match),
                "differing_fields": ";".join(differing_fields),
            }
        )

    config["detail_path"].parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with config["detail_path"].open(
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                config["key"],
                "matching_fields",
                "total_fields",
                "all_fields_match",
                "differing_fields",
            ],
        )
        writer.writeheader()
        writer.writerows(detail_rows)

    total_records = len(regex_rows)
    summary_rows = []

    for field in compared_fields:
        matches = field_match_counts[field]
        summary_rows.append(
            {
                "dataset": config["name"],
                "field": field,
                "matches": matches,
                "total": total_records,
                "agreement_percent": (
                    f"{100 * matches / total_records:.1f}"
                ),
            }
        )

    summary_rows.append(
        {
            "dataset": config["name"],
            "field": "complete_record",
            "matches": exact_record_matches,
            "total": total_records,
            "agreement_percent": (
                f"{100 * exact_record_matches / total_records:.1f}"
            ),
        }
    )

    print(
        f"{config['name']}: "
        f"{exact_record_matches}/{total_records} exact record matches; "
        f"{disagreeing_cells} disagreeing cells"
    )

    return summary_rows


def main():
    summary_rows = []

    for config in DATASETS:
        summary_rows.extend(compare_dataset(config))

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SUMMARY_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "dataset",
                "field",
                "matches",
                "total",
                "agreement_percent",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Wrote agreement summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
