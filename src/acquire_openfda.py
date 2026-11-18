"""Download and filter the official openFDA medical-device enforcement export."""

from __future__ import annotations

import json
import time
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST_URL = "https://api.fda.gov/download.json"
KEEP = {
    "status", "classification", "event_id", "recall_number", "recalling_firm",
    "state", "country", "voluntary_mandated", "initial_firm_notification",
    "product_description", "reason_for_recall", "recall_initiation_date",
    "center_classification_date", "report_date", "termination_date",
}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = requests.get(MANIFEST_URL, timeout=60).json()
    source = manifest["results"]["device"]["enforcement"]
    partition = source["partitions"][0]
    archive = RAW / "device-enforcement.json.zip"
    if not archive.exists():
        with requests.get(partition["file"], stream=True, timeout=120) as response:
            response.raise_for_status()
            with archive.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    handle.write(chunk)

    output = RAW / "openfda_enforcement_2022_2025.jsonl"
    with zipfile.ZipFile(archive) as bundle:
        with bundle.open(bundle.namelist()[0]) as handle:
            payload = json.load(handle)
    kept = 0
    with output.open("w", encoding="utf-8") as handle:
        for record in payload["results"]:
            value = record.get("recall_initiation_date", "")
            if "20220101" <= value <= "20251231":
                handle.write(json.dumps({key: record.get(key) for key in KEEP}, ensure_ascii=False) + "\n")
                kept += 1

    run_manifest = {
        "source_manifest": MANIFEST_URL,
        "source_file": partition["file"],
        "openfda_export_date": source["export_date"],
        "source_records": partition["records"],
        "cohort_filter": "recall_initiation_date between 2022-01-01 and 2025-12-31",
        "cohort_records": kept,
        "downloaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "output": str(output.relative_to(ROOT)),
    }
    (RAW / "download_manifest.json").write_text(json.dumps(run_manifest, indent=2), encoding="utf-8")
    print(json.dumps(run_manifest, indent=2))


if __name__ == "__main__":
    main()
