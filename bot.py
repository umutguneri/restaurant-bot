
import json
import requests
import re
import time
import urllib
import datetime

from random import randint
from dbhelper import DBHelper

db = DBHelper()

#TOKEN = "322250907:AAHhYIskBizbpIK0tgziKHw8k9UBDK4AEQE"
#TOKEN = "395965365:AAGbmgtzHM-l_oGuLD7BIW5QkRZ7e25k29U"
TOKEN = "425044369:AAHS5yc9dU8ETJL6VlSsvPDfd6orE-uW4Ug"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

restaurant_name = ""
restaurant_phone = ""
restaurant_latitude = 0
restaurant_longtitude = 0


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def prepareResponse(text, chat, name):
    with open('word.json') as data_file:
        data = json.load(data_file)
    with open('replies.json') as data_file:
        replies = json.load(data_file)

    #Check greeting
    print("------")

    parts = text.split()
    global restaurant_name, restaurant_phone, restaurant_latitude, restaurant_longtitude
    greeting=0
    location=0
    reservation=0
    contact=0
    menu=0

    for x in parts:
        word = data["greeting"]
        for y in word:
            if re.search(y, x, re.IGNORECASE):
                greeting=1

        word = data["location"]
        for y in word:
            if re.search(y, x, re.IGNORECASE):
                location=1

        word = data["reservation"]
        for y in word:
            if re.search(y, x, re.IGNORECASE):
                reservation=1

        word = data["contact"]
        for y in word:
            if re.search(y, x, re.IGNORECASE):
                contact=1

        word = data["menu"]
        for y in word:
            if re.search(y, x, re.IGNORECASE):
                menu=1

    print(greeting,location,reservation,contact,menu)
    
    if greeting==1 and location==0 and reservation==0 and contact==0 and menu==0:
        r = randint(0, 3)
        k = randint(0, 2)
        word1 = replies["his"]
        word2 = replies["greetingAlone"]
        reply = word1[r] + " " + name + ",\n" + word2[k]
        send_message(reply ,chat)
    
    if greeting==0 and location==1:
        l = randint(0, 2)
        loc = replies["location"]
        send_message(loc[l],chat)
        send_location(restaurant_latitude, restaurant_longtitude, chat);
    
    if greeting==1 and location==1:
        r = randint(0, 3)
        k = randint(0, 1)
        l = randint(0, 2)
        word1 = replies["his"]
        word2 = replies["greeting"]
        loc = replies["location"]
        reply = word1[r] + " " + name + ",\n" + word2[k] + "\n\n" + loc[l]
        send_message(reply,chat)
        send_location(restaurant_latitude, restaurant_longtitude, chat);
        greeting=0

    if greeting==0 and contact==1:
        c = randint(0, 2)
        con = replies["contact"]
        reply = con[c] + " " + restaurant_phone
        send_message(reply,chat)
    
    if greeting==1 and contact==1:
        r = randint(0, 3)
        k = randint(0, 1)
        c = randint(0, 2)
        word1 = replies["his"]
        word2 = replies["greeting"]
        con = replies["contact"]
        reply = word1[r] + " " + name + ",\n" + word2[k] + "\n\n" + con[c] + " " + restaurant_phone
        send_message(reply,chat)
        greeting=0


    if greeting==0 and menu==1:
        send_message("We are still working on showing the menu",chat)

    if greeting==1 and menu==1:
        send_message("Hi, /nSorry but we are still working on showing the menu",chat)
        greeting=0

    if greeting==0 and reservation==1:
        send_message("We are still working on taking reservations",chat)
    
    if greeting==1 and reservation==1:
        send_message("Hi, \nWe are still working on taking reservations",chat)
        greeting=0




    #Unclear request
    if greeting==0 and location==0 and reservation==0 and contact==0 and menu==0:
        reply = "Sorry " + name + ", " + "I'm still new at this job, what did you mean ?"
        send_message(reply,chat)




#    if data["greeting"][0] in text:

#    if re.search("hi", text, re.IGNORECASE) or re.search("hey", text, re.IGNORECASE) or re.search("hello", text, re.IGNORECASE) or re.search("moin", text, re.IGNORECASE) or re.search("hallo", text, re.IGNORECASE):
#        mes = ("Hey "+clientName+"\n")
#            send_message(mes,chat)

    return 3,2,3

#Handling a Last Message from User
def handle_updates(updates):
    for update in updates["result"]:
        #Get chat details
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        clientName = update["message"]["chat"]["first_name"]
        
        #Get restaurant info
        resName = db.get_restaurant("name")
        resNum = db.get_restaurant("phone")
        resLocationlong = db.get_restaurant("long")
        resLocationlat = db.get_restaurant("lat")
        
        #items = db.get_items(chat)
        #print(text.lower() in "number".lower())
        
#        p=text.split()
#        print(len(p))
#        print(data["greeting"])

        #Analyse Response
        k = prepareResponse(text, chat, clientName)

        #Check Reservation
        global Command

        # If the message is a command (/new), we have to show a screen with possible dates
        # and we have to get Reservation date, hour and table from customer step by step.
        if text=="/new" or text=="i want to make a reservation":
            showDates(updates)
            text = "/new"
            Command = text

        # If the message is a command (/cancel), we have to ask to customer his Reservation ID
        # and if it is correct ID , we able to delete this reservation from Database
        elif text=="/cancel" or text=="i want to cancel my reservation":
            send_message("Please enter your reservation ID to cancel:", chat, None)
            text = "/cancel"
            Command = text

        #Showing to screen all Reservations in Restaurants
        elif text=="/show" or text=="i want to see all Reservations":
            showList(updates)

        #For any different Message except Commands(new,cancel,show)
        else:
            handle_command(updates,chat)


#        print(k[0])


#        if text in items:
#            db.delete_item(text, chat)
#            items = db.get_items(chat)
#            message = "\n".join(items)
#            send_message(message, chat)
#        else:
#            db.add_item(text, chat)
#            items = db.get_items(chat)
#            message = "\n".join(items)
#            send_message(message, chat)

# Creating a Reservation with selected reservation date, reservation hour and table
def new(updates):
    global reservationDate,reservationHour,table_ID,Command
    if reservationDate==None :             #1.Step, Showing a possible Reservation Date , Getting a selected Reservation Date from Customer
        for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            reservationDate=text
            keyboard = build_keyboard(Hourlist)
            send_message("Reservation Date Selected.Reservation Hour?", chat, keyboard)

    elif reservationHour==None :          #2.Step, Showing a possible Reservation Hours , Getting a selected Reservation Hour from Customer
        for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            reservationHour = text
        freetables = db.get_freetables(reservationDate,reservationHour)
        List=[]
        for value in freetables:
            print("table:",value)
            List.append(str(value))
        keyboard = build_keyboard(List)
        if not List:
            send_message("There is no free table!", chat, keyboard)
            table_ID = None
            reservationDate = None
            reservationHour = None
            Command = None
        else:
            send_message("Reservation Hour Selected,Free Tables:", chat, keyboard)
    
    elif table_ID == None:               #3.Step, Showing a free tables in Restaurant, Getting a selected table from Customer
        for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
        send_message("Table selected, Please enter your name:", chat, None)
        table_ID=text
    else:                               #Last Step, Giving an unique ID to Customer. With this Id Customer can cancel his Reservation
        for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
        customerName=text
        send_message("Reservation is completed, Your reservation ID:", chat, None)
        reservation_ID=db.add_reservation(customerName,reservationDate,table_ID,reservationHour)
        send_message(str(reservation_ID), chat, None)
        table_ID = None
        reservationDate = None
        reservationHour = None
        Command = None

# Canceling a Reservation with received ID from Customer
def cancel(updates):
    global Command
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        reservation_ID = text
        db.cancel_reservation(reservation_ID)  #Deleting a Reservation from Database with received ID
        send_message("Your reservation is canceled!",chat,None)
        Command = None

#Showing a possible Reservation Dates to the Customer
def showDates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = Daylist
        keyboard=build_keyboard(items)
        send_message("Dates:", chat, keyboard)

# Showing all Reservations in Restaurant to the Screen
def showList(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        reservationsList = db.get_List()
        for value in reservationsList:
            send_message(str(value), chat, None)

def handle_command(updates,chat):
    if Command=="/new" : #If the command has been already defined as a "/new" command , "new" function is called.
        new(updates)
    elif Command=="/cancel": #If the command has been already defined as a "/cancel" command , "cancel" function is called.
        cancel(updates)
    else: #For any meaningless message
        send_message("I am sorry. I did not understand you, please write again! These are possible commands: /new /cancel /show ...",chat,None)

#Generating Reservation Dates and Reservation Hours
def set_Date():
    global Daylist
    global Hourlist
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    Daylist = []
    Daylist.append(str(today))
    
    for i in range(0, 5):
        today = today + one_day
        Daylist.append(str(today))

    start_hour = datetime.timedelta(hours=9)
    one_hour = datetime.timedelta(hours=1)
    Hourlist = []
    Hourlist.append(str(start_hour))

    for i in range(0, 14):
        start_hour = start_hour + one_hour
        Hourlist.append(str(start_hour))

#Getting a last message and last chat id from application
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

#Building a keyboard with any kind of list
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

#Sending a message to user
def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def send_location(latitude,longitude, chat_id, reply_markup=None):
    url = URL + "sendLocation?latitude={}&longitude={}&chat_id={}&parse_mode=Markdown".format(latitude,longitude, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)



def main():
    db.setup()   #Creating Database if it doesn't exist
    last_update_id = None
    
    #Restaurant
    restaurantName = db.get_restaurant("name")
    if restaurantName == "0":
        db.create_restaurant("Vapianno","04211683847","53.078846","8.8049183")  #Creating Sample Restaurant
        db.add_table(1,10,0)    #Creating a Sample Restaurant Table (ID INTEGER, Size TEXT, Is it near of window? BOOLEAN)
        db.add_table(2,5,1)     #Creating one more different Table...
        db.add_table(3,15,1)
        db.add_table(4,5,0)
        db.add_table(5,10,1)
        db.add_menu("Water","Small","1.5","drink")         #Creating a Sample Order Menu (Name TEXT, Size TEXT, Price INTEGER,Type TEXT)
        db.add_menu("CocaCola","Small","2","drink")        #Creating one more different Order Menu...
        db.add_menu("Fanta","Small","2","drink")
        db.add_menu("7up","Small","2","drink")
        db.add_menu("Orange Juice","Small","1.5","drink")
        db.add_menu("Apple Juice","Small","1.5","drink")
        db.add_menu("Pasta","Small","3.5","food")
        db.add_menu("Cesar Salad","Small","2.7","food")
        db.add_menu("Lasange","Small","5","food")
        db.add_menu("Pizza","Small","5","food")


    global restaurant_name                                                   #Defining a Global Variables...
    restaurant_name = db.get_restaurant("name")
    global restaurant_phone
    restaurant_phone = db.get_restaurant("phone")
    global restaurant_latitude
    restaurant_latitude = db.get_restaurant("latitude")
    global restaurant_longtitude
    restaurant_longtitude = db.get_restaurant("longtitude")

    #Reservation
    set_Date()     #Calling this function to generate Reservation Dates and Reservation Hours.
    global Command,reservationDate, reservationHour,customerName,table_ID    #Defining a Global Variables...
    Command = None
    reservationDate = None
    reservationHour = None
    customerName = None
    table_ID = None

    while True:
        updates = get_updates(last_update_id)     #Getting last message from application
        if len(updates["result"]) > 0:            #if the message is exist
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)               #Handling a last message from user
        time.sleep(0.5)


if __name__ == '__main__':
    main()