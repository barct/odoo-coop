# -*- coding: utf8 -*-

def oprint(obj, name="<no name>"):
	if not obj is None:
		title = "Dump: " + name + " : " + unicode(type(obj))
		print title
		title = str(obj)[:255]
		print title
		print "-"*len(title)
		d = dir(obj)
		for f in d:
			try:
				print "%s : %s" % (str(f),getattr(obj, f))
			except:
				print "%s : --Error--" % (str(f))

		title = "Fin Dump: " + name
		print title
		print "-"*len(title)

	else:
		print "None"