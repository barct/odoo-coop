# -*- coding: utf-8 *-*
import datetime 

N = 'Numerico'      # 2
A = 'Alfanumerico'  # 3
# I = 'Importe'       # 4
C = A               # 1 (caracter alfabetico)
B = A               # 9 (blanco)

def escribir(dic, formato, contraer_fechas=False):
    """Genera una cadena dado un formato y un diccionario de claves/valores"""
    linea = " " * sum([fmt[1] for fmt in formato])
    comienzo = 1
    for fmt in formato:
        clave, longitud, tipo = fmt[0:3]
        try:
            # dec = (len(fmt) > 3 and isinstance(fmt[3], int)) and fmt[3] or 2
            if clave.capitalize() in dic:
                clave = clave.capitalize()
            s = dic.get(clave, "")

            if isinstance(s, unicode):
                s = s.encode("latin1")
            if s is None:
                valor = ""
            elif type(s) is datetime.date and longitud == 8:
                valor = s.strftime('%Y%m%d')
            else:
                valor = str(s)
            # reemplazo saltos de linea por tabulaci{on vertical
            valor = valor.replace("\n\r", "\v")\
                .replace("\n", "\v").replace("\r", "\v")
            if tipo == N and valor and valor != "NULL":
                valor = ("%%0%dd" % longitud) % long(valor)
            # elif tipo == I and valor:
            #     valor = ("%%0%d.%df" % (longitud + 1, dec)
            #              % float(valor)).replace(".", "")
            elif contraer_fechas \
                    and clave.lower().startswith("fec") \
                    and longitud <= 8 \
                    and valor:
                valor = valor.replace("-", "")
            else:
                valor = ("%%-0%ds" % longitud) % valor
            linea = linea[:comienzo - 1] \
                + valor \
                + linea[comienzo - 1 + longitud:]
            comienzo += longitud
        except Exception, e:
            raise Exception("Error al escribir campo %s pos %s val '%s': %s"
                            % (clave, comienzo, valor, str(e)))
    return linea + "\n"


def format_as_dict(format):
    return dict([(k[0], None) for k in format])


def escribir_sp(vals):
    return escribir(vals, LIQUIDACION_SP)


LIQUIDACION_SP = [
    ('cbte_tipo', 2, N),
    ('pto_vta', 5, N),
    ('cbt_numero', 8, N),
    ('cbte_nro_interno', 50, A),
    ('fecha_cbte', 8, N),
    ('tipo_servicio', 1, C),

    ('usuario_tiene_info', 1, C),
    ('usuario_tipo_doc', 2, N),
    ('usuario_nro_doc', 20, A),
    ('usuario_nombre', 50, A),
    ('usuario_id', 50, A),
    ('usuario_impositiva_id', 2, N),
    ('usuario_es_propietario', 1, C),

    ('titular_tiene_info', 1, C),
    ('titular_tipo_doc', 2, N),
    ('titular_nro_doc', 20, A),
    ('titular_nombre', 50, A),
    ('titular_impositiva_id', 2, N),
    ('titular_es_propietario', 1, C),

    ('titular_inmueble_tiene_info', 1, C),
    ('titular_inmueble_tipo_doc', 2, N),
    ('titular_inmueble_nro_doc', 20, A),
    ('titular_inmueble_nombre', 50, A),

    ('usuario_domicilio_tiene_info', 1, C),
    ('usuario_domicilio_calle', 30, A),
    ('usuario_domicilio_puerta', 6, A),
    ('usuario_domicilio_piso', 5, A),
    ('usuario_domicilio_oficina', 5, A),
    ('usuario_domicilio_cp', 8, A),
    ('usuario_domicilio_localidad', 30, A),
    ('usuario_domicilio_partido', 50, A),
    ('usuario_domicilio_provincia', 2, N),

    ('titular_domicilio_tiene_info', 1, C),
    ('titular_domicilio_calle', 30, A),
    ('titular_domicilio_puerta', 6, A),
    ('titular_domicilio_piso', 5, A),
    ('titular_domicilio_oficina', 5, A),
    ('titular_domicilio_cp', 8, A),
    ('titular_domicilio_localidad', 30, A),
    ('titular_domicilio_partido', 50, A),
    ('titular_domicilio_provincia', 2, N),

    ('inmueble_domicilio_tiene_info', 1, C),
    ('inmueble_domicilio_calle', 30, A),
    ('inmueble_domicilio_puerta', 6, A),
    ('inmueble_domicilio_piso', 5, A),
    ('inmueble_domicilio_oficina', 5, A),
    ('inmueble_domicilio_cp', 8, A),
    ('inmueble_domicilio_localidad', 30, A),
    ('inmueble_domicilio_partido', 50, A),
    ('inmueble_domicilio_provincia', 2, N),
    ('inmueble_catastral', 98, A),

    ('servicio_periodicidad', 1, N),
    ('servicio_periodo_desde', 8, N),
    ('servicio_periodo_hasta', 8, N),

    ('vencimiento_1', 8, N),
    ('vencimiento_2', 8, N),

    ('tarifaria_categoria', 50, A),
    ('tarifaria_subcategoria', 50, A),

    ('consumo_cantidad', 15, N),
    ('consumo_tipo', 1, N),

    ('recibe_subsidio', 1, C),
    ('cargo_fijo_sin_subsidio', 15, N),
    ('cargo_variable_sin_subsidio', 15, N),
    ('cargo_fijo_con_subsidio', 15, N),
    ('cargo_variable_con_subsidio', 15, N),

    ('neto_gravado_signo_1er', 1, C),
    ('neto_gravado_1er', 15, N),

    ('iva_1er_signo', 1, C),
    ('iva_1er', 15, N),
    ('iva_alicuota', 1, N),

    ('total_no_gravados_signo_1er', 1, C),
    ('total_no_gravados_1er', 15, N),

    ('neto_excentas_signo_1er', 1, C),
    ('neto_excentas_1er', 15, N),

    ('percepciones_signo_1er', 1, C),
    ('percepciones_1er', 15, N),

    ('ingresos_brutos_signo_1er', 1, C),
    ('ingresos_brutos_1er', 15, N),

    ('municipal_signo_1er', 1, C),
    ('municipal_1er', 15, N),

    ('internos_signo_1er', 1, C),
    ('internos_1er', 15, N),

    ('otros_nacionales_signo_1er', 1, C),
    ('otros_nacionales_1er', 15, N),

    ('otros_provinciales_signo_1er', 1, C),
    ('otros_provinciales_1er', 15, N),

    ('neto_gravado_signo_1er', 1, C),
    ('neto_gravado_1er', 15, N),

    ('total_signo_1er', 1, C),
    ('total_1er', 15, N),

    ('total_signo_2do', 1, C),
    ('total_2do', 15, N),

    ('recargo_iva_signo_2do', 1, C),
    ('recargo_iva_1er', 15, N),

    ('percepciones_signo_2do', 1, C),
    ('percepciones_2er', 15, N),

    ('otros_signo_2do', 1, C),
    ('otros_2do', 15, N),

    ('otros_gravados_signo', 1, C),
    ('otros_gravados', 15, N),

    ('iva_signo', 1, C),
    ('iva', 15, N),

    ('exentos_signo', 1, C),
    ('exentos', 15, N),

    ('otros_triutos', 1, C),
    ('otros_tributos', 15, N),

    ('importe_final_signo_1er', 1, C),
    ('importe_final_1er', 15, N),

    ('importe_final_signo_2do', 1, C),
    ('importe_final_2do', 15, N),

    ('terceros_neto_gravado_signo', 1, C),
    ('terceros_neto_gravado', 15, N),

    ('terceros_iva_signo', 1, C),
    ('terceros_iva', 15, N),
    ('terceros_iva_alicuota', 1, N),

    ('terceros_otros_signo', 1, C),
    ('terceros_otros', 15, N),

]
