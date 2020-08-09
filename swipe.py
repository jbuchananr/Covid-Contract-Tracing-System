import re
from os import path
from datetime import datetime, timedelta
import pyrebase
import tkinter as tk
from tkinter import ttk
from functools import partial
import simpleaudio as sa
from time import strftime 
# Constants
kZBTYellow = '#ffd203'
kZBTBlue = '#121245' 
newStudentID = ''
newStudentSTRIP = ''

config = {
    "apiKey": "AIzaSyClZ_r-O4VkFsRvQy00mK1tbktR1qnHBGo",
    "authDomain": "zbtscanner.firebaseapp.com",
    "databaseURL": "https://zbtscanner.firebaseio.com",
    "projectId": "zbtscanner",
    "storageBucket": "zbtscanner.appspot.com",
    "messagingSenderId": "848484055790",
    "appId": "1:848484055790:web:c60a43dba75a6bf10fd1ff"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()


def FileCheck():
    if not path.exists('success.wav'):
        storage.child('success.wav').download('success.wav')
    if not path.exists('error.wav'):
        storage.child('error.wav').download('error.wav')

###################################################

# Clears the GUI SCREEN
def clearScreen():
    for widget in root.winfo_children():
        widget.pack_forget()
    mainFrame.place(height=0, width=0, x=0,y=0)
def adminPack():
    clearScreen()
    button1.pack(anchor='nw')
    mainFrame.place(height=750, width=1200, x=250, y=100)
    frameForAdmin.pack(anchor='nw')
    divider.pack(anchor='nw')
    dividerText.set("Filter by Month, Day, and PUID! Note, you can filter by just month and day.")


def mainPack():
    button.pack(anchor='nw')
    lbl.pack(anchor = 'center', pady=100)
    usernameLabel.pack(anchor='center', pady=25)
    cardNumber.pack(anchor='center')
    barStatus.pack(anchor='center')
    swipeLabel.pack(anchor='center')
    swipe1Label.pack(anchor='center')
    swipe2Label.pack(anchor='center')
def newUserPack():
    global newStudentID
    newUserLabel.pack(anchor='center', pady=100)
    idLabelPack2.pack(anchor='center', pady=10)
    nameLabel.pack(anchor = 'center', pady=5)
    createButton.pack(anchor='center', pady=10)
    idLabelPack2.config(text="PUID: " + str(newStudentID))
def clearFrame1():
    clearScreen()
    newUserPack()
    nameLabel.focus()
    return 
def clearFrame2():
    clearScreen()
    mainPack()
    studentID.set("")
    cardNumber.focus()
def loginPack():
    clearScreen()
    button1.pack(anchor='nw')
    adminlabel.pack(anchor='center', pady=100)
    passwordLabel.pack(anchor='center', pady=30)
    passwordEntry.pack(anchor='center') 
    loginButton.pack(anchor='center', pady=30)
    passwordEntry.focus()

# getTime - Takes a date value and converts into the format 08:00 AM
def getTime(time):
    time = str(time.time())
    x = int(time[:2])
    time_string = time[:5]
    if x > 11:
        time_string = time_string[2:]
        if x == 24:
            return ("12" + time_string + " AM")
        elif x == 12:
            return ("12" + time_string + " PM")
        else: 
            num = str(x % 12)
            return(num + time_string + " PM")
    else:
        if x == 0:
            time_string = time_string[2:]
            return ("12" + time_string + " AM")
        return (time_string + " AM")

# log - logs user information into data base. 
def log(user):
    if not db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day)).child(user.key()).get().val():
        # User Does not exist creating new check in for that day
        data = {    "name": user.val()['name'],
            "PUID": user.key(),
            "checkin": True, 
            "times": [str(getTime(datetime.now()))+"-"]
            }
        db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day)).child(user.key()).set(data)

        idVar.set("PUID:  " + str(user.key()))
        nameVar.set("NAME:  " + str(user.val()['name']))
        checkinVar.set("TIMESTAMP:  " + str(getTime(datetime.now()))+"-")
        return
    else:
        # User Exists need to check in or out
        user = db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day)).child(user.key()).get()
        attribute = user.val()
        times = attribute['times']
        if attribute['checkin']:
            times[len(times) - 1] = str(times[len(times) - 1]) + str(getTime(datetime.now()))
            db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day)).child(user.key()).update({"checkin": False, "times": times})
        else:
            times = attribute['times']
            times.append(getTime(datetime.now())+"-")
            db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day)).child(user.key()).update({"checkin": True, "times": times})
        print(user.key())
        print(user.val()['name'])
        idVar.set("PUID:  " + str(user.key()))
        nameVar.set("NAME:  " + str(user.val()['name']))
        checkinVar.set("TIMESTAMP:  " + str(times[len(times) - 1]))
        return

def getUserValue():
    clearFrame1()
# Returns Month in Text form for the data base
def getMonth(argument):
    switcher = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    return(switcher.get(argument, "Invalid month"))
# integrate() Integrates the data base from day to day checking in users as need be 
def integrate():
    clearScreen()
    prevDay = datetime.today() - timedelta(days=1)
    if not db.child('tracing').child(getMonth(datetime.today().month)).get().val():
        # First sign in users from past month
        for user in db.child('tracing').child(getMonth(prevDay.month)).child(int(prevDay.day)).get().each():
            var = user.val()
            if var['checkin'] ==  True:
                print(var['checkin'])
                times = var['times']
                if times[len(times) - 1] == "12:00 AM-":
                    times[len(times) - 1] = times[len(times) - 1] + "*11:59 PM*"
                    data = {"name": user.val()['name'],
                    "PUID": user.key(),
                    "checkin": True, 
                    "times": ["*12:00 AM*-"]}
                elif times[len(times) - 1] == "*12:00 AM*-":
                    times[len(times) - 1] = times[len(times) - 1] + "*11:59 PM*"
                    data = {"name": user.val()['name'],
                    "PUID": user.key(),
                    "checkin": False, 
                    "times": []}
                else:
                    times[len(times) - 1] = times[len(times) - 1] + "11:59 PM"
                    data = {"name": user.val()['name'],
                        "PUID": user.key(),
                        "checkin": True, 
                        "times": ["12:00 AM-"]}
                db.child('tracing').child(getMonth(prevDay.month)).child(int(prevDay.day)).get().child(user.key()).update({"checkin": False, "times": times})
                db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day)).child(user.key()).set(data)
        for day in db.child('tracing').child(getMonth(prevDay.month)).get().each():
            for user in day.get().each():
                var = user.val()
                if var['checkin'] ==  True:
                    print(var['checkin'])
                    times = var['times']
                    times[len(times) - 1] = times[len(times) - 1] + "*11:59 PM*"
                    db.child('tracing').child(getMonth(prevDay.month)).child(int(day)).get().child(user.key()).update({"checkin": False, "times": times})
        clearFrame2()
        return

    if not db.child('tracing').child(getMonth(datetime.today().month)).child(datetime.today().day).get().val():
        # 1 Day Behind Check
        for user in db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day - 1)).get().each():
            var = user.val()
            if var['checkin'] ==  True:
                times = var['times']
                if times[len(times) - 1] == "12:00 AM-" or times[len(times) - 1] == "*12:00 AM*-":
                    times[len(times) - 1] = times[len(times) - 1] + "*11:59 PM*"
                    data = {"name": user.val()['name'],
                    "PUID": user.key(),
                    "checkin": True, 
                    "times": ["*12:00 AM*-"]}
                else:
                    times[len(times) - 1] = times[len(times) - 1] + "11:59 PM"
                    data = {"name": user.val()['name'],
                        "PUID": user.key(),
                        "checkin": True, 
                        "times": ["12:00 AM-"]}
                db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day) - 1).child(user.key()).update({"checkin": False, "times": times})
                db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day)).child(user.key()).set(data)
            else: 
                print("False")
        # 2 Days Behind Check
        for user in db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day - 2)).get().each():
            var = user.val()
            if var['checkin'] ==  True:
                print(var['checkin'])
                times = var['times']
                times[len(times) - 1] = times[len(times) - 1] + "*11:59 PM*"
                db.child('tracing').child(getMonth(datetime.today().month)).child(int(datetime.today().day) - 2).child(user.key()).update({"checkin": False, "times": times})
            else: 
                print("False")
    return

# ProcessCard - Processes the data on PUID
def ProcessCard(carddata):
    wave_obj1 = sa.WaveObject.from_wave_file("error.wav")
    wave_obj2 = sa.WaveObject.from_wave_file("success.wav")
    match = re.search(r'[0-9]{10}',carddata)
    if match is None:
        barStatus.config(background="red", text="Invalid Swipe", foreground="white")
        print('First error')
        play_obj = wave_obj1.play()
        return
    studentID = int(match.group(0))
    if len(str(studentID)) > 9 or len(str(studentID)) < 6:
        print('Second Error')
        barStatus.config(background="red", text="Invalid Swipe", foreground="white")
        play_obj = wave_obj1.play()
        return
    print("ID successfully processed.")
    print("***************************************")
    if not db.child('Users').child(studentID).get().val():
        global newStudentID, newStudentSTRIP
        newStudentID = studentID
        newStudentSTRIP = carddata
        getUserValue()
        return
    user = db.child("Users").child(studentID).get()
    log(user)
    play_obj = wave_obj2.play()
    barStatus.config(background="#43ff00", text="Valid Swipe", foreground="black")
    return

def createUser(key):
    global newStudentSTRIP, newStudentID
    print(enterName.get())
    clearFrame2()
    data = {"name": enterName.get(), "Date Created": str(datetime.today())}
    db.child("Users").child(newStudentID).set(data)
    ProcessCard(newStudentSTRIP)
    enterName.set("")

def createUserButton():
    global newStudentSTRIP, newStudentID
    print(enterName.get())
    clearFrame2()
    data = {"name": enterName.get(), "Date Created": str(datetime.today())}
    db.child("Users").child(newStudentID).set(data)
    ProcessCard(newStudentSTRIP)
    enterName.set("")

def ClearFilter():
    for widget in displayFrame.scrollable_frame.winfo_children():
        widget.pack_forget()
    displayFrame.pack_forget()

# Filters the Admin Screen based off selection
def Filter():
    ClearFilter()
    year = yearVar.get()
    month = monthVar.get()
    day = dayVar.get()
    puid = puidVar.get()
    print(puid)
    if month == "Select Month" or day == "Select Day":
        dividerText.set("Invalid Filter")
        return
    if not db.child('Users').child(puid).get().val() or puid== "":
        if puid != "":
            dividerText.set("Invalid PUID, To search without PUID set the filter to an empty search bar.")
            return
        dividerText.set(month)
        if day == 'Entire Month':
            date = str(month)
            for obj in db.child('tracing').child(month).get().each():
                if (obj.key()) != 0:
                    day = obj.key()
                    date = month + " " + str(day) + " :"
                    tlabel = ttk.Label(displayFrame.scrollable_frame, text=date, font=('calibri', 16), background=kZBTBlue, foreground=kZBTYellow, width=1100)
                    tlabel.pack(anchor='nw', pady=(5, 5))
                    for user in db.child('tracing').child(month).child(int(day)).get().each():
                        text = " PUID: " + str(user.key()) + "     |     Name: " + user.val()['name']
                        label = ttk.Label(displayFrame.scrollable_frame, text=text, font=('calibri', 16))
                        label.pack(anchor='nw', pady=(10, 5))
                        times = ""
                        for stamp in user.val()['times']:
                            times = times + (stamp + ", ")
                        times = times[:(len(times) - 2)]
                        T = tk.Text(displayFrame.scrollable_frame, height=3, width=150)
                        T.insert(tk.END, times)
                        T.configure(state="disabled")
                        T.pack(anchor='nw', pady=(0,10))
        else:
            date = month + " " + day + " :"
            tlabel = ttk.Label(displayFrame.scrollable_frame, text=date, font=('calibri', 16), background=kZBTBlue, foreground=kZBTYellow, width=1100)
            tlabel.pack(anchor='nw', pady=(5, 5))
            for user in db.child('tracing').child(month).child(int(day)).get().each():
                text = " PUID: " + str(user.key()) + "     |     Name: " + user.val()['name']
                label = ttk.Label(displayFrame.scrollable_frame, text=text, font=('calibri', 16))
                label.pack(anchor='nw', pady=(10, 5))
                times = ""
                for stamp in user.val()['times']:
                    times = times + (stamp + ", ")
                times = times[:(len(times) - 2)]
                T = tk.Text(displayFrame.scrollable_frame, height=3, width=150)
                T.insert(tk.END, times)
                T.configure(state="disabled")
                T.pack(anchor='nw', pady=(0,10))
    else:
        print("Valid Student ID")
        dividerText.set("Showing PUID: " + str(puid))
        if day == 'Entire Month':
            date = str(month)
            for obj in db.child('tracing').child(month).get().each():
                if (obj.key()) != 0:
                    day = obj.key()
                    date = month + " " + str(day) + " :"
                    tlabel = ttk.Label(displayFrame.scrollable_frame, text=date, font=('calibri', 16), background=kZBTBlue, foreground=kZBTYellow, width=1100)
                    tlabel.pack(anchor='nw', pady=(5, 5))
                    user = db.child('tracing').child(month).child(int(day)).child(puid).get()
                    text = " PUID: " + str(user.key()) + "     |     Name: " + user.val()['name']
                    label = ttk.Label(displayFrame.scrollable_frame, text=text, font=('calibri', 16))
                    label.pack(anchor='nw', pady=(10, 5))
                    times = ""
                    for stamp in user.val()['times']:
                        times = times + (stamp + ", ")
                    times = times[:(len(times) - 2)]
                    T = tk.Text(displayFrame.scrollable_frame, height=3, width=150)
                    T.insert(tk.END, times)
                    T.configure(state="disabled")
                    T.pack(anchor='nw', pady=(0,10))
        else:
            date = month + " " + day + " :"
            tlabel = ttk.Label(displayFrame.scrollable_frame, text=date, font=('calibri', 16), background=kZBTBlue, foreground=kZBTYellow, width=1100)
            tlabel.pack(anchor='nw', pady=(5, 5))
            user = db.child('tracing').child(month).child(int(day)).child(puid).get()
            text = " PUID: " + str(user.key()) + "     |     Name: " + user.val()['name']
            label = ttk.Label(displayFrame.scrollable_frame, text=text, font=('calibri', 16))
            label.pack(anchor='nw', pady=(10, 5))
            times = ""
            for stamp in user.val()['times']:
                times = times + (stamp + ", ")
            times = times[:(len(times) - 2)]
            T = tk.Text(displayFrame.scrollable_frame, height=3, width=150)
            T.insert(tk.END, times)
            T.configure(state="disabled")
            T.pack(anchor='nw', pady=(0,10))
    displayFrame.pack(anchor='ne', pady=(20, 20), padx=20)
    return

## GUI PART OF THE CODE
class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

##### Scrollable frame class
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        canvas.config(height=500, width=1100)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

# creating tkinter window 
root = tk.Tk()
window = FullScreenApp(root)
root.title('ZBT Card Reader') 
root.configure(background='#121245')

# This function is used to  
# display time on the label 
# Methods dealing with GUI
def time(): 
    string = strftime('%H:%M:%S %p') 
    if (string == "00:00:00 AM"):
        integrate()
    date_time_obj = datetime.strptime(string, '%H:%M:%S %p')
    lbl.config(text = getTime(date_time_obj)) 
    lbl.after(1000, time)

def validateLogin(password):
    try: 
        user = auth.sign_in_with_email_and_password("admin@zbt.com", password.get())
        adminPack()
    except:
        print('bad password')
        try: 
            user = auth.sign_in_with_email_and_password("jbuchananr19@gmail.com", password.get())
            adminPack()
        except:
            print('no super user')
    password.set("")
    return
	

def swiped(key):
    print(studentID.get())
    value = studentID.get()
    ProcessCard(value)
    studentID.set("")
    cardNumber.focus()


def integratelabel():
    integrate()
# GUI Objects

# style configuration
style = ttk.Style(root)
style.theme_use('classic')
style.configure('TLabel', background='white', foreground="black", padding=6)
style.configure('TLabel2', background='red', foreground="black", padding=6)
lbl = ttk.Label(root, font = ('calibri', 100, 'bold'), borderwidth=24, relief='groove', style='TLabel') 
time()

######## MAIN SCREEN LABELS ######### 
usernameLabel = ttk.Label(root, text="   Please Swipe PUID   ", font=('calibri', 72, 'bold'), borderwidth=8, width= 20, relief='ridge', background = ('white'), anchor='center')
studentID = tk.StringVar()
cardNumber = tk.Entry(root, textvariable = studentID,  show='*', font = ('calibri', 40, 'bold'), width = 21) # style="TLabel"
cardNumber.bind('<Return>', swiped)
cardNumber.focus()
barStatus = ttk.Label(root, textvariable="", font=('calibri', 32, 'bold'), width= 24, background = kZBTBlue)
idVar = tk.StringVar()
idVar.set("PUID: ")
swipeLabel = ttk.Label(root, textvariable=idVar, font=('calibri', 32, 'bold'), borderwidth=1, width=25, relief='ridge', background = ('white'))
nameVar = tk.StringVar()
nameVar.set("NAME: ")
swipe1Label = ttk.Label(root, textvariable=nameVar, font=('calibri', 32, 'bold'), borderwidth=1, width=25, relief='ridge', background = ('white'))
checkinVar = tk.StringVar()
checkinVar.set("TIMESTAMP: ")
swipe2Label = ttk.Label(root, textvariable=checkinVar, font=('calibri', 32, 'bold'), borderwidth=1, width=25, relief='ridge', background = ('white'))


######### Create New User Screen ############ 
newUserLabel = ttk.Label(root, text="   Please Enter Your Full Name   ", font=('calibri', 50, 'bold'), borderwidth=8, width= 24, relief='ridge', background = ('#ffd203'), anchor='center')
idLabelPack2 = ttk.Label(root, text="PUID:  ", font=('calibri', 50, 'bold'), borderwidth=8, width= 24, relief='ridge', background = ('white'), anchor='center')
enterName = tk.StringVar()
nameLabel = tk.Entry(root, textvariable = enterName, font = ('calibri', 50, 'bold'), width = 24, background = ('white'))
nameLabel.bind('<Return>', createUser)
createButton = ttk.Button(root, text="Create User", command=createUserButton, width = 30)

button = ttk.Button(root, text="Admin", command=loginPack)



### Login Screen For Admin ###### 
#username label and text entry box
adminlabel = ttk.Label(root, text="ADMIN PAGE", font=('calibri', 50, 'bold'), width = 24, borderwidth = 8, relief='ridge', anchor='center')


#password label and password entry box
button1 = ttk.Button(root, text="Back", command=clearFrame2)
passwordLabel = ttk.Label(root,text="Password", font=('calibri', 50, 'bold'), width =24, anchor='center')
password = tk.StringVar()
passwordEntry = tk.Entry(root, textvariable=password, show='*', font=('calibri', 50, 'bold'), width=24) 

validateLogin = partial(validateLogin, password)

#login button
loginButton = ttk.Button(root, text="Login", command=validateLogin, width=24)

#######DROP DOWN BOX SCREEEN ######
# Add a grid
mainFrame = ttk.Frame(root)
frameForAdmin = ttk.Frame(mainFrame)
displayFrame = ScrollableFrame(mainFrame)
#frameForAdmin.config(background="white")


# Year
yearsLabel = ttk.Label(frameForAdmin,text="Year", font=('calibri', 16), anchor='center')
yearVar = tk.StringVar()
years = ['2020', '2020']
yearVar.set(years[0]) # set the default option
yearChoice = ttk.OptionMenu(frameForAdmin, yearVar, *years)

# Month
monthVar = tk.StringVar()
months = ['Select Month', 'January','Feburary','March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
monthVar.set(months[0]) # set the default option

monthsLabel = ttk.Label(frameForAdmin,text="Month", font=('calibri', 16), anchor='center')
monthChoice = tk.OptionMenu(frameForAdmin, monthVar, *months)
# Day
daysLabel = ttk.Label(frameForAdmin,text="Day", font=('calibri', 16), anchor='center')
dayVar = tk.StringVar()
days = ['Select Day', 'Entire Month']
for num in range(31):
    days.append(str(num + 1))
dayVar.set(days[0]) # set the default option
dayChoice = tk.OptionMenu(frameForAdmin, dayVar, *days)

# PUID

puidLabel = ttk.Label(frameForAdmin, text='PUID', font=('calibri', 16), anchor='center')
puidVar = tk.StringVar()
puidEntry = tk.Entry(frameForAdmin, text="", textvariable=puidVar, font=('calibri', 16,), width=25, background = ('white'))

filterButton = ttk.Button(frameForAdmin, text="Filter", command=Filter)
clearButton = ttk.Button(frameForAdmin, text="Clear", command=ClearFilter)



# Divider
dividerText = tk.StringVar()
dividerText.set("Filter by Month, Day, and PUID! Note, you can filter by just month and day.")
divider = ttk.Label(mainFrame, textvariable=dividerText, font=('calibri', 12, 'bold'), width=150, background='black', foreground=kZBTYellow)


# Positioning
yearsLabel.grid(row=1, column=1, padx=(20, 5), pady=10)
yearChoice.grid(row=1, column=2, padx=(5, 10), pady=10)
monthsLabel.grid(row=1, column=3, padx=(10, 5), pady=10)
monthChoice.grid(row=1, column=4, padx=(5, 10), pady=10)
daysLabel.grid(row=1, column=5, padx=(10, 5), pady=10)
dayChoice.grid(row=1, column=6, padx=(5, 10), pady=10)
puidLabel.grid(row=1, column=7, padx=(10, 5), pady=10)
puidEntry.grid(row=1, column=8, padx= (5, 10), pady=10)
filterButton.grid(row=1, column=9, padx=(10,10), pady=10)
clearButton.grid(row=1, column=10, padx=(10,10), pady=10)
FileCheck()
integrate()
clearFrame2()
root.mainloop()
