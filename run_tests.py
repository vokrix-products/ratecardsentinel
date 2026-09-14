import unittest

import processor


class TestProcessorCSV(unittest.TestCase):
    def test_csv_record_shape(self):
        data = (
            b"carrier_name,load_number,contracted_rate,invoiced_rate,due_date\n"
            b"Lightning Freight,LD-2201,2400.00,2650.00,2025-03-15\n"
        )
        records = processor.process_file(data)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record['title'], 'Lightning Freight')
        self.assertEqual(record['status'], 'flagged')
        self.assertEqual(record['due_date'], '2025-03-15')
        self.assertEqual(record['details']['load_number'], 'LD-2201')

    def test_csv_within_tolerance(self):
        data = (
            b"carrier_name,contracted_rate,invoiced_rate\n"
            b"Redwood Logistics,1800.00,1815.00\n"
        )
        records = processor.process_file(data)

        self.assertEqual(records[0]['status'], 'valid')
        self.assertEqual(records[0]['title'], 'Redwood Logistics')

    def test_csv_tolerance_review(self):
        data = (
            b"carrier_name,contracted_rate,invoiced_rate\n"
            b"Redwood Logistics,1800.00,1850.00\n"
        )
        records = processor.process_file(data)

        self.assertEqual(records[0]['status'], 'tolerance_review')
        self.assertEqual(records[0]['title'], 'Redwood Logistics')

    def test_csv_no_contract(self):
        data = (
            b"supplier,product,price\n"
            b"Acme,Widget,9.99\n"
        )
        records = processor.process_file(data)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Acme')
        self.assertEqual(records[0]['status'], 'no_contract')
        self.assertIsNone(records[0]['due_date'])
        self.assertEqual(records[0]['details']['product'], 'Widget')


class TestProcessorPlainText(unittest.TestCase):
    def test_multiple_rows_from_text(self):
        data = (
            b"Carrier Name: Lightning Freight\n"
            b"Invoice Number: INV-1001\n"
            b"Load Number: LD-2201\n"
            b"Contracted Rate: 2400.00\n"
            b"Invoiced Rate: 2650.00\n"
            b"Due Date: 2025-03-15\n"
        )
        records = processor.process_file(data)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record['title'], 'Lightning Freight')
        self.assertEqual(record['details']['invoice_number'], 'INV-1001')
        self.assertEqual(record['status'], 'flagged')

    def test_text_valid_rate(self):
        data = (
            b"Carrier Name: Redwood Logistics\n"
            b"Contracted Rate: 1800.00\n"
            b"Invoiced Rate: 1800.00\n"
        )
        records = processor.process_file(data)

        self.assertEqual(records[0]['status'], 'valid')

    def test_text_underbilled(self):
        data = (
            b"Carrier Name: Redwood Logistics\n"
            b"Contracted Rate: 2000.00\n"
            b"Invoiced Rate: 1700.00\n"
        )
        records = processor.process_file(data)

        self.assertEqual(records[0]['status'], 'underbilled')


class TestProcessorFallback(unittest.TestCase):
    def test_unknown_bytes(self):
        records = processor.process_file(b'\x00\x01\x02\xff\xfe')

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['title'], 'Unknown Entity')
        self.assertEqual(records[0]['status'], 'pending_review')
        self.assertIsNone(records[0]['due_date'])

    def test_empty_bytes(self):
        records = processor.process_file(b'')

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['status'], 'pending_review')

    def test_always_returns_list_of_dicts(self):
        for payload in [b'', b'random text', b'%PDF-1.4', b'\x00\x01']:
            records = processor.process_file(payload)
            self.assertIsInstance(records, list)
            self.assertTrue(len(records) >= 1)
            self.assertIsInstance(records[0], dict)
            for key in ('title', 'status', 'details', 'due_date'):
                self.assertIn(key, records[0])


if __name__ == "__main__":
    unittest.main()
