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
    'name': 'Infoocoop Afip Patch',
    'version': '9.0.0.0.1',
    'category': 'Tools',
    'sequence': 1,
    'summary': '',
    'description': """
Infoocoop Afip Patch
====================
This module implements requirements for Afip urgently.
In the future is package will be necessary
""",
    'author': 'Fernando Hidalgo',
    'website': 'www.hidalgofernando.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'infocoop',
        'electric_utility',
        'l10n_ar_chart',
    ],
    'external_dependencies': {
        # 'python': ['dbfread', 'hashlib'],
    },
    'data': [
        'views/infocoop_tab_fact_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
}
