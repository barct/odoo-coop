
# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import re


def strip_or_none(val):
    if val is None:
        return None
    if isinstance(val, basestring):
        val = val.strip()
        if val == "":
            return None
    return val


def doc_type_equivalences(doc_type):
    if doc_type == 1:
        return "DNI"
    elif doc_type == 2:
        return "LE"
    elif doc_type == 3:
        return "LC"
    elif doc_type == 6:
        return "CUIT"
    elif doc_type == 7:
        return "PAS"
    else:
        return None


def doc_type_afip_equivalences(doc_type):
    if doc_type == 1:
        return 96
    elif doc_type == 2:
        return 89
    elif doc_type == 3:
        return 90
    elif doc_type == 6:
        return 80
    elif doc_type == 7:
        return 94
    else:
        return None


def afip_resposability_equivalences(cod_iva):
    if cod_iva == 2:  # RI
        return "1"  # IVA Responsable Inscripto
    elif cod_iva == 3:
        return "4"  # IVA Sujeto Exento
    elif cod_iva == 5:
        return "6"  # Responsable Monotributo
    else:
        return "5"  # Consumidor Final


def doc_number_normalize(doc_type, number):
    try:
        number = int(number)
    except:
        number = None

    if (number <= 1111) \
            or "11111" in str(number) \
            or number is None \
            or doc_type is None:
        dt = None
        d = None
    else:
        dt = doc_type_equivalences(doc_type)
        d = number
    return (dt, d)


def name_clean(name):
    names = name.split("-")
    name = names[0]
    name = re.sub('[*]', '', name)
    name = re.sub('\s+', ' ', name)
    return name.title()


def insert_or_update(env, model, constraints, data):
    domain = list()
    for c in constraints:
        domain.append((c, "=", constraints[c]))
    ids = env[model].search(domain)
    if ids:
        ids.write(data)
        print "old %s" % data
    else:
        data.update(constraints)
        obj = env[model].create(data)
        print "new %s" % obj
