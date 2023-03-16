from __future__ import print_function
from flask import Flask
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

import os.path
import connections
Scope = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/spreadsheets']

app = Flask(__name__)

#Función que checa si las credenciales son correctas
def checkCredentials():
	creds = None
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', Scope)

	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())

		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', Scope)
			creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('token.json', 'w') as token:
				token.write(creds.to_json())
	return creds

#Función para actualizar el estado de la cita (update)
#Parametros
#id: int identificador de la cita a modificar
#newStatus: int 0-3 posición en la lista de status con el valor deseado
@app.route("/updateStatus/<id>/<newStatus>")
def POST_updateStatus(id, newStatus):
	creds = checkCredentials()
	status = ['Programada', 'Confirmada', 'Realizada', 'Cancelada']
	data_range = connections.Cita_range
	try:
		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'

		#Obtiene la hoja completa, y luego cambiar el valor 
		sheet = service.spreadsheets()
		result = sheet.values().get(spreadsheetId=connections.Cita,
					range=data_range).execute()
		payload = result.get('values', [])

		index = int(id) - 1
		payload[index][3] = status[int(newStatus)]

		value_range_body = {
			'values': payload
		}
		request = sheet.values().update(spreadsheetId=connections.Cita, range=data_range, valueInputOption=value_input_option, body=value_range_body)
		request.execute()

		return 'estatus cita actualizado'
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content

#Endpoint para registrar acceso (write) 
#Parametros
#id_usuario: string matrícula del alumno o colaborador que ingresó
#id_sensor: int identificador único del sensor 
#date: string fecha del acceso formato de la fecha: DD-MM-AAAA 
@app.route("/registrarAcceso/<id_usuario>/<id_sensor>/<date>")
def POST_RegistrarAcceso(id_usuario, id_sensor, date):
	creds = checkCredentials()

	try:
		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'
		insert_data_option = 'INSERT_ROWS'
		data_range = 'Sheet1!A2:C'

		#Lista para mandar los datos a la hoja de cálculo, tiene que tener el tamaño y acomodo igual a la hoja de cálculo
		payload = [id_usuario, id_sensor, date]

		#Se convierte en un diccionario para poder ser mandado como JSON
		value_range_body = {
			'values': [payload]
		}
		
		request = service.spreadsheets().values().append(spreadsheetId=connections.Acesso, range=data_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
		request.execute()

		return "acceso registrado"
	
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content

#Funcion para obtener el tamaño de una hoja (read)
#Parametros
#nombre_hoja: string tiene que ser igual al nombre dado en el archivo connections.py
def GET_lenght(nombre_hoja):
	creds = checkCredentials()

	try:
		service = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file('token.json', Scope))

		sheet = service.spreadsheets()
		result = sheet.values().get(spreadsheetId=getattr(connections, nombre_hoja),
					range=getattr(connections, (nombre_hoja + '_range'))).execute()
		values = result.get('values', [])

		if not values:
			return 'No data found.'
		else:
			return [len(values)]
		
	except HttpError as err:
		return err.content


#Función para guardar cita en la hoja de cálculo CITA
#Parametros
#id: int int identificador de la cita a registrar
#formato: string tipo de la cita que se va a hacer 
#recurrencia: string cada cuanto se va a repetir
#status: string por default es "Programada" 
#tipo: string que tipo de cita es, grupal o individual
#tipo_atencion: string, tipo de atención que se le va a dar, consulta, clase, taller u otros
def POST_cita(id, formato, recurrencia, status, tipo, tipo_atencion):
	creds = checkCredentials()

	try:
		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'
		insert_data_option = 'INSERT_ROWS'
		data_range = connections.Cita_range

		payload = [id, formato, recurrencia, status, tipo, tipo_atencion]

		value_range_body = {
			'values': [payload]
		}
		
		request = service.spreadsheets().values().append(spreadsheetId=connections.Cita, range=data_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
		request.execute()

		return "cita registrada"
	
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content

#Función para registrar hora de inicio de la cita
#Parametros
#id: int identificador único
#hora: int formato HH
#minuto: int formato MM
#horaCompleta: string formato HH:MM
def POST_horaInicio(id, hora, minuto, horaCompleta):
	creds = checkCredentials()
	try:
		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'
		insert_data_option = 'INSERT_ROWS'
		data_range = connections.Hora_Inicio_range

		payload = [id, hora, minuto, horaCompleta]

		value_range_body = {
			'values': [payload]
		}
		
		request = service.spreadsheets().values().append(spreadsheetId=connections.Hora_Inicio, range=data_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
		request.execute()

		return "hora inicio registrada"
	
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content


#Función para registrar hora de terminación de la cita
#Parametros
#id: int identificador único
#hora: int formato HH
#minuto: int formato MM
#horaCompleta: string formato HH:MM
def POST_horaFin(id, hora, minuto, horaCompleta):
	creds = checkCredentials()

	try:
		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'
		insert_data_option = 'INSERT_ROWS'
		data_range = connections.Hora_Fin_range

		payload = [id, hora, minuto, horaCompleta]

		value_range_body = {
			'values': [payload]
		}
		
		request = service.spreadsheets().values().append(spreadsheetId=connections.Hora_Fin, range=data_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
		request.execute()

		return "hora fin registrada"
	
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content


#Función para registrar fecha de inicio de la cita
#Parametros
#id: int identificador único
#dia: int usar 2 dígitos para decir el día
#mes: int usar 2 dígitos para ingresar el mes
#anio: int año 
#fecha: string fecha completa usar DD-MM-AAAA
def POST_fechaInicio(id, dia, mes, anio, fecha):
	creds = checkCredentials()

	try:
		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'
		insert_data_option = 'INSERT_ROWS'
		data_range = connections.Fecha_Inicio_range

		payload = [id, dia, mes, anio, fecha]

		value_range_body = {
			'values': [payload]
		}
		
		request = service.spreadsheets().values().append(spreadsheetId=connections.Fecha_Inicio, range=data_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
		request.execute()

		return "fecha inicio registrada"
	
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content

#Función para registrar fecha de fin de la cita
#Parametros
#id: int identificador único
#dia: int usar 2 dígitos para decir el día
#mes: int usar 2 dígitos para ingresar el mes
#anio: int año 
#fecha: string fecha completa usar DD-MM-AAAA
def POST_fechaFin(id, dia, mes, anio, fecha):
	creds = checkCredentials()

	try:
		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'
		insert_data_option = 'INSERT_ROWS'
		data_range = connections.Fecha_Fin_range

		payload = [id, dia, mes, anio, fecha]

		value_range_body = {
			'values': [payload]
		}
		
		request = service.spreadsheets().values().append(spreadsheetId=connections.Fecha_Fin, range=data_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
		request.execute()

		return "fecha fin registrada"
	
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content

#Función para agendar la cita
#Parametros
#id_registrar: string identificador único del que agenda la cita
#id_esp: string identificador único del especialista que se le va a agendar la cita
#id_alumno: string identificador único del alumno al que se le va a agendar la cita
#fecha_ini: string fecha de inicio de la cita formato DD-MM-AAAA 
#fecha_end: string fecha de termino de la cita formato DD-MM-AAAA 
#hora_ini: string hora de inicio de la cita formato HH:MM 
#hora_end: string hora de termino de la cita formato HH:MM
#formato: string tipo de la cita que se va a hacer 
#recurrencia: string cada cuanto se va a repetir
#status: string por default es "Programada" 
#tipo: string que tipo de cita es, grupal o individual
#tipo_atencion: string, tipo de atención que se le va a dar, consulta, clase, taller u otros
@app.route("/agendamientoCita/<id_registrar>/<id_esp>/<id_alumno>/<fecha_ini>/<fecha_end>/<hora_ini>/<hora_end>/<formato>/<recurrencia>/<status>/<tipo>/<tipo_atencion>")
def POST_agendamientoCita(id_registrar, id_esp, id_alumno, fecha_ini, fecha_end, hora_ini, hora_end, formato, recurrencia, status, tipo, tipo_atencion):
	creds = checkCredentials()

	try:
		id_registro = GET_lenght("Agendamiento_Cita")
		id_cita = GET_lenght("Cita")
		id_horaIni = GET_lenght("Hora_Inicio")
		id_horaFin = GET_lenght("Hora_Fin")
		id_fechaIni = GET_lenght("Fecha_Inicio")
		id_fechaEnd = GET_lenght("Fecha_Fin")

		horaIni = hora_ini[:2]
		minIni = hora_ini[3:]
		horaEnd = hora_end[:2]
		minEnd = hora_end[3:]

		#Formato recomendado de fecha DD/MM/YYYY dia y mes siempre usar 2 dígitos
		diaIni = fecha_ini[:2]
		mesIni = fecha_ini[3:5]
		anioIni = fecha_ini[6:]

		diaEnd= fecha_end[:2]
		mesEnd = fecha_end[3:5]
		anioEnd = fecha_end[6:]

		service = build('sheets', 'v4', credentials=creds)
		value_input_option = 'USER_ENTERED'
		insert_data_option = 'INSERT_ROWS'
	

		#ids de alumno, cita, especialista, fecha inicio, fecha fin, hora inicio, hora fin,
		payload = [id_registro[0] + 1, id_alumno, id_cita[0] + 1, id_esp, id_fechaIni[0] + 1, id_fechaEnd[0] + 1, id_horaIni[0] + 1, id_horaFin[0] + 1, "FALSE", str(datetime.date.today()), id_registrar]

		value_range_body = {
			'values': [payload]
		}
		POST_cita(id_cita[0] + 1, formato, recurrencia, status, tipo, tipo_atencion)
		POST_horaInicio(id_horaIni[0] + 1, horaIni, minIni, hora_ini)
		POST_horaFin(id_horaFin[0] + 1, horaEnd, minEnd, hora_end)
		POST_fechaInicio(id_fechaIni[0] + 1, diaIni, mesIni, anioIni, fecha_ini)
		POST_fechaFin(id_fechaEnd[0] + 1, diaEnd, mesEnd, anioEnd, fecha_end)

		request = service.spreadsheets().values().append(spreadsheetId=connections.Agendamiento_Cita, range=connections.Agendamiento_Cita_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
		request.execute()

		return "cita registrada con exito"
	
	except HttpError as error:
		print(f"An error occurred: {error}")
		return error.content
	

#Endpoint para obtener el estado de la cita (read)
#Parametros
#id: int identificador de la cita a buscar
@app.route("/statusCita/<id>")
def GET_EstatusCita(id):
	creds = checkCredentials()

	try:
		service = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file('token.json', Scope))

		sheet = service.spreadsheets()
		result = sheet.values().get(spreadsheetId=connections.Cita,
					range='Hoja 1!A2:F').execute()
		values = result.get('values', [])

		if not values:
			return 'No data found.'
		else:
			index = int(id) - 1
			return values[index][3]
		
	except HttpError as err:
		return err.content
	
#Función principal
@app.route("/")
def main():
	return 'Conectado al api, llama a un endpoint'