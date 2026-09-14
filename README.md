# RateCardSentinel

RateCardSentinel is a freight invoice rate-audit product. It ingests carrier invoice documents in whatever format they arrive in, extracts invoice header and line-item fields, compares invoiced charges against the contracted rate card for the lane, and surfaces every variance through a dashboard so finance teams can dispute overcharges and recover margin.

## Architecture

- `poller.py` — Railway worker. Long-running `poll()` loop that claims pending `process_upload` jobs from Supabase, downloads the uploaded invoice from the `uploads` storage bucket, runs it through `processor`, inserts one record per invoice/line item into the `records` table, uploads a JSON result to the `results` bucket, marks the job completed/failed, and writes a notification row.
- `processor.py` — Core extraction module. Exposes `process_file(file_bytes)`. Detects PDF / Excel / CSV / plain text, extracts invoice and line-item fields (invoice header, carrier, lane, contracted vs. invoiced rate, accessorials, fuel surcharge, variance), and returns a list of structured records.
- `backend/` — Copy of the processing modules packaged alongside the poller for deployment.
- `dashboard/` — Vite + React + TypeScript front end. Upload carrier invoices, review extracted line items, filter by invoice/carrier/lane, and track audit status (valid, flagged, underbilled, duplicate_invoice, no_contract, tolerance_review, pending_review, and more).
- `Dockerfile` — Railway build. Python 3.12 slim image that installs `requirements.txt` and runs `python3 poller.py`.

## Environment variables

- `SUPABASE_URL` — Supabase project URL.
- `SUPABASE_SERVICE_KEY` — Service-role key used for REST and storage access.
- `PRODUCT_ID` — Product identifier written to every record, job, and notification.
- `ANTHROPIC_API_KEY` — Reserved for downstream enrichment.

Dashboard build-time variables (set in Vercel):

- `VITE_PRODUCT_ARCHETYPE=extraction`
- `VITE_RECORDS_LABEL=Invoice Audits`
- `VITE_RECORDS_SUBTITLE=Carrier invoice line items compared against contracted rate cards`
- `VITE_FILTER_PLACEHOLDER=Filter by invoice, carrier, or lane...`
- `VITE_UPLOAD_DESCRIPTION` / `VITE_UPLOAD_EMPTY_STATE` — Upload copy.

## Files

- `processor.py` — Extraction and matching core.
- `poller.py` — Railway job poller.
- `backend/` — Deployment copy of the processing modules.
- `dashboard/` — Front-end application.
- `Dockerfile` — Container definition for the poller worker.
- `requirements.txt` — Python dependencies.

Dashboard: https://ratecardsentinel.vokrix.co
Vercel: ratecardsentinel
Railway: ratecardsentinel
