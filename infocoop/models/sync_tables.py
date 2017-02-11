# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from dbfread import DBF
import hashlib
import utils
from sys import stdout
import logging
import datetime
_logger = logging.getLogger(__name__)

DEBUG = True


ACCOUNT_INITIAL_DATE_SYNC = datetime.date(year=2017, month=1, day=1)


class mirror_table_base():
	"""
	Class mirror table
		is a base class for mirroring dbf of Infcooop system... and other stuff 
	"""
	hashcode = fields.Char(length=15)
	sync_version = fields.Integer(default=0, required=True)
	sync_delete_mark = fields.Boolean(default=False, required=True) 

	dbf_table = None

	def get_last_version(self):
		self.env.cr.execute("SELECT MAX(sync_version) FROM %s" % self._table)
		return self.env.cr.fetchone()[0] or 0


	def generateHash(self, rowdata):
		"""
		generate a hash code based on a raw row
		"""
		hash = hashlib.sha1()
		hash.update(str(rowdata))
		self.hashcode=hash.hexdigest()[-10:]
		return self.hashcode

	def checkHash(self, rowdata):
		"""
		check if row data maches the hash
		"""
		hash = hashlib.sha1()
		hash.update(str(rowdata))
		if self.hashcode==hash.hexdigest()[-10:]:
			return True
		else:
			return False

	def dbf_rows(self):
		"""
		iterate in every rows
		This method should be overwritten in a subclass to filter rows
		"""
		count = 0
		if DEBUG: total = len(self.dbf_table)
		for row in self.dbf_table:
				yield row
				if DEBUG:
					stdout.write("\r %s: %i de %i" % (self.dbf_tablename,count,total))
					stdout.flush()
					count += 1

	def sync(self):
		"""
		here's the magic
		Gets all rows in the dbf file and verifies that they are loaded in the model
		"""
		model = self._name
		path = self.env["infocoop_configuration"].get_dbf_path()
		dbf_tablename = path + "/" + self.dbf_tablename + '.dbf'
		self.dbf_table = DBF(dbf_tablename)

		##fields OPERADOR cause parse problems :(
		for field in self.dbf_table.fields:
			if field.name=="OPERADOR": 
				field.type="0"

		sync_version = self.get_last_version()+1

		for row in self.dbf_rows():
			pklist = []
			for pk in self.dbf_pk:
				pklist.append((pk,"=",utils.strip_or_none(row[pk.upper()])))
			ids = self.env[model].search(pklist, limit=1)
			if ids:
				is_changed = not (ids.checkHash(unicode(row)))
				if is_changed:
					ids.write_row(row, self.dbf_table, sync_version)
				else:
					ids.sync_version = sync_version
			else:
				new = self.env[model].create({})
				new.write_row(row, self.dbf_table, sync_version)

		#remove non exist records
		self.env.cr.execute("UPDATE %s SET sync_delete_mark=(sync_version < %i)" % (self._table,sync_version))
		self.post_process()


	def write_row(self, dbf_row, dbf_table, sync_version):
		'''
		write dbf row in the model
		'''
		write_dict={}
		for f in self._fields: #dbf_table.fields:
			if f.upper() in [x.name for x in dbf_table.fields]:
				write_dict[f]=utils.strip_or_none(dbf_row[f.upper()])
		write_dict["sync_version"]=sync_version
		self.write(write_dict)
		self.generateHash(unicode(dbf_row))

	def post_process(self):
		return
			

class infocoop_ingresos(models.Model, mirror_table_base):
	'''
	This model is a mirror of a table ingresos in InfoCoop system
	ingresos represent the members in a cooperative
	Not to be confused with socios table. This last one represent a service connections
	(... yes, this guys are awesome :O )
	'''

	dbf_tablename = "ingresos"
	dbf_pk = ("socio","medidor","orden")

	nombre = fields.Char(string='nombre',length=30)
	cuotas = fields.Integer(string='cuotas')
	pesos = fields.Float(string='pesos')
	contado = fields.Float(string='contado')
	cuotas_men = fields.Integer(string='cuotas_men')
	profesion = fields.Char(string='profesion',length=30)
	nacionalid = fields.Char(string='nacionalid',length=15)
	tipo_doc = fields.Integer(string='tipo_doc')
	nro_doc = fields.Char(string='nro_doc')
	telefono = fields.Char(string='telefono',length=15)
	dirser = fields.Char(string='dirser',length=30)
	domicilio = fields.Char(string='domicilio',length=60)
	localidad = fields.Integer(string='localidad')
	fec_nacim = fields.Date(string='fec_nacim')
	estado_civ = fields.Integer(string='estado_civ')
	padre = fields.Char(string='padre',length=30)
	madre = fields.Char(string='madre',length=30)
	conyugue = fields.Char(string='conyugue',length=30)
	sector = fields.Integer(string='sector')
	socio = fields.Char(string='socio', index=True)
	acta = fields.Integer(string='acta')
	fec_acta = fields.Date(string='fec_acta')
	fec_ingr = fields.Date(string='fec_ingr')
	observacio = fields.Text(string='observacio')
	aceptado = fields.Boolean(string='aceptado')
	barrio = fields.Integer(string='barrio')
	medidor = fields.Char(string='medidor')
	orden = fields.Char(string='orden',length=1)
	fec_baja = fields.Date(string='fec_baja')
	codpostal = fields.Char(string='codpostal',length=15)
	sexo = fields.Char(string='sexo',length=1)

	_sql_constraints = [('unique_keys', 'unique(socio,medidor,orden)', 'must be unique!'),]


	def dbf_rows(self):
		for row in super(infocoop_ingresos, self).dbf_rows():
			if row["FEC_BAJA"] is None:
				yield row


class infocoop_tablas(models.Model, mirror_table_base):

	dbf_tablename = "tablas"
	dbf_pk = ("tema","subtema","codigo","subcodigo")

	tema = fields.Char(string='tema',length=1)
	subtema = fields.Char(string='subtema',length=1)
	codigo = fields.Char(string='codigo',length=4)
	subcodigo = fields.Char(string='subcodigo',length=6)
	concepto = fields.Char(string='concepto',length=50)
	cantidad = fields.Char(string='cantidad',length=4)
	valor = fields.Float(string='valor')
	venc_1 = fields.Date(string='venc_1')
	recar_1 = fields.Float(string='recar_1')
	venc_2 = fields.Date(string='venc_2')
	recar_2 = fields.Float(string='recar_2')
	venc_3 = fields.Date(string='venc_3')
	recar_3 = fields.Float(string='recar_3')
	actualizar = fields.Float(string='actualizar')
	editable = fields.Boolean(string='editable')
	imputacion = fields.Char(string='imputacion',length=25)
	observacio = fields.Text(string='observacio')
	paragrupos = fields.Char(string='paragrupos',length=1)
	grafico = fields.Binary(string='grafico')

	_sql_constraints = [('unique_keys', 'unique(tema,subtema,codigo,subcodigo)', 'must be unique!'),]


class infocoop_liquidac(models.Model, mirror_table_base):

	dbf_tablename = "liquidac"
	dbf_pk = ("medidor","orden","periodo")

	_sql_constraints = [('unique_keys', 'unique(medidor,orden,periodo)', 'must be unique!'),]

	barrio = fields.Integer(string='barrio')
	medidor = fields.Char(string='medidor')
	orden = fields.Char(string='orden',length=1)
	periodo = fields.Char(string='periodo',length=7)
	numero = fields.Integer(string='numero')
	cons_ee = fields.Integer(string='cons_ee')
	imp_ee = fields.Float(string='imp_ee')
	cargo_fijo = fields.Float(string='cargo_fijo')
	serv_soc = fields.Float(string='serv_soc')
	imp_nac1 = fields.Float(string='imp_nac1')
	rec_muni = fields.Float(string='rec_muni')
	codiv = fields.Integer(string='codiv')
	iva1 = fields.Float(string='iva1')
	iva2 = fields.Float(string='iva2')
	ivc1 = fields.Float(string='ivc1')
	ivc2 = fields.Float(string='ivc2')
	cta_cap = fields.Float(string='cta_cap')
	neto_imp = fields.Float(string='neto_imp')
	neto_serv = fields.Float(string='neto_serv')
	servicios = fields.Char(string='servicios',length=10)
	categorias = fields.Char(string='categorias',length=12)
	num_fact = fields.Char(string='num_fact',length=14)

	def dbf_rows(self):
		for row in super(infocoop_liquidac, self).dbf_rows():
			try:
				year =  int(row["PERIODO"][-4:])
				month =  int(row["PERIODO"][:2])
				date = datetime.date(year=year, month=month, day=1)
			except:
				continue
			if  date >= ACCOUNT_INITIAL_DATE_SYNC:
				yield row

class infocoop_auxiliar(models.Model, mirror_table_base):

	dbf_tablename = "auxiliar"
	dbf_pk = ("medidor","orden","periodo","item")

	_sql_constraints = [('unique_keys', 'unique(medidor,orden,periodo,item)', 'must be unique!'),]

	barrio = fields.Integer(string='barrio')
	medidor = fields.Char(string='medidor')
	orden = fields.Char(string='orden',length=1)
	periodo = fields.Char(string='periodo',length=7)
	item = fields.Char(string='item')
	concepto = fields.Char(string='concepto',length=60)
	cantidad = fields.Float(string='cantidad')
	importe = fields.Float(string='importe')
	cond_iva = fields.Char(string='cond_iva',length=1)
	cta_cap = fields.Char(string='cta_cap',length=1)
	var_auxi = fields.Char(string='var_auxi',length=1)
	nro_orden = fields.Integer(string='nro_orden')

	def dbf_rows(self):
		for row in super(infocoop_auxiliar, self).dbf_rows():
			try:
				year =  int(row["PERIODO"][-4:])
				month =  int(row["PERIODO"][:2])
				date = datetime.date(year=year, month=month, day=1)
			except:
				continue
			if  date >= ACCOUNT_INITIAL_DATE_SYNC:
				yield row

class infocoop_ctacte(models.Model, mirror_table_base):

	dbf_tablename = "ctacte"
	dbf_pk = ("medidor","orden","periodo")

	_sql_constraints = [('unique_keys', 'unique(medidor,orden,periodo)', 'must be unique!'),]

	barrio = fields.Integer(string='barrio')
	medidor = fields.Char(string='medidor')
	orden = fields.Char(string='orden',length=1)
	periodo = fields.Char(string='periodo',length=7)
	fecha = fields.Date(string='fecha')
	banco = fields.Integer(string='banco')
	apagar = fields.Float(string='apagar')
	pagado = fields.Float(string='pagado')
	servicios = fields.Char(string='servicios',length=10)
	sininteres = fields.Float(string='sininteres')

	def dbf_rows(self):
		for row in super(infocoop_ctacte, self).dbf_rows():
			try:
				year =  int(row["PERIODO"][-4:])
				month =  int(row["PERIODO"][:2])
				date = datetime.date(year=year, month=month, day=1)
			except:
				continue
			if date >= ACCOUNT_INITIAL_DATE_SYNC:
				yield row


class infocoop_tab_fact(models.Model, mirror_table_base):

	dbf_tablename = "tab_fact"
	dbf_pk = ("periodo",)

	_sql_constraints = [('unique_keys', 'unique(periodo)', 'must be unique!'),]

	periodo = fields.Char(string='periodo',length=7)
	venc_1 = fields.Date(string='venc_1')
	recargo1 = fields.Float(string='recargo1')
	venc_2 = fields.Date(string='venc_2')
	recargo = fields.Float(string='recargo')
	venc_3 = fields.Date(string='venc_3')
	recargo3 = fields.Float(string='recargo3')
	reparto = fields.Date(string='reparto')
	observacio = fields.Text(string='observacio')
	prox_venc = fields.Date(string='prox_venc')

	def dbf_rows(self):
		for row in super(infocoop_tab_fact, self).dbf_rows():
			try:
				year =  int(row["PERIODO"][-4:])
				month =  int(row["PERIODO"][:2])
				date = datetime.date(year=year, month=month, day=1)
			except:
				continue
			print year
			if  date >= ACCOUNT_INITIAL_DATE_SYNC:
				yield row


class infocoop_socios(models.Model, mirror_table_base):
	dbf_tablename = "socios"
	dbf_pk = ("medido","orden")

	_sql_constraints = [('unique_keys', 'unique(medido, orden)', 'must be unique!'),]

	sector = fields.Integer(string='sector')
	nrosoc = fields.Integer(string='nrosoc', index=True)
	codint = fields.Char(string='codint',length=2)
	secuencia = fields.Char(string='secuencia',length=10)
	cod2 = fields.Char(string='cod2',length=2)
	corte = fields.Char(string='corte',length=1)
	usuario3 = fields.Char(string='usuario3',length=1)
	activo = fields.Char(string='activo',length=1)
	barrio = fields.Integer(string='barrio')
	medido = fields.Integer(string='medido')
	orden = fields.Char(string='orden',length=1)
	nombre = fields.Char(string='nombre',length=30)
	direccion = fields.Char(string='direccion',length=40)
	codpostal = fields.Char(string='codpostal',length=8)
	codloca = fields.Integer(string='codloca')
	codiva = fields.Integer(string='codiva')
	catene = fields.Integer(string='catene')
	bonesp = fields.Integer(string='bonesp')
	codsep = fields.Char(string='codsep',length=1)
	adherentes = fields.Integer(string='adherentes')
	fec_inag = fields.Date(string='fec_inag')
	cuit = fields.Char(string='cuit',length=13)
	ing_brutos = fields.Char(string='ing_brutos',length=13)
	nrotel = fields.Integer(string='nrotel')
	dirser = fields.Char(string='dirser',length=30)
	nromedluz = fields.Char(string='nromedluz',length=15)
	fec_inen = fields.Date(string='fec_inen')
	hasta = fields.Date(string='hasta')
	avisado = fields.Char(string='avisado',length=1)
	observacio = fields.Text(string='observacio')
	des_ee = fields.Char(string='des_ee',length=7)
	has_ee = fields.Char(string='has_ee',length=7)
	cuenta = fields.Integer(string='cuenta')
	sec_estado = fields.Char(string='sec_estado',length=10)
	telefono = fields.Char(string='telefono',length=20)
	e_mail = fields.Char(string='e_mail',length=40)
	sucursalcb = fields.Char(string='sucursalcb',length=3)
	codigocbu = fields.Char(string='codigocbu',length=22)
	cuentacbu = fields.Char(string='cuentacbu',length=10)
	tipocbu = fields.Char(string='tipocbu',length=1)
	decl_jur = fields.Char(string='decl_jur',length=20)
	catcab = fields.Integer(string='catcab')

	def dbf_rows(self):
		for row in super(infocoop_socios, self).dbf_rows():
			if row["ORDEN"] in ["E","F","G","H","I","J","K","L","M"]:
				yield row

class infocoop_modi_soc(models.Model, mirror_table_base):
	dbf_tablename = "modi_soc"
	dbf_pk = ("medidor","orden","campo","fecha","hora")

	_sql_constraints = [('unique_keys', 'unique(medidor, orden, campo, fecha, hora)', 'must be unique!'),]

	barrio = fields.Integer(string='barrio')
	medidor = fields.Integer(string='medidor')
	orden = fields.Char(string='orden',length=1)
	campo = fields.Char(string='campo',length=10)
	anterior = fields.Char(string='anterior',length=50)
	actual = fields.Char(string='actual',length=50)
	fecha = fields.Date(string='fecha')
	base = fields.Integer(string='base')
	motivo = fields.Char(string='motivo',length=20)
	hora = fields.Integer(string='hora')

	def dbf_rows(self):
		for row in super(infocoop_modi_soc, self).dbf_rows():
			if row["MEDIDOR"]>0 and not row["CAMPO"] is None and row["ORDEN"] in ["E","F","G","H","I","J","K","L","M"]:
				yield row


class infocoop_red_usu(models.Model, mirror_table_base):
	dbf_tablename = "red_usu"
	dbf_pk = ("medidor","orden")

	_sql_constraints = [('unique_keys', 'unique(medidor, orden)', 'must be unique!'),]


	barrio = fields.Integer(string='barrio')
	medidor = fields.Integer(string='medidor')
	orden = fields.Char(string='orden',length=1)
	servicio = fields.Char(string='servicio',length=2)
	zona = fields.Char(string='zona',length=4)
	fec_inst = fields.Date(string='fec_inst')
	detalle = fields.Text(string='detalle')
	nromedidor = fields.Char(string='nromedidor',length=15)
	marcamed = fields.Char(string='marcamed',length=20)
	tipo_med = fields.Integer(string='tipo_med')
	tipo = fields.Char(string='tipo',length=10)
	multiplica = fields.Float(string='multiplica')
	desig_cat = fields.Char(string='desig_cat',length=30)
	latitud = fields.Char(string='latitud',length=10)
	longitud = fields.Char(string='longitud',length=10)

	def dbf_rows(self):
		for row in super(infocoop_red_usu, self).dbf_rows():
			if row["MEDIDOR"]>0:
				yield row


class infocoop_suscrip(models.Model, mirror_table_base):
	dbf_tablename = "suscrip"
	dbf_pk = ("nrosoc",)

	_sql_constraints = [('unique_keys', 'unique(nrosoc)', 'must be unique!'),]

	barrio = fields.Integer(string='barrio')
	medidor = fields.Integer(string='medidor')
	orden = fields.Char(string='orden',length=1)
	servicio = fields.Char(string='servicio',length=2)
	fecha = fields.Date(string='fecha')
	cuotas = fields.Integer(string='cuotas')
	indice = fields.Integer(string='indice')
	capital = fields.Float(string='capital')
	sector = fields.Integer(string='sector')
	nrosoc = fields.Integer(string='nrosoc')
	contado = fields.Float(string='contado')
	ctas_soc = fields.Integer(string='ctas_soc')
	acta = fields.Integer(string='acta')
	fec_acta = fields.Date(string='fec_acta')
	observacio = fields.Text(string='observacio')
	nro_cert = fields.Integer(string='nro_cert')


class infocoop_estados(models.Model, mirror_table_base):
	dbf_tablename = "estados"
	dbf_pk = ("medidor","orden", "mes", "anio")

	_sql_constraints = [('unique_keys', 'unique(medidor, orden, mes, anio)', 'must be unique!'),]

	barrio = fields.Integer(string='barrio')
	medidor = fields.Integer(string='medidor')
	orden = fields.Char(string='orden',length=1)
	mes = fields.Integer(string='mes')
	catagua = fields.Integer(string='catagua')
	anio = fields.Integer(string='anio')
	luz_ant = fields.Integer(string='luz_ant')
	luz_act = fields.Integer(string='luz_act')
	ag_ant = fields.Integer(string='ag_ant')
	ag_act = fields.Integer(string='ag_act')
	deudores = fields.Float(string='deudores')
	acciones = fields.Float(string='acciones')
	correo = fields.Float(string='correo')
	alumbrado = fields.Float(string='alumbrado')
	varios = fields.Float(string='varios')
	varios2 = fields.Float(string='varios2')
	varios3 = fields.Float(string='varios3')
	varios4 = fields.Float(string='varios4')
	varios5 = fields.Float(string='varios5')
	varios6 = fields.Float(string='varios6')
	tomo = fields.Char(string='tomo',length=3)
	fecha = fields.Char(string='fecha',length=20)

	def dbf_rows(self):
		for row in super(infocoop_estados, self).dbf_rows():
			try:
				year =  int(row["PERIODO"][-4:])
				month =  int(row["PERIODO"][:2])
				date = datetime.date(year=year, month=month, day=1)
			except:
				continue
			print year
			if  date >= ACCOUNT_INITIAL_DATE_SYNC:
				yield row


class infocoop_acciones(models.Model, mirror_table_base):

	dbf_tablename = "acciones"
	dbf_pk = ("nrosoc","cuota")

	_sql_constraints = [('unique_keys', 'unique(nrosoc, cuota)', 'must be unique!'),]
	barrio = fields.Integer(string='barrio')
	medidor = fields.Integer(string='medidor')
	orden = fields.Char(string='orden',length=1)
	servicio = fields.Char(string='servicio',length=2)
	cuota = fields.Integer(string='cuota')
	importe = fields.Float(string='importe')
	ajuste = fields.Float(string='ajuste')
	indice = fields.Float(string='indice')
	periodo = fields.Char(string='periodo',length=7)
	fecha = fields.Date(string='fecha')
	recibo = fields.Char(string='recibo',length=10)
	sector = fields.Integer(string='sector')
	nrosoc = fields.Integer(string='nrosoc')
	fec_suscri = fields.Date(string='fec_suscri')


	def dbf_rows(self):
		for row in super(infocoop_acciones, self).dbf_rows():
			if row["NROSOC"]<9000:
				yield row