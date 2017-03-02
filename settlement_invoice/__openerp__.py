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
    'name': 'Electric Utility Like Settlement Aeroo Report',
    'version': '9.0.0.0.1',
    'category': 'Localization/Argentina',
    'summary': '',
    'description': """

Electric Utility Like Settlement Aeroo Report
=============================================

TODO

    """,
    'author':  'Fernando Hidalgo',
    'website': 'www.hidalgofernando.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'report_extended_account',
        'l10n_ar_account',
        'l10n_ar_aeroo_base',
    ],
    'external_dependencies': {
 #       'python': ['dbfread', 'hashlib'],
    },
    'data': [
        'settlement_report.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
}