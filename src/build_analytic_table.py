"""Build the graduate samples × features × metadata table."""

import argparse
import csv
from pathlib import Path


OUTPUT_FIELDS = [
    "sample_id",
    "feature_glucose_mg_dl",
    "feature_glucose_missing",
    "metadata_patient_name",
    "metadata_dob",
    "metadata_sex",
    "metadata_enrollment_site",
    "metadata_glucose_status",
    "metadata_notes",
]


def transform_row(row):
    """Separate analytic features from sample metadata."""
    glucose = row["glucose_mg_dl"].strip()
    glucose_missing = "1" if glucose == "" else "0"

    return {
        "sample_id": row["sample_id"],
        "feature_glucose_mg_dl": glucose,
        "feature_glucose_missing": glucose_missing,
        "metadata_patient_name": row["patient_name"],
        "metadata_dob": row["dob"],
        "metadata_sex": row["sex"],
        "metadata_enrollment_site": row["enrollment_site"],
        "metadata_glucose_status": row["glucose_status"],
        "metadata_notes": row["notes"],
    }


def build_table(input_path, output_path):
    """Read the cleaned records and write the analytic table."""
    with input_path.open(newline="", encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))

    sample_ids = [row["sample_id"] for row in rows]

    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Sample IDs are not unique")

    analytic_rows = [transform_row(row) for row in rows]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=OUTPUT_FIELDS,
        )
        writer.writeheader()
        writer.writerows(analytic_rows)

    missing_count = sum(
        row["feature_glucose_missing"] == "1"
        for row in analytic_rows
    )

    print(f"Wrote {len(analytic_rows)} samples to {output_path}")
    print(f"Samples with missing glucose: {missing_count}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Build the Lab 3 analytic sample table."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(
            "data/processed/regex/clean_samples_regex.csv"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/processed/analytic_samples.csv"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    build_table(args.input, args.output)


if __name__ == "__main__":
    main()
