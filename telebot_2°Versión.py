import telebot
import numpy as np
import pandas as pd
from telebot.types import ReplyKeyboardMarkup
import re
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

features = {}


bot = telebot.TeleBot("6242548752:AAEpxVC4y-4KgMy5hCY7A8xOIWjbP0YRopc")

young = pd.read_csv('./diario.csv', sep=';')
young = young[young['Código'] != 'O']

@bot.message_handler(commands=['entrevista'])
def bienvenida(pm):

    send_msg=bot.send_message(pm.chat.id, "Bienvenido a Bipotest, soy un asistente virtual que te ayudara con tu diagnóstico")
    send_msg=bot.send_message(pm.chat.id, "¿Puedes indicarme tu nombre?")
    bot.register_next_step_handler(send_msg, saludar)

def saludar(pm):
    nombre=pm.text
    bot.send_message(pm.chat.id, "Hola "+nombre+", voy a asistirte con tu diagnostico virtual")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
        bot.register_next_step_handler(sent_msg, validar_animo)

def motivacion(pm):
    
    valor=int(pm.text)
    if -3 <=valor<=3:
        features["animo"]=valor
        motivacion(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
        bot.register_next_step_handler(sent_msg, validar_calidad)

def cigarrillos(pm):
    sent_msg = bot.send_message(pm.chat.id, "Cantidad de cigarrillos ? ")
    bot.register_next_step_handler(sent_msg, validar_cigarrillos)

def validar_cigarrillos(pm):
    valor=pm.text
    if valor.isnumeric():
        features["cigarrillos"]=valor
        cafeina(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
        bot.register_next_step_handler(sent_msg, validar_cigarrillos)



def cafeina(pm):
    sent_msg = bot.send_message(pm.chat.id, "Indique cantidad consumida de cafeina en mg, Te indico algunas referencias: \n\nTaza de té negro = 60 \nLata de Red Bull 250 ml = 80 \nLata de cola 330ml = 30 \nCafé exprés = 90")
    bot.register_next_step_handler(sent_msg, validar_cafeina)

def validar_cafeina(pm):
    valor=pm.text
    if valor.isnumeric():
        features["cafeina"]=valor
        alcohol(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
        bot.register_next_step_handler(sent_msg, validar_cafeina)

def alcohol(pm):
    sent_msg = bot.send_message(pm.chat.id, "¿Consumio alcohol ? Ingrese Si o No")
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
    sent_msg = bot.send_message(pm.chat.id, "¿Consumio alguna droga? Ingrese Si o No")
    bot.register_next_step_handler(sent_msg, validar_drogas)

def validar_drogas(pm):
    valor=pm.text
    if (valor=="Si" or valor=="No"):
        features["drogas"]=valor
        despertar(pm)
    else: 
        sent_msg = bot.send_message(pm.chat.id, "Ingreso un valor incorrecto, Reingreselo por favor")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
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
        sent_msg = bot.send_message(pm.chat.id, "El valor no se encuentra en el rango, Reingreselo por favor")
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

    X_train, X_test, y_train, y_test = train_test_split(young.drop(["Código","Fecha","Alcohol","Otras drogas","Hora de despertar","Hora a la que te dormiste","Ciclo menstrual"],axis=1),young['Código'],test_size=0.33, random_state=10)

    print(X_train)
    print(X_test)
    print(y_train)


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
    current_day = datetime.date.today()
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
            features["cigarrillos"], features["cafeina"],features["alcohol"],features["drogas"],features["despertar"],features["dormir"],features["codigo"],features["fecha"]],index=['Estado de ánimo','Motivación','Problemas de concentración y atención','Irritabilidad','Ansiedad','Calidad del sueño','Número de cigarrillos','Cafeína','Alcohol','Otras drogas','Hora de despertar','Hora a la que te dormiste','Código','Fecha']),ignore_index=True)
    print(youngNew)
    
    youngNew.to_csv('./diario.csv', sep=';',index=False)

    #Guarda en el archivo los datos nuevos
    #youngNew.to_excel('Resultados.xlsx')
    sent_msg = bot.send_message(pm.chat.id,"Gracias por responder, Hasta luego")
    

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
def handle_help(message):
    chat_id = message.chat.id
    help_message = "¡Bienvenido! Este bot te permite realizar una entrevista para evaluar tus características. Para comenzar, usa el comando /entrevista. "
    help_message += "Sigue las instrucciones para responder las preguntas. Al final de la entrevista, podes evaluar tu seguimiento con el comando /resultados."
    bot.send_message(chat_id, help_message)


@bot.message_handler(commands=['resultados'])
def resultados(message):
    chat_id = message.chat.id
    mensaje= "Para poder realizar tu seguimiento vas a poder evaluar tus resultados según distintos gráficos de analisis de datos. \n \n 1) Ingrese el comando '/temporal' para poder ver el análisis temporal de tus caracteristicas \n \n 2) Ingrese '/correlacion' para ver la relación entre carácteristicas \n \n 3) Ingrese el comando '/boxplot' para revisar la dispersion de datosa en formato de diagrama de cajas "
    bot.send_message(chat_id, mensaje)

@bot.message_handler(commands=['correlacion'])
def mapa_correlacion(pm):
    bot.send_message(pm.chat.id, "Aquí puedes observar como se relacionan tus datos.")
    df=young["Código"]==features["codigo"]
    dfC=young[df]
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
    bot.send_photo(pm.chat.id, photo=img_buffer)



@bot.message_handler(commands=['boxplot'])
def mapa_boxplot(pm):
    bot.send_message(pm.chat.id, "Aquí puedes observar como se distribuyeron tus datos y cuales fueron valores atípicos.")
    df=young["Código"]==features["codigo"]
    dfC=young[df]
    
    img_buffer = io.BytesIO()
    plt.figure(figsize=(8, 6))
    dfC.boxplot(column=["Motivación","Calidad del sueño","Ansiedad","Irritabilidad","Estado de ánimo"],figsize=(15, 15))
    plt.savefig(img_buffer, format='png')

    img_buffer.seek(0)
   

    # Envía el gráfico al usuario a través de Telegram
    bot.send_photo(pm.chat.id, photo=img_buffer)




@bot.message_handler(commands=['temporal'])
def generar_graficos(pm):
    bot.send_message(pm.chat.id, "Aquí puedes observar como variaron tus comportamientos en el ultimo tiempo.")
    # Utiliza las respuestas almacenadas en respuestas_entrevista[chat_id]
    # para generar tus gráficos
    young['fecha_datetime'] = pd.to_datetime(young['Fecha'], format='%d/%m/%Y')

    filtrado=young[young["Código"]==features["codigo"]]
    plt.figure(figsize=(30, 10))
    caracteristicas=['Motivación','Calidad del sueño','Ansiedad','Irritabilidad','Estado de ánimo']
    for feature in caracteristicas:
        sns.lineplot(x='fecha_datetime', y=feature,data=filtrado, label=feature)
    plt.xlabel('Fecha')
    plt.ylabel('Características')
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
   

    # Envía el gráfico al usuario a través de Telegram
    bot.send_photo(pm.chat.id, photo=img_buffer)



@bot.message_handler(func=lambda message: True)
def handle_saludo(message):
    if message.text.lower() in ["hola", "Buenas", "ayuda", "saludos"]:
        bot.reply_to(message, "¡Hola! Soy Bipotest ¿En qué puedo ayudarte?, para mas información ingrese el comando /help")
    elif message.text.lower() in ["adiós", "chao", "hasta luego","gracias"]:
        bot.reply_to(message, "¡Hasta luego! Siempre estoy aquí si me necesitas.")
    else:
        bot.reply_to(message, "No entiendo lo que dices. ¿En qué puedo ayudarte? Para mayor información ingrese el comando /help")



if __name__=='__main__':
    
	print("********INICIANDO EL BOT**********")
    
	bot.infinity_polling()
    

    


