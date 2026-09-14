from processor import process_file

SAMPLE_CSV = (
    "carrier_name,load_number,origin_city,destination_city,"
    "contracted_rate,invoiced_rate,due_date,invoice_number\n"
    "Lightning Freight,LD-2201,Chicago,Dallas,2400.00,2650.00,2025-03-15,INV-1001\n"
    "Redwood Logistics,LD-2202,Atlanta,Miami,1800.00,1815.00,2025-03-18,INV-1002\n"
)


def main():
    file_bytes = SAMPLE_CSV.encode('utf-8')
    records = process_file(file_bytes)

    print("RateCardSentinel demo — processed {0} record(s)".format(len(records)))
    for record in records:
        print("-")
        print("  title:    {0}".format(record['title']))
        print("  status:   {0}".format(record['status']))
        print("  due_date: {0}".format(record['due_date']))
        print("  details:  {0}".format(record['details']))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
