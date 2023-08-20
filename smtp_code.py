from PyQt5.uic import loadUi
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QDialog,QApplication,QWidget
import threading,sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import re
import time,csv
# from smtplib import SMTPException

def strChecker(msg,email):
    from datetime import datetime
    current_time = datetime.now().time()
    time = current_time.strftime("%I:%M %p")
    current_date = datetime.now().date()
    date = current_date.strftime("%A, %B %d, %Y")
    domain=email.split("@")[1]
    username=str(email.split("@")[0]).capitalize()

    


    msg=replace_number(msg)
    msg=msg.replace("{domain}",domain).replace("{date}",date).replace("{time}",time).replace("{user}",username).replace("{email}",email)

    return msg

def replace_number(string):
    pattern = r'\{number-(\d+)\}'
    matches = re.findall(pattern, string)

    for match in matches:
        replacement_length = int(match)
        random_number = str(random.randint(10**(replacement_length-1), (10**replacement_length)-1))
        string = string.replace(f"{{number-{match}}}", random_number)


    return string
    


     

class MainScreen(QDialog):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("main.ui",self)
        self.startedSending=False
        self.pauseSending=False
        self.start.clicked.connect(self.process)
        self.addServer.clicked.connect(self.add_Server)
        self.pause.clicked.connect(self.pauseTheSending)
        self.resume.clicked.connect(self.resumeTheSending)
    def resumeTheSending(self):
        if(self.pauseSending):
            self.pauseSending=False
            print("->Resuming...")

    def pauseTheSending(self):
        if(self.startedSending):
            self.pauseSending=True
            print("->Paused :P")
        
        
    def add_Server(self):
        smtpServer=self.server.text()
        smtpUserName=self.user_name.text()
        smtpPass=self.password.text()
        smtpPort=self.port.text()
        with open("smtp Server.csv","a",encoding="utf-8",newline="") as f:
            csv.writer(f).writerow([smtpServer,smtpUserName,smtpPass,smtpPort])
    def return_Server(self):
        smtpServers=[]
        with open("smtp Server.csv","r",encoding="utf-8") as f:
            for server in csv.reader(f):
                if server!=[]:
                    smtpServers.append(server)
        return smtpServers
    def startAfterTime(self):
        hours, minutes = re.findall(r'\d+', self.start_after.text())

        # Convert hours and minutes to integers
        hours = int(hours)
        minutes = int(minutes)

        # Convert hours and minutes to seconds
        total_seconds = (hours * 3600) + (minutes * 60)
        return total_seconds

    def send_email(self):
        try:
            startAfter=self.start_after.text()

            print("->Starting the bot..")
            if(str(startAfter)!=""):
                print(f"Waiting for the {startAfter} time.")
                time.sleep(self.startAfterTime())

            delayTime=self.delay_time.text()
            pauseHere=int(self.pause_here.text())
            senderEmail=self.sender_email.text()
            subjectMsg=self.subject.text()
            bodyMsg=self.body.toPlainText()
            receiverEmails=[]
            with open("emails.csv","r",encoding="utf-8") as f:
                for i in csv.reader(f):
                    if(i!=[]):
                        receiverEmails.append(i[0])
            # SMTP server details

            
            smtpServerdetails=self.return_Server()

            
            index=0
            smtpIndex=0
            while index<len(receiverEmails):
            # Email content
                if not(self.pauseSending):
                    try:
                        smtp_server =smtpServerdetails[smtpIndex][0]
                        smtp_username = smtpServerdetails[smtpIndex][1]
                        smtp_password = smtpServerdetails[smtpIndex][2]
                        smtp_port = int(smtpServerdetails[smtpIndex][3])

                       

                        receiverEmail=receiverEmails[index]
                        print("->Sending mail to ",receiverEmail)
                        
                        # adding paused logic

                        index+=1

                        sender_email = strChecker(senderEmail,receiverEmail)
                    
                        recipient_email = receiverEmail
                        recipient_name=strChecker(str(self.recipient_name.text()),receiverEmail)
                        subject = strChecker(subjectMsg,receiverEmail)
                        message = strChecker(bodyMsg,receiverEmail)

                        # Create the email message
                        email = MIMEMultipart()
                        email['From'] = f'{recipient_name} <{sender_email}>'
                        email['To'] = recipient_email
                        email['Subject'] = subject
                        email['X-Priority'] = '1'  # 1 indicates high priority

                        # Attach the message to the email
                        email.attach(MIMEText(message, 'html'))

                        # Connect to the SMTP server and send the email
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(smtp_username, smtp_password)
                            server.sendmail(sender_email, recipient_email, email.as_string())
                        

                        if(index%pauseHere==0):
                            print(f"->using SMTP Server of {smtp_server}")
                            smtpIndex+=1
                            if(smtpIndex>=len(smtpServerdetails)):
                          
                                smtpIndex=0
                            print(str("->waiting "+delayTime))
                            
                            time.sleep(int(delayTime))

                    except smtplib.SMTPAuthenticationError:
                        print("->SMTP authentication failed. Check your username and password.")

                    except smtplib.SMTPServerDisconnected:
                        print("->SMTP server disconnected unexpectedly.")

                    except smtplib.SMTPConnectError:
                        print("->Failed to connect to the SMTP server.")

                    except smtplib.SMTPHeloError:
                        print("->Error with the SMTP HELO command.")

                    except smtplib.SMTPDataError:
                        print("->Error with the SMTP DATA command.")

                    except smtplib.SMTPException as e:
                        print(f"->An SMTP error occurred:{str(e)}" )

                    except Exception as err:
                        print(f"->Something went wrongs {err}")
        except Exception as err:
            print(f"->Something went wrongs {err}")
        print("===>Completed.")

            


    def process(self):
        self.startedSending=True
 
        t = threading.Thread(target=self.send_email)
        t.daemon=True
        t.start()


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui",self)
        self.login.clicked.connect(self.process)
    def process(self):
        if self.password.text()=="Daniella19922525!":
            
            widget.setCurrentIndex(widget.currentIndex()+1)

app=QApplication(sys.argv)
welcome=Login()

widget= QtWidgets.QStackedWidget()
widget.addWidget(welcome)
main=MainScreen()
widget.addWidget(main)
widget.setFixedWidth(571)
widget.setFixedHeight(440)
widget.show()
try:
    sys.exit(app.exec_())
except Exception as err:
    print(err)
    print('exiting')
    time.sleep(10)