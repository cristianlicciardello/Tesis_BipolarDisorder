import telebot #Libreria de api telegram
import numpy as np #Libreria de 
import pandas as pd 
from telebot import types #Utilizo la herramienta types de la libreria telebot 
import re
import matplotlib.pyplot as plt #Utilizo la libreria matplot para los graficos
import seaborn as sns #Utilizo libreria de seaborn para graficar
import io 
import datetime #Utilizo datetime para manejo de fechas
import timedelta
from tabulate import tabulate

#Importo herramientas de machine learnin de sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

#Declaración de variables Globales
features = {} #Caracteristicas correspondientes a cada paciente 'Ansiedad', 'Motivación','Irritabilidad','Estado de ánimo','Calidad del sueño'
fecha_inicio= pd.to_datetime('1900-01-01')
fecha_fin= pd.to_datetime('2100-01-01')
df_pacientes = pd.DataFrame(columns=['chat_id', 'nombre_completo', 'numero_telefono'])
selected_metrics=[] #Lista de metricas seleccionadas
current_day = datetime.date.today() #Dia de la fecha
print(current_day)
bot = telebot.TeleBot("6242548752:AAEpxVC4y-4KgMy5hCY7A8xOIWjbP0YRopc")#Token de bot

young = pd.read_csv('./diario.csv', sep=';')#Lectura de base de datos
young = young[young['Código'] != 'O']#Data cleaning
plt.figure(figsize=(15, 15))


#Modulo de solicitud de derivación médica
@bot.callback_query_handler(func=lambda call: call.data == '/solicitar_derivacion')
def solicitar_derivacion(call):
    chat_id = call.message.chat.id
    
    sent_msg=bot.send_message(chat_id, "Por favor, proporcione su nombre completo para solicitar la derivación.")
    bot.register_next_step_handler(sent_msg, procesar_nombre)

def procesar_nombre(message):
    chat_id = message.chat.id
    nombre_completo = message.text
    df_pacientes.loc[df_pacientes.shape[0]] = [chat_id, nombre_completo, None]
    sent_msg=bot.send_message(chat_id, "Gracias, ahora proporciona tu número de teléfono📞 para que podamos contactarte.")
    bot.register_next_step_handler(sent_msg, procesar_numero)
    
def procesar_numero(message):
    chat_id = message.chat.id
    numero_telefono = message.text

    df_pacientes.loc[df_pacientes['chat_id'] == chat_id, 'numero_telefono'] = numero_telefono
    bot.send_message(chat_id, "Hemos registrado tu solicitud de derivación. Un profesional de la salud se pondrá en contacto contigo pronto.")
    df_pacientes.to_csv('datos_pacientes.csv', index=False)
    
def urgencia(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1) 
    itembtn1 = types.InlineKeyboardButton('Líneas de acompañamiento, apoyo y orientación en salud mental', url="https://www.argentina.gob.ar/andis/lineas-de-acompanamiento-apoyo-y-orientacion-en-salud-mental-en-contextos-de-cuarentena") 
    markup.add(itembtn1) 
    bot.send_message(chat_id,"🆘Urgencia Médica🆘 \n\nSi te encuentras en una situación de emergencia médica, es vital buscar ayuda inmediata. En el siguiente link encontrarás formas de comunicarte:", reply_markup=markup) 






#Modulo de entrevista
@bot.callback_query_handler(func=lambda call: call.data == '/entrevista')
def bienvenida(pm):
    chat_id=pm.message.chat.id
    send_msg=bot.send_message(chat_id, "Sigue las instrucciones para responder las preguntas. Al final de la entrevista, podes evaluar tu seguimiento y ver gráficos de estado")
    send_msg=bot.send_message(chat_id, "¿Puedes indicarme tu nombre?")
    bot.register_next_step_handler(send_msg, saludar)

def saludar(pm):
    nombre=pm.text
    features["ID"]=pm.chat.id
    bot.send_message(pm.chat.id, "Bueno  "+nombre+", voy a asistirte con tu seguimiento virtual 📝")
    animo(pm)


def animo(pm): 
    sent_msg = bot.send_message(pm.chat.id, "Resume cómo ha sido tu estado de ánimo en el día de hoy (en un rango de -3 a + 3),Siendo : \n\n-3)Grado máximo de depresión \n-2)grado intermedio de depresión \n-1)depresión leve, apenas perceptible \n0) Eutimia o normalidad \n1)euforia o irritabilidad leve, apenas perceptible \n2)grado intermedio de euforia o irritabilidad \n3)Grado máximo de euforia o irritabilidad")
    bot.register_next_step_handler(sent_msg, validar_animo)

def validar_animo(pm):
    
    valor=int(pm.text)
    if -3<=valor<=3:
        features["animo"]=valor
        motivacion(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_animo)

def motivacion(pm):
    
    valor=int(pm.text)
    if -3 <=valor<=3:
        features["animo"]=valor
        motivacion(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_animo)
def motivacion(pm):   
    sent_msg = bot.send_message(pm.chat.id, "Indica tu grado de motivación(de -3 a 3). Se refiere a las ganas de hacer cosas, la energía y la actividad que has tenido durante este día. Debes marcar entre -3 y 3, Siendo: \n\n-3) Grado mínimo de motivación \n-2)Grado intermedio de motivación\n-1)Leve disminución en la motivación, apenas perceptible \n0)Motivación o energía media, normal.\n 1)Motivación o ganas de hacer cosas un poco aumentadas\n2)grado intermedio de motivación \n3) Grado Máximo de motivación ")
    bot.register_next_step_handler(sent_msg, validar_motivación) #Next message will call the age_handler function
    


def validar_motivación(pm):
    
    valor=int(pm.text)
    if -3 <=valor<=3:
        features["motivacion"]=valor
        atencion(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_motivación)



def atencion(pm):
    sent_msg = bot.send_message(pm.chat.id, "En esta escala (0 a 4) debes marcar cómo te has concentrado y has prestado atención durante el día. Siendo:\n \n 0)Buena atención y concentración \n1)Leves problemas apenas perceptibles\n2)Problemas moderados\n3)Dificultades importantes, es difícil seguir una película o leer un texto \n4)Alteración grave, imposibilidad de mantener una conversación.")
    bot.register_next_step_handler(sent_msg, validar_atencion)

def validar_atencion(pm):
    
    valor=int(pm.text)
    if 0<=valor<=4:
        features["atencion"]=valor
        irritabilidad(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_atencion)


def irritabilidad(pm):
    
    sent_msg = bot.send_message(pm.chat.id, "Indica (de 0 a 4) cómo has estado de irritable, impaciente o con facilidad para enfadarte durante este día. Es muy difícil ser objetivo. Si tienes dudas, puede preguntar a tus allegados.  siendo: \n\n 0)Muy tranquilo, inalterable, ninguna discusión \n 1)Leve tendencia a enfadarse, apenas perceptible \n 2)Moderada irritabilidad, claramente apreciable. \n 3)Muy irritable, dificultades para contenerse \n 4)Irritabilidad extrema, incluso agresividad.")
    bot.register_next_step_handler(sent_msg, validar_irritabilidad)

def validar_irritabilidad(pm):
    
    valor=int(pm.text)
    if 0 <=valor<=4:
        features["irritabilidad"]=valor
        ansiedad(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_irritabilidad)

    
def ansiedad(pm):
    sent_msg = bot.send_message(pm.chat.id, "Indica si has tenido ansiedad, nerviosismo o angustia durante este día. Siendo: \n\n0)Ausente\n 1)Leve \n2)Moderado\n3)Grave y continua \n4)Muy grave, incapacitante ")
    bot.register_next_step_handler(sent_msg, validar_ansiedad)


def validar_ansiedad(pm):
    
    valor=int(pm.text)
    if 0 <=valor<=4:
        features["ansiedad"]=valor
        calidad_sueño(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_ansiedad)



def calidad_sueño(pm):
    sent_msg = bot.send_message(pm.chat.id, "Índica cómo has dormido esta última noche, sin tener en cuenta si has precisado medicación para dormir. \n\n 0) Sueño adecuado y reparador \n1)Leves problemas de sueño \n2)Moderados problemas de sueño \n3)Apenas he descansado. \n4)No he dormido nada")
    bot.register_next_step_handler(sent_msg, validar_calidad)


def validar_calidad(pm):
    
    valor=int(pm.text)
    if  (0 <=valor<=4):
        features["calidad_sueño"]=valor
        cigarrillos(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_calidad)

def cigarrillos(pm):
    sent_msg = bot.send_message(pm.chat.id, "Cantidad de cigarrillos consumidos 🚬 ? ")
    bot.register_next_step_handler(sent_msg, validar_cigarrillos)

def validar_cigarrillos(pm):
    valor=pm.text
    if valor.isnumeric():
        features["cigarrillos"]=valor
        cafeina(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌ El valor no se encuentra en el rango, Reingreselo por favor❌")
        bot.register_next_step_handler(sent_msg, validar_cigarrillos)



def cafeina(pm):
    sent_msg = bot.send_message(pm.chat.id, "Indique cantidad consumida de cafeina ☕ en mg, Te indico algunas referencias: \n\nTaza de té negro = 60 \nLata de Red Bull 250 ml = 80 \nLata de cola 330ml = 30 \nCafé exprés = 90")
    bot.register_next_step_handler(sent_msg, validar_cafeina)

def validar_cafeina(pm):
    valor=pm.text
    if valor.isnumeric():
        features["cafeina"]=valor
        alcohol(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌ El valor no se encuentra en el rango, Reingreselo por favor❌ ")
        bot.register_next_step_handler(sent_msg, validar_cafeina)

def alcohol(pm):
    sent_msg = bot.send_message(pm.chat.id, "¿Consumio alcohol 🍺 🍻 🍸 🍹 ? Ingrese Si o No")
    bot.register_next_step_handler(sent_msg, validar_alcohol)

def validar_alcohol(pm):
    valor=pm.text
    if (valor=="Si" or valor=="No"):
        features["alcohol"]=valor
        drogas(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "Ingreso un valor incorrecto, Reingreselo por favor")
        bot.register_next_step_handler(sent_msg, validar_alcohol)

def drogas(pm):
    sent_msg = bot.send_message(pm.chat.id, "¿Consumio alguna droga 💊? Ingrese Si o No")
    bot.register_next_step_handler(sent_msg, validar_drogas)

def validar_drogas(pm):
    valor=pm.text
    if (valor=="Si" or valor=="No"):
        features["drogas"]=valor
        despertar(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, " ❌ Ingreso un valor incorrecto, Reingreselo por favor ❌")
        bot.register_next_step_handler(sent_msg, validar_drogas)

def despertar(pm):
    
    sent_msg = bot.send_message(pm.chat.id, "¿ A que hora se despertó (hh:mm)? ")
    bot.register_next_step_handler(sent_msg, validar_despertar)

def validar_despertar(pm):
    valor=pm.text
    if re.match('[0-9]{2}:[0-9]{2}$', valor):
        features["despertar"]=valor
        dormir(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌ El valor no se encuentra en el rango, Reingreselo por favor ❌")
        bot.register_next_step_handler(sent_msg, validar_despertar)



def dormir(pm):
    sent_msg = bot.send_message(pm.chat.id, "¿ A que hora se durmió (hh:mm)? ")
    bot.register_next_step_handler(sent_msg, validar_dormir)

def validar_dormir(pm):
    valor=pm.text
    if re.match('[0-9]{2}:[0-9]{2}$', valor):
        features["dormir"]=valor
        fin_entrevista(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "❌ El valor no se encuentra en el rango, Reingreselo por favor ❌")
        bot.register_next_step_handler(sent_msg, validar_dormir)
    

def fin_entrevista(pm):

    sent_msg = bot.send_message(pm.chat.id, "Finalizo la entrevista, vamos a analizar los datos envidados...")

   

    x=np.array([features["animo"], features["motivacion"], features["atencion"],
            features["irritabilidad"], features["ansiedad"], features["calidad_sueño"],
            features["cigarrillos"], features["cafeina"]]).reshape(1,-1)
    print(x)
    sent_msg = bot.send_message(pm.chat.id,"Los datos ingresados son los siguientes: ")

    sent_msg = bot.send_message(pm.chat.id,str(x))

    young.dropna()
    np.nan_to_num(young)

    #Entrenamiento de datos

    X_train, X_test, y_train, y_test = train_test_split(young.drop(["Código","Fecha","Alcohol","Otras drogas","Hora de despertar","Hora a la que te dormiste","Ciclo menstrual","ID"],axis=1),young['Código'],test_size=0.33, random_state=10)

    print(X_train)
    print(X_test)
    print(y_train)

    #Predicción con modulo de Machine learning
    rf = RandomForestClassifier(n_jobs=-1)
    X_train2=X_train.iloc[1]

    dt = DecisionTreeClassifier(max_depth=10, min_samples_leaf=15)
    dt.fit(X_train, y_train)

    rf.fit(X_train, y_train)
    scores = cross_val_score(rf, X_test, y_test)
    print ("Model accuracy: ", scores.mean())
    print ("\n")
    X_test2=X_test.iloc[1:2]

    print(x)
    y_pred_test=rf.predict(X_test)
    y_pred=rf.predict(x)
    print (y_pred)
    features["codigo"]=y_pred[0]
    
    formatted_date = datetime.date.strftime(current_day, "%d/%m/%Y")

    features["fecha"]=formatted_date

    print(accuracy_score(y_test,y_pred_test))
    
    print("La predicción de su estado a traves de algoritmo de Random Forest es; ", show_prediction(y_pred))
    sent_msg = bot.send_message(pm.chat.id,"La predicción de su estado a traves de algoritmo de Random Forest es: ")
    sent_msg = bot.send_message(pm.chat.id,show_prediction(rf.predict(x)))
    sent_msg = bot.send_message(pm.chat.id,"La predicción de su estado a traves de algoritmo de arbol de decisión es: ")
    sent_msg = bot.send_message(pm.chat.id,show_prediction(dt.predict(x)))


    print ("\n")

    youngNew=young.append(pd.Series([features["animo"], features["motivacion"], features["atencion"],
            features["irritabilidad"], features["ansiedad"], features["calidad_sueño"],
            features["cigarrillos"], features["cafeina"],features["alcohol"],features["drogas"],features["despertar"],features["dormir"],features["codigo"],features["fecha"],features["ID"]],index=['Estado de ánimo','Motivación','Problemas de concentración y atención','Irritabilidad','Ansiedad','Calidad del sueño','Número de cigarrillos','Cafeína','Alcohol','Otras drogas','Hora de despertar','Hora a la que te dormiste','Código','Fecha','ID']),ignore_index=True)
    print(youngNew)
    
    youngNew.to_csv('./diario.csv', sep=';',index=False)

    #Guarda en el archivo los datos nuevos
    #youngNew.to_excel('Resultados.xlsx')
    markup = types.InlineKeyboardMarkup(row_width=3) 
    itembtn = types.InlineKeyboardButton('Seguimiento de datos 📈 ', callback_data='/resultados') 
    markup.add(itembtn)
    bot.send_message(pm.chat.id,"Gracias por responder, si desea ver los análisis de su datos, pulse el boton para realizar el seguimiento ", reply_markup=markup) 

#Mensajes a mostrar según predicción de estado
def show_prediction(pred):
    msg = ''
    if pred == 'D':
        msg = ("El paciente podria tender hacia un episodio de DEPRESIÓN")
    elif pred == 'M':
        msg = ("El paciente podría tender hacía un episodio de MANIA")
    else:
        msg = ("El paciente posee un estado eutímico")
    return msg

@bot.message_handler(commands=['help'])
def consentimiento(message):
    chat_id = message.chat.id
    help_message = "¡Bienvenido!😊 Estoy aquí para brindarte apoyo y orientación en relación con el trastorno bipolar. "
    bot.send_message(chat_id,help_message)
    bot.send_message(chat_id,"Por favor, tómate un momento para revisar la información siguiente....")
    bot.send_message(chat_id,"*La privacidad y la confidencialidad de tus datos son fundamentales para nosotros.*\nTu información se manejará de acuerdo con las leyes de protección de datos aplicables y no se compartirá con terceros sin tu consentimiento.", parse_mode="Markdown")
    bot.send_message(chat_id,"Al utilizar esta aplicación, aceptas voluntariamente los términos y condiciones mencionados. Tu participación es voluntaria, y puedes optar por no utilizar la aplicación si no estás de acuerdo con estos términos.")
    
    markup = types.InlineKeyboardMarkup(row_width=1) 
    itembtn1 = types.InlineKeyboardButton('Sí, acepto✅', callback_data='/comenzar') 
    itembtn2 = types.InlineKeyboardButton('No, no estoy de acuerdo✖️', callback_data='/finalizar') 
    
    markup.add(itembtn1)
    markup.add(itembtn2)
    

    bot.send_message(chat_id," ¿Estás de acuerdo con las condiciones mencionadas y deseas utilizar la aplicación?:", reply_markup=markup) 



#Modulo de ayuda 
@bot.callback_query_handler(func=lambda call: call.data == '/comenzar')
def handle_help(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id,"*IMPORTANTE* ‼️ recordar que soy un asistente virtual y no un sustituto de la atención médica profesional. Sin embargo, puedo tomar tus datos para que un profesional se ponga en contacto contigo", parse_mode="Markdown")
    
    markup = types.InlineKeyboardMarkup(row_width=1) 
    itembtn1 = types.InlineKeyboardButton('Entrevista ❓', callback_data='/entrevista') 
    itembtn2 = types.InlineKeyboardButton('Solicitar atención médica 🩺', callback_data='/solicitar_derivacion') 
    itembtn3 = types.InlineKeyboardButton('Información sobre el trastorno bipolar ℹ',  callback_data='/info_bipolar') 

    markup.add(itembtn1)
    markup.add(itembtn2)
    markup.add(itembtn3)

    
    bot.send_message(chat_id," Para comenzar, elige la opción que quieras realizar:", reply_markup=markup) 


@bot.callback_query_handler(func=lambda call: call.data == '/info_bipolar')
def info(call):
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1) 
    itembtn1 = types.InlineKeyboardButton('Más información sobre el trastorno bipolar', url="https://www.mayoclinic.org/es/diseases-conditions/bipolar-disorder/symptoms-causes/syc-20355955") 
    markup.add(itembtn1) 
    bot.send_message(chat_id,"*El trastorno bipolar*, también conocido como enfermedad maníaco-depresiva, es una afección psiquiátrica crónica que involucra oscilaciones anormales en el estado de ánimo, que pueden variar desde episodios de euforia extrema (manía) hasta episodios de depresión profunda.", parse_mode="Markdown")
    bot.send_message(chat_id,"*Síntomas:* \n\n*Manía:* Durante los episodios maníacos, las personas pueden experimentar un aumento excesivo de la energía, irritabilidad, hiperactividad, pensamientos acelerados y comportamientos impulsivos. \n\n*Depresión:* Los episodios depresivos se caracterizan por una profunda tristeza, falta de energía, apatía, dificultad para dormir, pérdida de interés en actividades previamente disfrutadas y pensamientos de suicidio.", parse_mode="Markdown") 
    bot.send_message(chat_id,"*Impacto:* El trastorno bipolar puede afectar significativamente la calidad de vida, las relaciones y el funcionamiento diario. Sin embargo, con un tratamiento adecuado, muchas personas pueden llevar una vida plena.", parse_mode="Markdown") 
    bot.send_message(chat_id,"*Importancia del Diagnóstico y Tratamiento:* El diagnóstico temprano y el tratamiento adecuado son fundamentales para gestionar el trastorno bipolar y prevenir complicaciones. El apoyo y la comprensión de amigos y familiares también son esenciales.", parse_mode="Markdown") 

    bot.send_message(chat_id,"Para saber más información:", reply_markup=markup) 
    
#Modulo de evaluación de resultados
@bot.callback_query_handler(func=lambda call: call.data == '/resultados')
def resultados(call):
    chat_id = call.message.chat.id
    mensaje= "Para poder realizar tu seguimiento vas a poder evaluar tus resultados según distintos gráficos de analisis de datos."
    markup = types.InlineKeyboardMarkup(row_width=1) 
    itembtn1 = types.InlineKeyboardButton('1) Mirar Correlación de variables', callback_data='/correlacion') 
    itembtn2 = types.InlineKeyboardButton('2) Mirar diagrama de caja', callback_data='/boxplot')
    itembtn3 = types.InlineKeyboardButton('3) Ver seguimiento Temporal', callback_data='/temporal')
    itembtn4 = types.InlineKeyboardButton('4) Ver variables descriptivas', callback_data='/descriptivas')
    itembtn5 = types.InlineKeyboardButton('5) Volver al inicio', callback_data='/comenzar')
    itembtn6 = types.InlineKeyboardButton('6) Finalizar conversación', callback_data='/finalizar')
    markup.add(itembtn1) 
    markup.add(itembtn2)
    markup.add(itembtn3)
    markup.add(itembtn4)
    markup.add(itembtn5)
    markup.add(itembtn6)
    bot.send_message(chat_id,mensaje) 
    bot.send_message(chat_id,"Elige la opción que quieras ver:", reply_markup=markup) 
    
#Gráfico de variables descriptivas
@bot.callback_query_handler(func=lambda call: call.data == '/descriptivas')
def variables_descriptivas(pm):
    bot.send_message(pm.message.chat.id, "Aquí puedes observar como se comportan las variables de este paciente....")
    df=young[young["ID"]==features["ID"]]
    df=df.drop(["Ciclo menstrual","ID"],axis=1)
    df=df.rename(columns={'Problemas de concentración y atención': 'Problemas de C&A'})
    #Agrega una columna con las etiquetas correspondientes.
    
    descriptivas=df.describe().round(3)  
    descriptivas['Etiqueta'] = ['Count', 'Media', 'std','min','25%', '50%', '75%', 'Max']
    # Reorganiza las columnas para que la columna de etiquetas sea la primera.
    descriptivas = descriptivas[['Etiqueta'] + list(descriptivas.columns[:-1])]
    fig, ax = plt.subplots(figsize=(40,20))
    ax.axis('off')

    # Crea una tabla.
    tabla = ax.table(cellText=descriptivas.values,
                 colLabels=descriptivas.columns,
                 cellLoc='center',
                 loc='center',
                 colColours=['#f2f2f2']*len(descriptivas.columns),
                 bbox=[0, 0, 1, 1]
                 )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(21)  # Ajusta el tamaño de la fuente según tus preferencias.

    # Guarda la imagen en un buffer.
    buffer = io.BytesIO() 
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    bot.send_photo(pm.message.chat.id, photo=buffer)
    resultados(pm)

#Gráfico de correlación
@bot.callback_query_handler(func=lambda call: call.data == '/correlacion')
def mapa_correlacion(pm):
    
    bot.send_message(pm.message.chat.id, "Voy a darte una breve introducción: \n\n*Una matriz de correlaciones* es una tabla o una cuadrícula de números que muestra cómo dos o más variables están relacionadas entre sí. \n\n\n En otras palabras, te muestra si hay una conexión o asociación entre diferentes cosas que estás observando o midiendo. Cada número en la matriz representa la correlación entre dos variables. \n\n\n La correlación es un valor que va de -1 a 1: \n\n\n *-Si la correlación es cercana a 1*, significa que las dos variables están fuertemente relacionadas de manera positiva, lo que significa que cuando una variable aumenta, la otra también tiende a aumentar. \n\n\n *- Si la correlación es cercana a -1*, significa que las dos variables están fuertemente relacionadas de manera negativa, lo que significa que cuando una variable aumenta, la otra tiende a disminuir. \n\n\n *- Si la correlación es cercana a 0*, significa que no hay una relación fuerte entre las dos variables.", parse_mode="Markdown")
    bot.send_message(pm.message.chat.id, "Aquí puedes observar como se relacionan tus datos....")
    df=young["ID"]==features["ID"]
    dfC=young[df].drop(["Ciclo menstrual","ID"],axis=1)
    img_buffer = io.BytesIO()
    plt.figure(figsize=(10, 10))
    
    sns.heatmap(
        dfC.corr(),
        annot= True,
        cbar      = False,
        annot_kws = {"size": 8},
        vmin      = -1,
        vmax      = 1,
        center    = 0,
        cmap      = sns.diverging_palette(20, 220, n=200),
        square    = True,
        )



    plt.savefig(img_buffer, format='png')

    img_buffer.seek(0)
   

    # Envía el gráfico al usuario a través de Telegram
    bot.send_photo(pm.message.chat.id, photo=img_buffer)
    plt.clf()
    resultados(pm)

#Graficos de diagrama de caja
@bot.callback_query_handler(func=lambda call: call.data == '/boxplot')

def mapa_boxplot(pm):
    bot.send_message(pm.message.chat.id, "Aquí puedes observar como se distribuyeron tus datos y cuales fueron valores atípicos.")
    df=young["ID"]==features["ID"]
    dfC=young[df]
    
    img_buffer = io.BytesIO()
    
    dfC.boxplot(column=["Motivación","Calidad del sueño","Ansiedad","Irritabilidad","Estado de ánimo"],figsize=(15, 15))
    plt.savefig(img_buffer, format='png')

    img_buffer.seek(0)
   

    # Envía el gráfico al usuario a través de Telegram
    bot.send_photo(pm.message.chat.id, photo=img_buffer)
    plt.clf()
    resultados(pm)


@bot.callback_query_handler(func=lambda call: call.data == '/temporal')
def generar_graficos(pm):
    bot.send_message(pm.message.chat.id, "Aquí puedes observar como variaron tus comportamientos en el ultimo tiempo. Selecciona las métricas que desees ver y luego pulsa *Finalizar Selección* ", parse_mode="Markdown")
    send_metrics_selection(pm.message.chat.id)

    
#Seleccion de metricas para graficos temporales
def send_metrics_selection(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1=types.InlineKeyboardButton("-Ansiedad ☑️", callback_data='Ansiedad')
    btn2=types.InlineKeyboardButton("-Motivación ☑️", callback_data='Motivación')
    btn3=types.InlineKeyboardButton("-Irritabilidad ☑️", callback_data='Irritabilidad')
    btn4=types.InlineKeyboardButton("-Estado de ánimo ☑️", callback_data='Estado de ánimo')
    btn5=types.InlineKeyboardButton("-Calidad del sueño ☑️", callback_data='Calidad del sueño')
    btn6=types.InlineKeyboardButton("-Problemas de concentración y atención ☑️", callback_data='Problemas de concentración y atención')
    btn7=types.InlineKeyboardButton("-Finalizar selección 🔚", callback_data='done')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn5)
    markup.add(btn6)
    markup.add(btn7)
    bot.send_message(chat_id, "Selecciona las métricas que deseas incluir en el gráfico:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in {'Ansiedad', 'Motivación','Irritabilidad','Estado de ánimo','Calidad del sueño','Problemas de concentración y atención'})
def handle_metrics_selection(call):
    selected_metric = call.data
    if selected_metric not in selected_metrics:
        selected_metrics.append(selected_metric)
    send_metrics_selection(call.message.chat.id)
    




@bot.callback_query_handler(func=lambda call: call.data =='done')
def handle_done_selection(call):
    if not selected_metrics:
        bot.send_message(call.message.chat.id, "No has seleccionado ninguna métrica. Vuelve a comenzar.")
        return
    metrics_text = "\n".join(selected_metrics)
    bot.send_message(call.message.chat.id, f"Has seleccionado las siguientes métricas:\n{metrics_text}\n")
    bot.send_message(call.message.chat.id, "¿A partir de que fecha de INICIO desea ver los comportamientos? Ingrese en formato AAAA-MM-DD .")
    bot.register_next_step_handler(call.message, select_start_date)




def select_start_date(pm):
    fecha_inicio=pd.to_datetime(pm.text)
    sent_msg=bot.send_message(pm.chat.id, "¿Hasta que fecha desea ver los comportamientos? Ingrese en formato AAAA-MM-DD")
    bot.register_next_step_handler(sent_msg, select_end_date)
   
def select_end_date(pm):    
    
    fecha_fin=pd.to_datetime(pm.text)
    create_graph(pm.chat.id)




#Creacion del grafico temporal filtrado por comportamiento
def create_graph(chat_id):

    young['fecha_datetime'] = pd.to_datetime(young['Fecha'], format='%d/%m/%Y')
    filtrado=young[(young["ID"]==features["ID"])]                
    filtrado_fecha=filtrado[(filtrado['fecha_datetime'] >= fecha_inicio) & (filtrado['fecha_datetime'] <= fecha_fin)]   
    

    for feature in selected_metrics:
        sns.lineplot(data=filtrado_fecha, x='fecha_datetime', y=feature, label=feature)
        
    plt.xlabel('Fecha',fontsize=12)
    plt.ylabel('Características', fontsize=12)
    plt.tick_params(axis='both', labelsize=16)
    plt.xticks(rotation=90)
    plt.grid(True)
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    # Envía el gráfico al usuario a través de Telegram
    bot.send_photo(chat_id, photo=img_buffer)
    plt.clf()
    markup = types.InlineKeyboardMarkup(row_width=1) 
    itembtn1 = types.InlineKeyboardButton('Sí✅', callback_data='/prediccion') 
    itembtn2 = types.InlineKeyboardButton('No✖️', callback_data='/resultados') 
    
    markup.add(itembtn1)
    markup.add(itembtn2)
    bot.send_message(chat_id,"¿Quiere conocer una predicción de su estado de ánimo en los próximos días?", reply_markup=markup) 

#Módulo de predicción en secuencia temporal de estado de ánimo
@bot.callback_query_handler(func=lambda call: call.data == '/prediccion')
def generar_prediccion(pm):
    filtrado=young[(young["ID"]==features["ID"])]
    filtrado=filtrado[(filtrado['fecha_datetime'] >= fecha_inicio) & (filtrado['fecha_datetime'] <= fecha_fin)]
    filtrado.set_index('fecha_datetime', inplace=True)
    duplicates = filtrado.index[filtrado.index.duplicated()]
    filtrado = filtrado[~filtrado.index.duplicated()]
    bot.send_message(pm.message.chat.id, "A tráves del algoritmo de ARIMA podemos predecir como será tu estado de ánimo a futuro.")
    # Ajustar el modelo ARIMA para predecir el estado de ánimo (por ejemplo)
    p = 1  # Orden del componente autoregresivo
    d = 1  # Orden de diferenciación
    q = 1  # Orden del componente de media móvil

    # Ajustar el modelo ARIMA para el estado de ánimo
    model = ARIMA(filtrado['Motivación'], order=(p, d, q))
    results = model.fit()

    # Realizar predicciones para el estado de ánimo (por ejemplo)
    forecast_steps = 30  # Número de pasos a predecir (30 días en este caso)
    forecast = results.get_forecast(steps=forecast_steps).predicted_mean

    img_buffer = io.BytesIO()
    
    # Visualizar las predicciones para el estado de ánimo
    
    plt.plot(filtrado.index, filtrado['Estado de ánimo'], label='Estado de ánimo')
    plt.plot(pd.date_range(start=filtrado.index[-1], periods=forecast_steps, freq='D'), forecast, label='Predicción de Estado de ánimo',linestyle='dashed')
    plt.title('Predicción de Estado de ánimo de un Paciente Bipolar con ARIMA',fontsize=20)
    plt.xlabel('Fecha',fontsize=18)
    plt.ylabel('Puntuación de Estado de ánimo',fontsize=18)
    plt.tick_params(axis='both', labelsize=16)
    plt.grid(True)
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    # Envía el gráfico al usuario a través de Telegram
    bot.send_photo(pm.message.chat.id, photo=img_buffer)
    plt.clf()
    resultados(pm)

#Finalizacion de charla y encuesta de feedback
@bot.callback_query_handler(func=lambda call: call.data == '/finalizar')
def finalizar(pm):
    markup = types.InlineKeyboardMarkup(row_width=1) 
    itembtn1 = types.InlineKeyboardButton('Encuesta de feedback💬', url="https://forms.gle/oiCVuP2MaF62iBzn9") 
    markup.add(itembtn1)
    bot.send_message(pm.message.chat.id,"¡Gracias por utilizar nuestro chatbot para obtener información sobre el trastorno bipolar! Estamos interesados en mejorar nuestra plataforma y nos gustaría conocer tu opinión. ¿Te gustaría tomarte un momento para completar una breve encuesta?",reply_markup=markup) 


#Bucle de recepción de mensajes de inicio
@bot.message_handler(func=lambda message: True)
def handle_saludo(message):
    if message.text.lower() in ["hola", "buenas", "saludos"]:
        bot.reply_to(message, "¡Hola! 👋 ¿Como estás?, soy Bipotest un asistente virtual 🤖 que te ayudara con tu diagnóstico y seguimiento de estado del trastorno bipolar..... ")
        consentimiento(message)
    elif message.text.lower() in ["adiós", "chao", "hasta luego","gracias","chau","muchas gracias"]:
        bot.reply_to(message, "Gracias por usar el chatbot, estoy aquí si me necesitas. ")

    elif message.text.lower() in ["ayuda","sos","socorro"]:
        urgencia(message)
    else:
        bot.reply_to(message, "No entiendo lo que dices 😔. ¿En qué puedo ayudarte? Para mayor información ingrese el comando /help")





if __name__=='__main__':
    
	print("********INICIANDO EL BOT**********")
    
	bot.infinity_polling()


    


