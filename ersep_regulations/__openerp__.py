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
    'name': 'ERSeP Regulations',
    'version': '9.0.0.0.1',
    'category': 'Tools',
    'sequence': 1,
    'summary': '',
    'description': """

ERSeP Regulations 
=================

This module is a regionalization of Córdoba province for odoo-coop
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
        'electric_utility',
        'base',
        'l10n_ar_chart',
    ],
    'external_dependencies': {
 #       'python': ['dbfread', 'hashlib'],
    },
    'data': [
        'data/account_chart.xml',
        'data/account_tax.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
}
