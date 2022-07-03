from subprocess import call

import pandas
import plotly.utils
from flask import Flask, render_template, request,redirect, session
import sqlite3
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from urllib.request import urlopen
import hashlib
import requests
import matplotlib.pyplot as plt
import graphviz
from sklearn import datasets, linear_model, tree
from sklearn.tree import export_graphviz
from sklearn.ensemble import RandomForestClassifier
from fpdf import FPDF
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

class PDF(FPDF):
    pass

fLegal = open('./assets/legal.json')
fUsers = open('./assets/users.json')
fClases = open('./assets/users_IA_clases.json')
fPredecir = open('./assets/users_IA_predecir.json')
dataLegal = json.load(fLegal)
dataUsers = json.load(fUsers)
dataClases = json.load(fClases)
dataPredecir = json.load(fPredecir)

df_critico = pd.DataFrame()
df_usuarios = pd.DataFrame()
df_admins = pd.DataFrame()
df_menorDoscientos = pd.DataFrame()
df_mayorDoscientos = pd.DataFrame()
df_legal = pd.DataFrame()
df_vulnerable = pd.DataFrame()
totalDF = pd.DataFrame()
df_privacidad = pd.DataFrame()
df_conexiones = pd.DataFrame()


def comprobarPassword(password):
    print("Comprobando contrasena:",password)
    md5hash = password
    try:
        password_list = str(urlopen("https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(),'utf-8')
        for password in password_list.split('\n'):
            guess = hashlib.md5(bytes(password, 'utf-8')).hexdigest()
            if guess == md5hash:
                return 1
            elif guess != md5hash:
                continue
            else:
                return 2
        return 2
    except Exception as exc:
        return 2

def probabilidadClick(cliclados,total):
    if (total!=0):
        return (cliclados/total) * 100
    else:
        return 0

'''con = sqlite3.connect('SISTINF.db')
cursorObj = con.cursor()
cursorObj.execute("DROP TABLE  legal")
cursorObj.execute("DROP TABLE  users")
cursorObj.execute("CREATE TABLE IF NOT EXISTS legal (url,cookie,aviso,proteccion,politica,creacion)")
cursorObj.execute("CREATE TABLE IF NOT EXISTS users (nombre,telefono,contrasena,provincia,permisos,emailsTot,emailsPhis,emailsClick,probClick, fechas, num_fechas, ips, num_ips, fortPass,primary key (nombre))")
insertLegal = """INSERT INTO legal (url,cookie,aviso,proteccion,politica,creacion) VALUES (?,?,?,?,?,?)"""
insertUsers = """INSERT INTO users (nombre,telefono,contrasena,provincia,permisos,emailsTot,emailsPhis,emailsClick,probClick, fechas, num_fechas, ips, num_ips, fortPass) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
for i in dataLegal['legal']:
    for j in i.keys():
        for k in i.values():
            datosLegal = (j, k['cookies'], k['aviso'], k['proteccion_de_datos'], k['cookies'] + k['aviso'] + k['proteccion_de_datos'], k['creacion'])
        cursorObj.execute(insertLegal, datosLegal)
        con.commit()

for i in dataUsers['usuarios']:
    for j in i.keys():
        for k in i.values():
            datosUsers = (j, k['telefono'], k['contrasena'], k['provincia'], k['permisos'], k['emails']['total'], k['emails']['phishing'], k['emails']['cliclados'],probabilidadClick(k['emails']['cliclados'],k['emails']['phishing']), str(k['fechas']), len(k['fechas']), str(k['ips']), len(k['ips']), comprobarPassword(k['contrasena']))
        cursorObj.execute(insertUsers, datosUsers)
        con.commit()

con.commit()'''


@app.route('/')
def index():  # put application's code here
    return render_template('login.html')

@app.route('/home.html')
def home():  # put application's code here
        return render_template("home.html")

users = [["admin","admin"],["user","user"]]
app.secret_key = "SecretKey"

@app.route('/login.html',methods=["GET","POST"])
def login():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        for i in range(len(users)):
            if (users[i][0]==username and users[i][1]==password):
                session['user'] = username
                return redirect('/home.html')

        return "<h1>Wrong username or password</h1>"

    return render_template("login.html")

@app.route('/register.html',methods=["GET","POST"])
def register():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        users.append([username,password])

    return render_template("register.html")

@app.route('/TopUsuariosCriticos.html', methods=["GET","POST"])
def topUssersCrit():
    num = request.form.get('numero', default=10)
    probNum = request.form.get('porcentaje',default='0')
    if(num==''):
        num = 10
    df_critico = pandas.DataFrame()
    con = sqlite3.connect('SISTINF.db')
    cursor_obj = con.cursor()

    if(probNum == '0'):
        query = """SELECT nombre,probClick FROM users where fortPass=1 ORDER BY probClick DESC LIMIT (?)"""
    elif(probNum == '1'):
        query = """SELECT nombre,probClick FROM users where fortPass=1 AND probClick>=50 ORDER BY probClick DESC LIMIT (?)"""
    elif(probNum =='2'):
        query = """SELECT nombre,probClick FROM users where fortPass=1 AND probClick<50 ORDER BY probClick DESC LIMIT (?)"""

    cursor_obj.execute(query, (num,))
    rows = cursor_obj.fetchall()
    nombre = []
    prob = []
    for i in range(len(rows)):
        nombre += [rows[i][0]]
        prob += [rows[i][1]]
    df_critico['Nombre'] = nombre
    df_critico['Probabilidad de Click'] = prob
    fig = px.bar(df_critico, x=df_critico['Nombre'], y=df_critico['Probabilidad de Click'])
    a = plotly.utils.PlotlyJSONEncoder
    graphJSONUsu = json.dumps(fig, cls=a)
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf_w = 210
    pdf_h = 297
    plotly.io.write_image(fig, file='pltx.png', format='png', width=700, height=450)
    pltx = (os.getcwd() + '/' + "pltx.png")
    pdf.set_xy(40.0, 25.0)
    pdf.image(pltx, link='', type='', w=700 / 5, h=450 / 5)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    txt = "Top de usuarios críticos. En el eje X se muestran los nombres de los usuarios mientras que en el eje Y se muestra la probabilidad de click."
    pdf.set_xy(10.0, 130.0)
    pdf.multi_cell(w=0, h=10, txt=txt, align='L')
    pdf.output('static/topUsuariosCriticos.pdf', 'F')
    con.close()
    return render_template('TopUsuariosCriticos.html', graphJSONUsu=graphJSONUsu)

@app.route('/TopPaginasVulnerables.html', methods=["GET","POST"])
def topWebsVuln():
    num = request.form.get('numero', default=10)
    if (num == ''):
        num = 10
    print("00.33="+str(num));
    df_topWebs =pandas.DataFrame()
    con = sqlite3.connect('SISTINF.db')
    cursor_obj = con.cursor()
    query = """SELECT url,cookie,aviso,proteccion FROM legal ORDER BY politica LIMIT (?)"""
    cursor_obj.execute(query, (num,))
    rows = cursor_obj.fetchall()
    nombre = []
    cookies = []
    avisos = []
    proteccionDatos = []
    for i in range(len(rows)):
        nombre += [rows[i][0]]
        cookies += [rows[i][1]]
        avisos += [rows[i][2]]
        proteccionDatos += [rows[i][3]]
    df_topWebs['Nombre'] = nombre
    df_topWebs['Cookies'] = cookies
    df_topWebs['Avisos'] = avisos
    df_topWebs['Proteccion de Datos'] = proteccionDatos
    fig = go.Figure(data=[
        go.Bar(name='Cookies', x=df_topWebs['Nombre'], y=df_topWebs['Cookies'], marker_color='steelblue'),
        go.Bar(name='Avisos', x=df_topWebs['Nombre'], y=df_topWebs['Avisos'], marker_color='lightsalmon'),
        go.Bar(name='Proteccion de datos', x=df_topWebs['Nombre'], y=df_topWebs['Proteccion de Datos'], marker_color='red')
    ])
    fig.update_layout(title_text="Top páginas vulnerables", title_font_size=41, barmode='group')
    a = plotly.utils.PlotlyJSONEncoder
    graphJSONPag = json.dumps(fig, cls=a)
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf_w = 210
    pdf_h = 297
    plotly.io.write_image(fig, file='pltx.png', format='png', width=700, height=450)
    pltx = (os.getcwd() + '/' + "pltx.png")
    pdf.set_xy(40.0, 25.0)
    pdf.image(pltx, link='', type='', w=700 / 5, h=450 / 5)
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0,0,0)
    txt="Top paginas vulnerables. En el eje X se muestran las paginas web mientras que en el eje Y semuestra la politica. "
    pdf.set_xy(10.0, 140.0)
    pdf.multi_cell(w=0, h=10, txt=txt,align='L')
    pdf.output('static/topPaginasVulnerables.pdf', 'F')
    return render_template('TopPaginasVulnerables.html', graphJSONPag=graphJSONPag)

@app.route('/Ultimas10Vulnerabilidades.html')
def ejerCuatro():
    page = requests.get("https://cve.circl.lu/api/last")
    jsons = page.json()
    listaCve = []
    listaSum = []
    for i in range(0,10):
        listaCve += [jsons[i]['id']]
        listaSum += [jsons[i]['summary']]
    fig = go.Figure(data=[go.Table(header=dict(values=['Vulnerabilidad','Descripcion']),cells=dict(values=[listaCve,listaSum]))])
    tabla = plotly.io.to_html(fig)
    return render_template('Ultimas10Vulnerabilidades.html',tablaHTMLVul=tabla)

def regresionLineal():
    print('Regresion Lineal')

    with open('./assets/users_IA_clases.json') as dat:
        data = json.load(dat)
    dataX = []
    dataY = []
    for usuario in np.asarray(data['usuarios']):
        dataX.append([usuario['emails_phishing_recibidos'], usuario['emails_phishing_clicados']])
        dataY.append(usuario['vulnerable'])
    reg = LinearRegression().fit(dataX, dataY)
    print(reg.score(dataX, dataY))
    with open('./assets/users_IA_predecir.json') as dat:
        dataPredecir = json.load(dat)
    predecirX = []
    for usuario in np.asarray(dataPredecir['usuarios']):
        predecirX.append([usuario['emails_phishing_recibidos'], usuario['emails_phishing_clicados']])
    predecirY = reg.predict((np.array(predecirX)))
    print(predecirY)
    return predecirY

def decisionTree():
    print('\n Arbol de Decision')
    with open('./assets/users_IA_clases.json') as dat:
        data = json.load(dat)
    dataX = []
    dataY = []
    for usuario in np.asarray(data['usuarios']):
        dataX.append([usuario['emails_phishing_recibidos'], usuario['emails_phishing_clicados']])
        dataY.append(usuario['vulnerable'])
    reg = DecisionTreeClassifier().fit(dataX, dataY)
    print(reg.score(dataX, dataY))
    with open('./assets/users_IA_predecir.json') as dat:
        dataPredecir = json.load(dat)
    predecirX = []
    for usuario in np.asarray(dataPredecir['usuarios']):
        predecirX.append([usuario['emails_phishing_recibidos'], usuario['emails_phishing_clicados']])
    predecirY = reg.predict((np.array(predecirX)))
    print(predecirY)
    return predecirY

def randomForest():
    print('\n Bosque Aleatorio')
    with open('./assets/users_IA_clases.json') as dat:
        data = json.load(dat)
    dataX = []
    dataY = []
    for usuario in np.asarray(data['usuarios']):
        dataX.append([usuario['emails_phishing_recibidos'], usuario['emails_phishing_clicados']])
        dataY.append(usuario['vulnerable'])
    reg = RandomForestClassifier().fit(dataX, dataY)
    print(reg.score(dataX, dataY))
    with open('./assets/users_IA_predecir.json') as dat:
        dataPredecir = json.load(dat)
    predecirX = []
    for usuario in np.asarray(dataPredecir['usuarios']):
        predecirX.append([usuario['emails_phishing_recibidos'], usuario['emails_phishing_clicados']])
    predecirY = reg.predict((np.array(predecirX)))
    print(predecirY)
    return predecirY

regresionLineal();
decisionTree();
randomForest();

if __name__ == '__main__':
    app.run(debug=True)