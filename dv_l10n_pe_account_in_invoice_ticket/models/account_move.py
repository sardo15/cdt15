from odoo import api, fields, tools, models, _
from importlib import reload
import sys
try:
    import qrcode
    qr_mod = True
except:
    qr_mod = False
from base64 import encodestring
from io import StringIO, BytesIO
from num2words import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_in_text = fields.Char(
        string="Amount in Words", compute='_compute_amount_in_text')

    @api.depends('amount_total', 'currency_id')
    def _compute_amount_in_text(self):
        """Transform the amount to text
        """
        for move in self:
            amount_base, amount = divmod(move.amount_total, 1)
            amount = round(amount, 2)
            amount = int(round(amount * 100, 2))

            lang_code = self.env.context.get('lang') or self.env.user.lang
            lang = self.env['res.lang'].search([('code', '=', lang_code)])
            words = num2words(amount_base, lang=lang.iso_code)
            # WITH
            result = _('%(words)s CON %(amount)02d/100 %(currency_label)s') % {
                'words': words,
                'amount': amount,
                'currency_label': move.currency_id.name == 'PEN' and 'SOLES' or move.currency_id.currency_unit_label,
            }
            move.amount_in_text = result.upper()

    l10n_latam_document_name = fields.Char(
        'Nombre del documento', compute='_get_latam_doc_name')

    l10n_pe_sunat_qr_code = fields.Char(
        'Peruvian QR Code', compute='_compute_l10n_pe_sunat_qr_code')

    l10n_pe_edi_serie = fields.Char(
        string='Serie', compute='_get_einvoice_number')
    l10n_pe_edi_number = fields.Char(
        string='Correlativo', compute='_get_einvoice_number')

    def _get_einvoice_number(self):
        for move in self:
            if move.name:
                inv_number = move.name.split('-')
            else:
                inv_number = []
            if move.name and move.move_type != 'entry' and len(inv_number) == 2:
                inv_serie = inv_number[0].split(' ')
                if len(inv_serie) == 2:
                    serie = inv_serie[1]
                else:
                    serie = inv_number[0]
                move.l10n_pe_edi_serie = serie
                move.l10n_pe_edi_number = inv_number[1]
            else:
                move.l10n_pe_edi_serie = False
                move.l10n_pe_edi_number = False

    @api.depends('name', 'l10n_pe_edi_serie', 'l10n_pe_edi_number', 'amount_tax', 'amount_total', 'invoice_date', 'partner_id.vat', 'partner_id.l10n_pe_document_type_code', 'company_id.partner_id.vat')
    def _compute_l10n_pe_sunat_qr_code(self):
        for invoice in self:
            if invoice.name == '/':
                l10n_pe_sunat_qr_code = ''
            elif len(invoice.name.split('-')) > 1 and invoice.invoice_date:
                res = [
                    invoice.company_id.partner_id.vat or '-',
                    invoice.l10n_latam_document_type_id.code or '',
                    invoice.l10n_pe_edi_serie or '',
                    invoice.l10n_pe_edi_number or '',
                    str(invoice.amount_tax),  # igv?
                    str(invoice.amount_total),
                    fields.Date.to_string(invoice.invoice_date),
                    invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '-',
                    invoice.partner_id.vat or '-'
                    ]
                l10n_pe_sunat_qr_code = '|'.join(res)
            else:
                l10n_pe_sunat_qr_code = ''
            invoice.l10n_pe_sunat_qr_code = l10n_pe_sunat_qr_code

    @api.depends('l10n_latam_document_type_id')
    def _get_latam_doc_name(self):
        for record in self:
            if record.l10n_latam_document_type_id:
                doc_name = record.l10n_latam_document_type_id.name
            else:
                doc_name = False
            record.l10n_latam_document_name = doc_name

    def _get_address_details(self, partner):
        self.ensure_one()
        address = ''
        if partner.l10n_pe_district:
            address = "%s" % (partner.l10n_pe_district.name)
        if partner.city:
            address += ", %s" % (partner.city)
        if partner.state_id.name:
            address += ", %s" % (partner.state_id.name)
        if partner.zip:
            address += ", %s" % (partner.zip)
        if partner.country_id.name:
            address += ", %s" % (partner.country_id.name)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False

    def _get_street(self, partner):
        self.ensure_one()
        address = ''
        if partner.street:
            address = "%s" % (partner.street)
        if partner.street2:
            address += ", %s" % (partner.street2)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False

    def print_invoice_ticket_format(self):
        return self.env.ref('dv_account_ticket_format.report_sale_ticket_format').report_action(self)
