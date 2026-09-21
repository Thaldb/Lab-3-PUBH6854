"""Parse inconsistent FASTA headers into a structured CSV table."""

import argparse
import csv
import re
from pathlib import Path


OUTPUT_FIELDS = [
    "sample_id",
    "organism",
    "gene",
    "reported_length",
    "sequence_length",
    "length_match",
    "notes",
    "sequence",
]


def parse_sample_id(header):
    """Extract and standardize sample/sequence identifiers."""
    match = re.search(
        r"\b(?:sample|seq)[_-]?0*(\d+)\b",
        header,
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(f"Could not identify sample ID in header: {header!r}")

    return f"sample_{int(match.group(1)):03d}"


def parse_organism(header):
    """Recognize the observed Homo sapiens spellings."""
    match = re.search(
        r"(?:Homo[_ ]sapiens|H\.?sapiens)",
        header,
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(f"Could not identify organism in header: {header!r}")

    return "Homo sapiens"


def parse_gene(header):
    """Extract one of the expected gene symbols."""
    match = re.search(
        r"\b(BRCA1|TP53|EGFR)\b",
        header,
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(f"Could not identify gene in header: {header!r}")

    return match.group(1).upper()


def parse_reported_length(header):
    """Extract a numeric reported length when the header provides one."""
    keyed_match = re.search(
        r"\b(?:len|length)\s*[:=]\s*(\d+)(?:\s*bp)?\b",
        header,
        flags=re.IGNORECASE,
    )

    if keyed_match:
        return int(keyed_match.group(1))

    unkeyed_match = re.search(
        r"\b(\d+)\s*bp\b",
        header,
        flags=re.IGNORECASE,
    )

    if unkeyed_match:
        return int(unkeyed_match.group(1))

    return None


def parse_note(header):
    """Extract an optional note field."""
    match = re.search(
        r"\bnote\s*[:=]\s*([^|;]+)",
        header,
        flags=re.IGNORECASE,
    )

    return match.group(1).strip() if match else ""


def validate_sequence(sequence, header):
    """Ensure that the assembled sequence contains only DNA characters."""
    if not re.fullmatch(r"[ACGTN]+", sequence, flags=re.IGNORECASE):
        raise ValueError(f"Invalid sequence characters for header: {header!r}")


def structure_record(header, sequence):
    """Convert one FASTA record into a structured row."""
    sequence = sequence.upper()
    validate_sequence(sequence, header)

    reported_length = parse_reported_length(header)
    sequence_length = len(sequence)

    if reported_length is None:
        length_match = ""
        reported_length_output = ""
    else:
        length_match = str(reported_length == sequence_length)
        reported_length_output = reported_length

    return {
        "sample_id": parse_sample_id(header),
        "organism": parse_organism(header),
        "gene": parse_gene(header),
        "reported_length": reported_length_output,
        "sequence_length": sequence_length,
        "length_match": length_match,
        "notes": parse_note(header),
        "sequence": sequence,
    }


def read_fasta(input_path):
    """Read multiline FASTA records."""
    records = []
    current_header = None
    sequence_parts = []

    with input_path.open(encoding="utf-8") as input_file:
        for file_line, raw_line in enumerate(input_file, start=1):
            line = raw_line.strip()

            if not line:
                continue

            header_match = re.fullmatch(r">(.+)", line)

            if header_match:
                if current_header is not None:
                    records.append(
                        structure_record(
                            current_header,
                            "".join(sequence_parts),
                        )
                    )

                current_header = header_match.group(1)
                sequence_parts = []
            else:
                if current_header is None:
                    raise ValueError(
                        f"Sequence found before a header on line {file_line}"
                    )

                sequence_parts.append(line)

    if current_header is not None:
        records.append(
            structure_record(current_header, "".join(sequence_parts))
        )

    return records


def clean_file(input_path, output_path):
    """Parse the FASTA file and write a structured CSV."""
    records = read_fasta(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} records to {output_path}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parse the Lab 3 FASTA data with regex."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/messy_sequences.fasta"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/processed/regex/clean_sequences_regex.csv"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    clean_file(args.input, args.output)


if __name__ == "__main__":
    main()
