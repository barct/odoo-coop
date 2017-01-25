# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016  Fernando Hidalgo  (http://www.hidalgofernando.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Electric Public Utility',
    'version': '9.0.0.0.1',
    'category': 'Tools',
    'sequence': 1,
    'summary': '',
    'description': """

Electric Public Utility
=======================

This module implements functionality for a electric public utility.
Based on the experience of the "Cooperativa Anisacate" cooperative.
Uses the Argentine tax & legal regulations and particularly those of the province of "Córdoba"
through the regulator ERSeP.

    """,
    'author':  'Fernando Hidalgo',
    'website': 'www.hidalgofernando.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base',
 #       'coop_members',
        'l10n_ar_invoice',
    ],
    'external_dependencies': {
 #       'python': ['dbfread', 'hashlib'],
    },
    'data': [
        'views/connection_view.xml',
        'views/contrat_view.xml',
        'views/res_partner_view.xml',
        'data/afip_document_class.xml',
 #       'res_config_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'test': [
    ],
}
