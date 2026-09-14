# RateCardSentinel

RateCardSentinel is a freight invoice rate-audit backend. It ingests carrier invoice documents in whatever format they arrive in, extracts invoice header and line-item fields, matches invoiced charges against the contracted rate card for the lane, and returns one structured record per invoice or line item so a downstream dashboard or poller can act on it.

## Files

- processor.py   Core module. Exposes process_file(file_bytes). Detects PDF / Excel / CSV / plain text, extracts invoice and line-item fields, returns a list of structured records.
- run_demo.py    Zero-argument demo. Runs a hardcoded CSV byte string through processor.process_file() and prints the records. Exits 0.
- run_tests.py   Unit tests covering CSV processing, plain-text invoice extraction, and the unknown-bytes fallback.
- requirements.txt  Python dependencies.

## Files

- processor.py   Core module. Exposes process_file(file_bytes). Detects PDF, Excel, CSV, or plain text, extracts invoice and line-item fields, and returns a list of structured records.
- run_demo.py   Zero-argument demo. Runs a hardcoded CSV byte string through processor.process_file() and prints the records. Exits 0.
- run_tests.py   Unit tests covering CSV processing, plain-text invoice extraction, and the unknown-bytes fallback.
- requirements.txt   Python dependencies.
