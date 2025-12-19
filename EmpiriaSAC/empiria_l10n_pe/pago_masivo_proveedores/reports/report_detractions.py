import base64
import os
import tempfile
import zipfile


class ReportInvBalTxt(object):

    def __init__(self, name, line, data, data_2, bank):
        self.name = name
        self.line = line
        self.data = data
        self.data_2 = data_2
        self.bank = bank
        self.filename = 'Pago'

    def get_content(self):
        raw = ''
        if self.bank == '11': # BBVA Continental
            zeros = '000000000000000000'
            raw += '750{bank_account_id}{currency_id}{amount_total}{process_type}{date}{executing_schedule}{reference}{lines}{validate_belonging}{zeros}\r\n'.format(
                bank_account_id=self.line['bank_account_id'],
                currency_id=self.line['currency_id'],
                amount_total=self.line['amount_total'],
                process_type=self.line['process_type'],
                date=self.line['date'],
                executing_schedule=self.line['executing_schedule'],
                reference=self.line['reference'],
                lines=self.line['lines'],
                validate_belonging=self.line['validate_belonging'],
                zeros=self.line['zeros'],
            )
            template = '002{doi_type}{doi_number}{type_deposit}{account}{name_client}{amount}{type_document}{number_document}{N}{reference}{zeros}\r\n'
            for value in self.data:
                raw += template.format(
                    doi_type=value['doi_type'],
                    doi_number=value['doi_number'],
                    type_deposit=value['type_deposit'],
                    account=value['account'],
                    name_client=value['name_client'],
                    amount=value['amount'],
                    type_document=value['type_document'],
                    number_document=value['number_document'],
                    N=value['grouped_credit'],
                    reference=value['reference'],
                    zeros=value['zeros']
                )
            return raw
        #
        elif self.bank == '02': # BCP
            # linea 1
            raw += '{id}{lines_total}{date}{c}{currency}{acc_number}{amount_total}{reference}{N}{abono}\r\n'.format(
                id=self.line['id'], #col 1 (1)      
                lines_total=self.line['lines_total'], #col 2-7 (6)
                date=self.line['date'], #col 8-15 (8)
                c=self.line['c'], # col 16 (1)
                currency=self.line['currency'], # col 17-20 (4)
                acc_number=self.line['acc_number'], # col 21-40 (20)
                amount_total=self.line['amount_total'], # col 41-57 (15)
                reference=self.line['reference'], # col 58-97
                N=self.line['N'], # col 98
                abono=self.line['abono'], # col 99-113
            )
            # linea 2
            template = '{id}{bank_cod}{account}{id_2}{doc}{vat}{spaces}{partner_name}{reference}{payment_reference}{currency}{amount}{N}\r\n'
            for value in self.data:
                raw += template.format(
                    id=value['id'],
                    bank_cod=value['bank_cod'],
                    account=value['account'],
                    id_2=value['id_2'],
                    doc=value['doc'],
                    vat=value['vat'],
                    spaces=value['spaces'],
                    partner_name=value['partner_name'],
                    reference=value['reference'],
                    payment_reference=value['payment_reference'],
                    currency=value['currency'],
                    amount=value['amount'],
                    N=value['N'],
                )
            # linea 3
            template_2 = '{id}{document}{ref}{amount}\r\n'
            for value in self.data_2:
                raw += template_2.format(
                    id=value['id'], # col 1
                    document=value['document'], # col 2
                    ref=value['ref'], # col 3-17
                    amount=value['amount'], #col 18-34
                )
            return raw
        elif self.bank == '03': # Interbank
            raw += '0103{company_code}{service_code}{bank_account}{account_type}{currency_id}{pay}{date_time}{process_type_itb}{date}{lines}{amount_total_pen}{amount_total_usd}{m}\r\n'.format(
                company_code=self.line['company_code'], # col 5-8 (4)
                service_code=self.line['service_code'], # col 9-10 (2)
                bank_account=self.line['bank_account'], # col 11-23 (13)
                account_type=self.line['account_type'], # col 24-26 (3)
                currency_id=self.line['currency_id'], # col 27-28 (2)
                pay=self.line['pay'], # col 29-40 (12)
                date_time=self.line['date_time'], # col 41-54 (14)
                process_type_itb=self.line['process_type_itb'], # col 55 (1)
                date=self.line['date'], # col 56-63 ()
                lines=self.line['lines'], # col 64-69
                amount_total_pen=self.line['amount_total_pen'], # col 70-84
                amount_total_usd=self.line['amount_total_usd'], # col 85-99
                m=self.line['m'], # col 100-104
            )
            template = '02{ruc}{doc}{payment}{expire_date}{currency}{amount}{space}{sunat_bank_code}{account_type}' \
                       '{currency_id}{acc_3}{account}{type_document}{doc_tyoe}{document}{name}{number}\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'], # col 3-22 (20)
                    doc=value['doc'], # col 23-23 (1) V
                    payment=value['payment'], # col 24-43 (20) V
                    expire_date=value['expire_date'], # col 44-51 (8) V
                    currency=value['currency'], # col 52-53 (2)
                    amount=value['amount'], # col 54-68 (15)
                    space=value['space'], # col 69-69 (1)
                    sunat_bank_code=value['sunat_bank_code'], # col 70-71 (2)
                    account_type=value['account_type'], # col 72-74 (3)
                    currency_id=value['currency_id'], # col 75-76 (2)
                    acc_3=value['acc_3'], # col 77-79 (2)
                    account=value['account'], # col 80-99 (20)
                    type_document=value['type_document'], # col 100-100 (1) V
                    doc_tyoe=value['doc_tyoe'], # col 101-102 (2)
                    document=value['document'], # col 103-117 (15)
                    name=value['name'],  # col 118-177 (60)
                    number=value['203'],
                )
            return raw
        elif self.bank == '09': #SCOTIABANK
            template = '{ruc}{name}{ref}{invoice_date}{payment_amount}{type_acc}{office}{acc_number}' \
                       '{count_account}{email}{cci_number}{currency_id}01\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'],
                    name=value['name'],
                    ref=value['ref'],
                    invoice_date=value['invoice_date'],
                    payment_amount=value['payment_amount'],
                    office=value['office'],
                    type_acc=value['type_acc'],
                    acc_number=value['acc_number'],
                    count_account=value['count_account'],
                    email=value['email'],
                    cci_number=value['cci_number'],
                    currency_id=value['currency_id'],
                )
        elif self.bank == '09_txt':
            template = '{ruc}{name}{email}{ref}{currency_id}{amount}' \
                       '{spaces}{bank}\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'],
                    name=value['name'],
                    email=value['email'],
                    ref=value['ref'],
                    currency_id=value['currency_id'],
                    amount=value['amount'],
                    spaces=value['spaces'],
                    bank=value['bank'],
                )
        elif self.bank == '09_zip':
            template = '{ruc}{name}{email}{ref}{currency_id}{amount}' \
                       '{spaces}{bank}\r\n'
            for value in self.data:
                raw += template.format(
                    ruc=value['ruc'],
                    name=value['name'],
                    email=value['email'],
                    ref=value['ref'],
                    currency_id=value['currency_id'],
                    amount=value['amount'],
                    spaces=value['spaces'],
                    bank=value['bank'],
                )
            tmp_dir = self.generate_tmp_dir(raw)
            zip_dir = self.generate_zip(tmp_dir)
            f = open(zip_dir, "rb").read()
            return base64.encodebytes(f)
        return raw

    def get_filename(self):
        if self.bank == '03':
            return 'H2HH03{company_code}{service_code}{count_txt}{date_time}.txt'.format(
                company_code=self.name['company_code'],
                service_code=self.name['service_code'],
                count_txt=self.name['count_txt'],
                date_time=self.name['date_time'],
            )
        else:
            return '{name}.txt'.format(
                name=self.name['name']
            )

    @staticmethod
    def generate_tmp_dir(xmlstr):
        tmp_dir = tempfile.mkdtemp()
        with open(os.path.join(tmp_dir, 'Pago.txt'), 'w') as f:
            f.write(xmlstr)
        return tmp_dir

    def generate_zip(self, tmp_dir):
        zip_filename = os.path.join(tmp_dir, self.filename)
        with zipfile.ZipFile(zip_filename, 'w') as docx:
            docx.write(os.path.join(tmp_dir, 'Pago.txt'), 'Pago.txt')
        return zip_filename
