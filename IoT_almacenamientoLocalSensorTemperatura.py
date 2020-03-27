###Codigo creado por Luis Gerardo Sandoval Rodriguez
###Antes de comenzar se prueba que esten los modulos necesarios instalados, de lo contrario el programa salira de ejecución 
try:
	import ntplib
except ImportError:
	print("Modulo 'ntplib' no instalado")
	exit()
try:
	import pytz
except ImportError:
	print("Modulo 'pytz' no instalado")
	exit()
try:
	import pymysql
except ImportError:
	print("Modulo 'import pymysql' no instalado")
	exit()
import sys,os
import time
import datetime
import hashlib 
from random import uniform

###Funcion que hace una consulta a un servidor NTP para despues ponerla sobre la maquina en la que se corra el script 
def cambiarFechaHora():
	utc=pytz.utc

	print("hora y fecha actual antes de pedir al NPT----> "+str(datetime.datetime.now()))

	####Formato para la conversion a UTC
	fmt = '%Y-%m-%d %H:%M:%S'
	fmtt = '%Y-%m-%d %H:%M:%S.%f'
	mexico = pytz.timezone('America/Mexico_City')

	####Pide tiempo al servidor ntp
	client=ntplib.NTPClient()
	print("pidiendo hora a servidor --------------------> ntp.cais.rnp.br...")
	tiempo_salida_peticion=datetime.datetime.now()
	response=client.request('ntp.cais.rnp.br')#('europe.pool.ntp.org')
	tiempo_llegada_peticion=datetime.datetime.now()


	tiempo_respuesta_peticion=(tiempo_llegada_peticion-tiempo_salida_peticion)/2
	print(f"tiempo de respuesta de peticion -------------> {tiempo_respuesta_peticion}")
	hora_servidor=time.localtime(response.tx_time)
	#hora_servidor=time.gmtime(response.tx_time)
	print(f"hora de servidor NTP ------------------------> {hora_servidor}")


	####Cambia al formato para la conversion a UTC
	date_time=str(hora_servidor[0])+"-"+str(hora_servidor[1])+"-"+str(hora_servidor[2])+" "+str(hora_servidor[3])+":"+str(hora_servidor[4])+":"+str(hora_servidor[5])


	####Cambia hora a UTC
	dt = datetime.datetime.strptime(date_time, fmt)
	am_dt = mexico.localize(dt)
	print(am_dt)
	#hora_utc=am_dt.astimezone(utc).strftime(fmt)+",00"
	hora_utc=am_dt.strftime(fmt)+".00"

	print(f"hora sin la suma el retraso {hora_utc}")

	#hora_servidor=time.strftime(fmt,hora_servidor)+".00"

	tiempo_en_ejecucion=datetime.datetime.now()-tiempo_llegada_peticion
	print(f"tiempo de retraso de ejecucion --------------> {tiempo_en_ejecucion}")
	hora_ntp=(datetime.datetime.strptime(hora_utc, fmtt)+tiempo_respuesta_peticion+tiempo_en_ejecucion).strftime(fmtt)

	####Aplica la hora al sistema (year,month,dayOfWeek,day,hour,minute,second,millisecond)
	if sys.platform=='linux':
		os.system(f"sudo date --set \"{hora_ntp}\"")	
		print("")




###Funcion que devuelve la temperatura obtenida de un sensor, asi como la fecha y hora en el momento que fue tomada
##Nota->Los datos en este caso son generados aleatoriamente (valor de temperatura entre 16 a 37) porque no hay 
##manera de obtenerlo de un sensor real
def leerTemperatura():
	array = {}
	print("Obteniendo temperatura......")
	array['fecha'] = datetime.datetime.now().strftime("%y/%m/%d")
	array['hora'] = datetime.datetime.now().strftime("%H:%M:%S")
	array['valor'] = uniform(16, 37) 
	return array




###Funcion que retorna una firma electronica que se genera aplicando MD5 a el nombre del sensor
def generarFirma(sensor): 
	result = hashlib.md5(sensor.encode()) 
	print(f"firma del sensor generada -------------------> {result.hexdigest()}") 
	return result.hexdigest()


###Funcion que se conecta a una base de datos para guardar los registros recibidos 
def guardarDatos(id, firma, latitud, longitud, fecha, hora, variable, valor):
	DB_HOST = '127.0.0.1' 
	DB_USER = 'root' 
	DB_PASS = '' 
	DB_NAME = 'IoT_datos' 

	try:

		# Abre conexion con la base de datos
		conn = pymysql.connect(DB_HOST,DB_USER,DB_PASS,DB_NAME)

		# prepare a cursor object using cursor() method
		cursor = conn.cursor()

		query = f"Insert into clima values('{id}', '{firma}',{latitud}, {longitud}, '{fecha}','{hora}', '{variable}', '{valor}')"

		# ejecuta el SQL query usando el metodo execute().
		try:
		   cursor.execute(query)
		   conn.commit()
		   print("Datos guardados en la base de datos con exito") 
		except:
		   # Rollback en bd
		   conn.rollback()
		   print("Ocurrio un error al intertar guardar los datos en la base de datos")


		# desconecta del servidor
		cursor.close()
		conn.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		os.system('clear')
		print(f"Ocurrio un error al intentar conectar a al base de datos --> {e}")
		exit()






###Nota-> Los datos son fijos porque solo se esta simulando un sensor, que es el de temperatura, asi como la latitud y longitud de 
##donde se supone que esta localizado este sensor

sensor = 'temperatura_01'
latitud = 19.721803
longitud = -101.185790
cambiarFechaHora()

###bucle que esta "actualizando" los valores del sensor de temperatura cada 60 segundos
while(True):
	datosSensor = leerTemperatura()
	firma = generarFirma(sensor)
	guardarDatos(sensor, firma, latitud, longitud, datosSensor['fecha'], datosSensor['hora'], '2', datosSensor['valor'])
	print("---------------------------------------------------------------------------------------------------------------")
	print("\n\nEn 60 segundos se actualizara la informacion")
	time.sleep(60)
	print("\n\n---------------------------------------------------------------------------------------------------------------")






















