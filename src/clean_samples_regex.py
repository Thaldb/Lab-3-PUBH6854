"""Clean the messy clinical sample records using explicit regex rules."""

import argparse
import csv
import re
from datetime import datetime, date
from pathlib import Path


MMOL_L_TO_MG_DL = 18.0182

OUTPUT_FIELDS = [
    "sample_id",
    "patient_name",
    "dob",
    "sex",
    "enrollment_site",
    "glucose_mg_dl",
    "glucose_status",
    "notes",
]


def clean_sample_id(raw_value):
    """Convert S0001 and s-0001 forms to S0001."""
    match = re.fullmatch(r"[Ss]-?(\d{4})", raw_value.strip())

    if not match:
        raise ValueError(f"Unrecognized sample ID: {raw_value!r}")

    return f"S{int(match.group(1)):04d}"


def clean_date(raw_value):
    """Convert the four observed date formats to YYYY-MM-DD."""
    value = raw_value.strip()

    patterns = [
        (r"\d{2}/\d{2}/\d{4}", "%m/%d/%Y"),
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
        (r"\d{2}-[A-Za-z]{3}-\d{4}", "%d-%b-%Y"),
    ]

    for regex, date_format in patterns:
        if re.fullmatch(regex, value):
            return datetime.strptime(value, date_format).date().isoformat()

    # Handle MM.DD.YY separately so the century rule is explicit.
    match = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", value)

    if match:
        month, day, two_digit_year = map(int, match.groups())

        # The synthetic records were generated in 2026 and contain no
        # future dates. Years 00–26 are interpreted as 2000–2026;
        # larger values are interpreted as 1900–1999.
        year = (
            2000 + two_digit_year
            if two_digit_year <= 26
            else 1900 + two_digit_year
        )

        return date(year, month, day).isoformat()

    raise ValueError(f"Unrecognized date: {raw_value!r}")


def clean_sex(raw_value):
    """Standardize sex coding to Male, Female, or Unknown."""
    value = raw_value.strip().lower()

    if re.fullmatch(r"m|male", value):
        return "Male"

    if re.fullmatch(r"f|female", value):
        return "Female"

    if re.fullmatch(r"u|unknown|", value):
        return "Unknown"

    raise ValueError(f"Unrecognized sex value: {raw_value!r}")


def clean_site(raw_value):
    """Standardize site spelling, punctuation, spacing, and case."""
    compact = re.sub(r"[\s_-]+", "", raw_value).lower()
    match = re.fullmatch(r"site([abc])", compact)

    if not match:
        raise ValueError(f"Unrecognized site: {raw_value!r}")

    return f"Site {match.group(1).upper()}"


def clean_glucose(raw_value, raw_unit):
    """Return glucose in mg/dL plus its parsing status."""
    value = raw_value.strip()
    unit = re.sub(r"\s+", "", raw_unit).lower()

    if re.fullmatch(r"n/?a", value, flags=re.IGNORECASE):
        return "", "missing"

    match = re.fullmatch(r"(\d+(?:\.\d+)?)(\*)?", value)

    if not match:
        raise ValueError(f"Unrecognized glucose value: {raw_value!r}")

    glucose = float(match.group(1))
    status = "annotated" if match.group(2) else "reported"

    if unit == "mmol/l":
        glucose *= MMOL_L_TO_MG_DL
    elif unit != "mg/dl":
        raise ValueError(f"Unrecognized glucose unit: {raw_unit!r}")

    return f"{glucose:.1f}", status


def clean_row(row):
    """Clean one input record."""
    glucose, glucose_status = clean_glucose(
        row["glucose_value"],
        row["glucose_unit"],
    )

    return {
        "sample_id": clean_sample_id(row["sample_id"]),
        "patient_name": row["patient_name"].strip().title(),
        "dob": clean_date(row["dob"]),
        "sex": clean_sex(row["sex"]),
        "enrollment_site": clean_site(row["enrollment_site"]),
        "glucose_mg_dl": glucose,
        "glucose_status": glucose_status,
        "notes": row["notes"].strip(),
    }


def clean_file(input_path, output_path):
    """Clean the complete CSV and write a structured output table."""
    with input_path.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        cleaned_rows = []

        for file_line, row in enumerate(reader, start=2):
            try:
                cleaned_rows.append(clean_row(row))
            except ValueError as error:
                raise ValueError(f"Input line {file_line}: {error}") from error

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"Wrote {len(cleaned_rows)} records to {output_path}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Clean the Lab 3 clinical sample data with regex."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/messy_samples.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/regex/clean_samples_regex.csv"),
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    clean_file(args.input, args.output)


if __name__ == "__main__":
    main()
