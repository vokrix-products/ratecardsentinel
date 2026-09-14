import io
import json
import os
import time
from datetime import datetime, timezone

import requests

import processor

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
PRODUCT_ID = os.environ.get("PRODUCT_ID", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

REST_URL = SUPABASE_URL + "/rest/v1"
SB_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": "Bearer " + SUPABASE_SERVICE_KEY,
}


def download_file(bucket, file_path):
    if file_path.startswith(bucket + "/"):
        file_path = file_path[len(bucket) + 1:]
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
        },
    )
    resp.raise_for_status()
    return resp.content


def upload_file(bucket, file_path, content, content_type="application/octet-stream"):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
            "Content-Type": content_type,
            "x-upsert": "true",
        },
        data=content,
    )
    resp.raise_for_status()
    return resp.json() if resp.content else {}


def get_pending_jobs():
    url = (
        REST_URL
        + "/jobs?status=eq.pending&job_type=eq.process_upload&product_id=eq."
        + PRODUCT_ID
    )
    resp = requests.get(url, headers=SB_HEADERS)
    resp.raise_for_status()
    return resp.json()


def update_job(job_id, payload):
    url = REST_URL + "/jobs?id=eq." + str(job_id)
    resp = requests.patch(
        url,
        headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        json=payload,
    )
    resp.raise_for_status()


def insert_record(customer_id, job, r):
    resp = requests.post(
        REST_URL + "/records",
        headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        json={
            "product_id": PRODUCT_ID,
            "customer_id": customer_id,
            "title": r["title"],
            "status": r["status"],
            "details": r["details"],
            "source_file_path": job["input_file_path"],
            "due_date": r.get("due_date"),
        },
    )
    resp.raise_for_status()


def insert_notification(customer_id, title, body, type_):
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/notifications",
            headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={
                "product_id": PRODUCT_ID,
                "customer_id": customer_id,
                "title": title,
                "body": body,
                "type": type_,
                "read": False,
            },
        )
    except Exception as exc:
        print("notification failed:", exc)


def process_job(job):
    job_id = job["id"]
    customer_id = job["customer_id"]
    input_file_path = job["input_file_path"]

    try:
        file_bytes = download_file("uploads", input_file_path)
        records = processor.process_file(file_bytes)

        for r in records:
            insert_record(customer_id, job, r)

        result_payload = json.dumps(records, default=str, indent=2).encode("utf-8")
        output_file_path = f"{job_id}.json"
        upload_file("results", output_file_path, result_payload, "application/json")

        summary = f"Processed {len(records)} record(s) from {input_file_path}"
        update_job(
            job_id,
            {
                "status": "completed",
                "output_file_path": output_file_path,
                "result_summary": summary,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        insert_notification(
            customer_id,
            "Processing complete",
            "Your upload has been processed successfully.",
            "success",
        )
        print(f"job {job_id} completed: {summary}")

    except Exception as exc:
        print(f"job {job_id} failed:", exc)
        try:
            update_job(
                job_id,
                {
                    "status": "failed",
                    "result_summary": str(exc)[:500],
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception as update_exc:
            print("failed to mark job failed:", update_exc)
        insert_notification(
            customer_id,
            "Processing failed",
            "There was an error processing your upload.",
            "error",
        )


def poll():
    print("Polling for pending jobs...")
    while True:
        try:
            jobs = get_pending_jobs()
            for job in jobs:
                process_job(job)
        except Exception as exc:
            print("poll error:", exc)
        time.sleep(60)


if __name__ == "__main__":
    print("Poller started")
    poll()
