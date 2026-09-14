import csv
import io
import re
from datetime import datetime


_FIELD_PATTERNS = {
    'invoice_number': r'(?i)invoice\s*(?:number|#|no)?\s*[:.]\s*([A-Za-z0-9\-]+)',
    'carrier_name': r'(?i)carrier\s*(?:name)?\s*[:.]\s*(.+)',
    'carrier_mc_number': r'(?i)mc\s*(?:number|#|no)?\s*[:.]\s*([0-9]{5,})',
    'carrier_dot_number': r'(?i)dot\s*(?:number|#|no)?\s*[:.]\s*([0-9]{5,})',
    'broker_name': r'(?i)broker\s*(?:name)?\s*[:.]\s*(.+)',
    'load_number': r'(?i)load\s*(?:number|#|no)?\s*[:.]\s*([A-Za-z0-9\-]+)',
    'bol_number': r'(?i)bol\s*(?:number|#|no)?\s*[:.]\s*([A-Za-z0-9\-]+)',
    'pro_number': r'(?i)pro\s*(?:number|#|no)?\s*[:.]\s*([A-Za-z0-9\-]+)',
    'shipment_date': r'(?i)shipment\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+[0-9]{1,2},\s*[0-9]{4})',
    'delivery_date': r'(?i)delivery\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+[0-9]{1,2},\s*[0-9]{4})',
    'invoice_date': r'(?i)invoice\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+[0-9]{1,2},\s*[0-9]{4})',
    'due_date': r'(?i)due\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+[0-9]{1,2},\s*[0-9]{4})',
    'payment_terms': r'(?i)payment\s*terms\s*[:.]\s*(.+)',
    'origin_city': r'(?i)origin\s*city\s*[:.]\s*(.+)',
    'origin_state': r'(?i)origin\s*state\s*[:.]\s*([A-Za-z]{2})',
    'origin_zip': r'(?i)origin\s*zip\s*[:.]\s*([0-9]{5}(?:-?[0-9]{4})?)',
    'destination_city': r'(?i)destination\s*city\s*[:.]\s*(.+)',
    'destination_state': r'(?i)destination\s*state\s*[:.]\s*([A-Za-z]{2})',
    'destination_zip': r'(?i)destination\s*zip\s*[:.]\s*([0-9]{5}(?:-?[0-9]{4})?)',
    'lane': r'(?i)lane\s*[:.]\s*(.+)',
    'total_invoice_amount': r'(?i)total\s*(?:invoice\s*amount|amount\s*due)?\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'currency': r'(?i)currency\s*[:.]\s*([A-Za-z]{3})',
    'remit_to': r'(?i)remit\s*to\s*[:.]\s*(.+)',
    'reference_numbers': r'(?i)reference\s*(?:number|numbers|#)?\s*[:.]\s*(.+)',
    'purchase_order': r'(?i)purchase\s*order\s*[:.]\s*(.+)',
    'customer_reference': r'(?i)customer\s*reference\s*[:.]\s*(.+)',
    'invoice_status': r'(?i)invoice\s*status\s*[:.]\s*(.+)',
    'source_document_name': r'(?i)source\s*document\s*name\s*[:.]\s*(.+)',
    'page_number': r'(?i)page\s*(?:number|#)?\s*[:.]\s*([0-9]+)',
    'line_item_number': r'(?i)line\s*(?:item\s*number|item\s*#|#)?\s*[:.]\s*([A-Za-z0-9\-]+)',
    'charge_description': r'(?i)charge\s*description\s*[:.]\s*(.+)',
    'charge_type': r'(?i)charge\s*type\s*[:.]\s*(.+)',
    'rate_confirmation_line_item': r'(?i)rate\s*confirmation\s*line\s*item\s*[:.]\s*(.+)',
    'contracted_rate': r'(?i)contracted\s*rate\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'invoiced_rate': r'(?i)invoiced\s*rate\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'variance_amount': r'(?i)variance\s*amount\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'variance_percent': r'(?i)variance\s*percent\s*[:.]\s*([0-9.]+%?)',
    'quantity': r'(?i)quantity\s*[:.]\s*([0-9.]+)',
    'unit_type': r'(?i)unit\s*type\s*[:.]\s*(.+)',
    'miles': r'(?i)miles\s*[:.]\s*([0-9.]+)',
    'weight': r'(?i)weight\s*[:.]\s*([0-9.]+)',
    'pieces': r'(?i)pieces\s*[:.]\s*([0-9]+)',
    'pallets': r'(?i)pallets\s*[:.]\s*([0-9]+)',
    'commodity': r'(?i)commodity\s*[:.]\s*(.+)',
    'equipment_type': r'(?i)equipment\s*type\s*[:.]\s*(.+)',
    'temperature_requirements': r'(?i)temperature\s*requirements\s*[:.]\s*(.+)',
    'accessorial_code': r'(?i)accessorial\s*code\s*[:.]\s*(.+)',
    'accessorial_description': r'(?i)accessorial\s*description\s*[:.]\s*(.+)',
    'fuel_surcharge_rate': r'(?i)fuel\s*surcharge\s*rate\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'fuel_surcharge_amount': r'(?i)fuel\s*surcharge\s*amount\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'fuel_index_date': r'(?i)fuel\s*index\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4})',
    'fuel_peg': r'(?i)fuel\s*peg\s*[:.]\s*(.+)',
    'fuel_base_price': r'(?i)fuel\s*base\s*price\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'discount': r'(?i)discount\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'surcharge': r'(?i)surcharge\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'tax': r'(?i)tax\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'total_line_amount': r'(?i)total\s*line\s*amount\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'rate_card_reference': r'(?i)rate\s*card\s*reference\s*[:.]\s*(.+)',
    'contract_reference': r'(?i)contract\s*reference\s*[:.]\s*(.+)',
    'effective_date': r'(?i)effective\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+[0-9]{1,2},\s*[0-9]{4})',
    'expiration_date': r'(?i)expiration\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+[0-9]{1,2},\s*[0-9]{4})',
    'commodity_restrictions': r'(?i)commodity\s*restrictions\s*[:.]\s*(.+)',
    'service_level': r'(?i)service\s*level\s*[:.]\s*(.+)',
    'contract_terms': r'(?i)contract\s*terms\s*[:.]\s*(.+)',
    'version': r'(?i)version\s*[:.]\s*(.+)',
    'approval_status': r'(?i)approval\s*status\s*[:.]\s*(.+)',
    'matched_rate_card_id': r'(?i)matched\s*rate\s*card\s*id\s*[:.]\s*(.+)',
    'matched_contract_lane': r'(?i)matched\s*contract\s*lane\s*[:.]\s*(.+)',
    'match_confidence': r'(?i)match\s*confidence\s*[:.]\s*([0-9.]+%?)',
    'expected_base_rate': r'(?i)expected\s*base\s*rate\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'invoiced_base_rate': r'(?i)invoiced\s*base\s*rate\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'expected_fuel_surcharge': r'(?i)expected\s*fuel\s*surcharge\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'invoiced_fuel_surcharge': r'(?i)invoiced\s*fuel\s*surcharge\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'expected_accessorial_total': r'(?i)expected\s*accessorial\s*total\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'invoiced_accessorial_total': r'(?i)invoiced\s*accessorial\s*total\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'total_expected_amount': r'(?i)total\s*expected\s*amount\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'total_invoiced_amount': r'(?i)total\s*invoiced\s*amount\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'total_variance': r'(?i)total\s*variance\s*[:.]\s*([$\s]*[0-9,]+\.?[0-9]*)',
    'variance_direction': r'(?i)variance\s*direction\s*[:.]\s*(.+)',
    'severity': r'(?i)severity\s*[:.]\s*(.+)',
    'recommended_action': r'(?i)recommended\s*action\s*[:.]\s*(.+)',
    'dispute_packet_available': r'(?i)dispute\s*packet\s*available\s*[:.]\s*(.+)',
    'recurring_error_flag': r'(?i)recurring\s*error\s*flag\s*[:.]\s*(.+)',
    'carrier_pattern_flag': r'(?i)carrier\s*pattern\s*flag\s*[:.]\s*(.+)',
    'audit_date': r'(?i)audit\s*date\s*[:.]\s*([0-9]{1,4}[/\-][0-9]{1,4}[/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+[0-9]{1,2},\s*[0-9]{4})',
    'auditor': r'(?i)auditor\s*[:.]\s*(.+)',
}


def _extract_text(file_bytes: bytes) -> str:
    if file_bytes[:4] == b'%PDF':
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() or '' for page in pdf.pages]
                return '\n'.join(pages)
        except Exception:
            pass

    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        rows = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                values = ['' if cell is None else str(cell) for cell in row]
                if any(v.strip() for v in values):
                    rows.append('\t'.join(values))
        if rows:
            return '\n'.join(rows)
    except Exception:
        pass

    return file_bytes.decode('utf-8', errors='ignore')


def _parse_table(text: str):
    if not text.strip():
        return [], []

    for delimiter in [',', '\t', ';', '|']:
        try:
            reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
            headers = [h.strip() for h in reader.fieldnames if h and h.strip()]
            if len(headers) < 2:
                continue

            rows = []
            for row in reader:
                cleaned = {}
                for key, value in row.items():
                    if key is None:
                        continue
                    cleaned[key.strip()] = (value or '').strip()
                if any(cleaned.values()):
                    rows.append(cleaned)

            if rows:
                return rows, headers
        except Exception:
            continue

    return [], []


def _parse_date(value):
    if not value:
        return None
    value = value.strip()
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%m/%d/%y',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%d-%b-%Y',
        '%b %d, %Y',
        '%Y/%m/%d',
        '%m-%d-%Y',
        '%d %b %Y',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _to_float(value):
    if value is None:
        return None
    text = str(value).replace('$', '').replace(',', '').strip()
    if text.endswith('%'):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return None


def _find_key_value(details, *names):
    for key, value in details.items():
        key_lower = key.lower().strip()
        for name in names:
            if key_lower == name.lower():
                return value
    return None


def _parse_fields_from_text(text):
    fields = {}
    for key, pattern in _FIELD_PATTERNS.items():
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            if value:
                fields[key] = value
    return fields


def _extract_title(details):
    for key in ['carrier_name', 'supplier', 'vendor', 'broker_name', 'customer']:
        value = _find_key_value(details, key)
        if value:
            return value.strip()
    return 'Unknown Entity'


def _determine_status(details):
    contracted = _find_key_value(
        details, 'contracted_rate', 'contracted rate', 'contracted_amount', 'rate'
    )
    invoiced = _find_key_value(
        details, 'invoiced_rate', 'invoiced rate', 'invoiced_amount', 'price',
        'total_line_amount', 'amount'
    )

    if contracted is not None and invoiced is not None:
        contracted_val = _to_float(contracted)
        invoiced_val = _to_float(invoiced)
        if contracted_val is not None and invoiced_val is not None and contracted_val != 0:
            variance = invoiced_val - contracted_val
            variance_percent = (variance / contracted_val) * 100
            details['variance_amount'] = round(variance, 2)
            details['variance_percent'] = round(variance_percent, 2)
            if abs(variance_percent) <= 2:
                return 'valid'
            if variance > 0:
                return 'flagged' if variance_percent > 5 else 'tolerance_review'
            return 'underbilled' if variance_percent < -5 else 'tolerance_review'

    has_identifier = any(
        _find_key_value(details, key)
        for key in [
            'invoice_number', 'carrier_name', 'supplier', 'vendor',
            'customer', 'broker_name'
        ]
    )
    has_contract = _find_key_value(
        details, 'rate_card_id', 'contract_reference',
        'rate_card_reference', 'contracted_rate'
    )

    if has_identifier and not has_contract:
        return 'no_contract'

    if str(_find_key_value(details, 'invoice_status')).strip().lower() == 'duplicate':
        return 'duplicate_invoice'

    return 'pending_review'


def _record_from_row(row):
    details = {}
    for key, value in row.items():
        if key is not None:
            details[key.strip()] = (value or '').strip()

    due_date = _parse_date(_find_key_value(details, 'due_date'))

    return {
        'title': _extract_title(details),
        'status': _determine_status(details),
        'details': details,
        'due_date': due_date,
    }


def _record_from_fields(fields, text=''):
    details = dict(fields)
    if not details and text:
        details['raw_text'] = text[:2000]

    due_date = _parse_date(details.get('due_date'))

    return {
        'title': _extract_title(details),
        'status': _determine_status(details),
        'details': details,
        'due_date': due_date,
    }


def process_file(file_bytes: bytes) -> list:
    try:
        text = _extract_text(file_bytes)
        rows, _ = _parse_table(text)

        if rows:
            records = []
            for row in rows:
                records.append(_record_from_row(row))
            return records

        fields = _parse_fields_from_text(text)
        return [_record_from_fields(fields, text)]

    except Exception:
        fallback_text = file_bytes.decode('utf-8', errors='ignore')[:2000]
        return [{
            'title': 'Unknown Entity',
            'status': 'pending_review',
            'details': {'raw_text': fallback_text},
            'due_date': None,
        }]
