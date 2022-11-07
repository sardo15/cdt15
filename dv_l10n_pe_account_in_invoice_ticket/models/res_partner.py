from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_pe_document_type_code = fields.Char(
        related="l10n_latam_identification_type_id.l10n_pe_vat_code")
