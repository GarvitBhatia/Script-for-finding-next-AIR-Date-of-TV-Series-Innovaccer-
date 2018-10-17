import requests 
from bs4 import BeautifulSoup as BS
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import mysql.connector

def send_mail(to,msg):
    body=MIMEMultipart()
    body['From']='tv.series.reminder.noreply@gmail.com'
    body['To']=to
    body['Subject'] ='Reminder Mail for TV Series'
    body.attach(MIMEText(msg,'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("tv.series.reminder.noreply@gmail.com", "admin@123J")
    server.sendmail('tv.series.reminder.noreply@gmail.com',to,body.as_string())
    print('Check your Inbox')
    
def scrap(email,x):
    query=x.replace(' ', '%20')
    url_ = "https://www.imdb.com/find?q="+query.lower()+"&s=tt&ttype=tv&ref_=fn_tv"
    r = requests.get(url_,{}) 
    soup = BS(r.text,'lxml')
    
    result=soup.find_all(class_='result_text')
    
    link="https://www.imdb.com"  
    if len(result)==0:
        print('No such series found')
        return ''
    name=result[0].text.strip()
    if 'movie' in result[0].text.lower().replace('.',''):
        print('No such series found')
        return ''

    if x.lower().replace('.','').replace('-','') in result[0].text.lower().replace('.','').replace('-',''):
        if x.lower().replace('.','').replace('-','')==result[0].text.lower().replace('.','').replace('-',''):
            link+=result[0].find('a').attrs['href']
        else:
            print("Did you mean: "+name+" ? [y/n]:")
            op=input()
            if op.lower()=='y':
                link+=result[0].find('a').attrs['href']
            else:
                return ''
    else:
        print("Did you mean: "+name+" ? [y/n]:")
        op=input()
        if op.lower()=='y':
            link+=result[0].find('a').attrs['href']
        else:
            return ''
    
        

    r = requests.post(link,{})

  
    soup = BS(r.text,'lxml')
    z=soup.find_all('div',class_='seasons-and-year-nav')
    link="https://www.imdb.com"
    link+=z[0].find('a').attrs['href']
  
    r = requests.post(link,{})

    soup = BS(r.text,'lxml')
    z=soup.find_all('div',class_='airdate')
    present=datetime.now()
    prefix=''
    msg=''
    idx=0
    for dt in z:
        var=dt.text.replace('\n','').replace('.','')
        spl=var.strip().split(' ')
        obj=datetime.now()
        spl=list(filter(None,spl))
        if len(spl)==3:
            obj=datetime.strptime(spl[0]+spl[1]+spl[2],"%d%b%Y")
            if obj>present:
                if idx==0:
                    prefix='Next season of '
                else:
                    prefix='Next episode of '
                msg=' will Air on ' +spl[0]+" "+spl[1]+" "+spl[2]
                break
        elif len(spl)==2:
            if idx==0:
                prefix='Next season of '
            else:
                prefix='Next episode of '
            msg=' will Air in '+spl[0]+" "+spl[1]
        elif len(spl)==1:
            if idx==0:
                prefix='Next season of '
            else:
                prefix='Next episode of '
            msg=' will Air in '+spl[0]
        else:
            prefix='The Air date for next episode of '
            msg=' is not known'
            break
        idx+=1
    if msg=='':
        prefix=''
        msg=' is no more being streamed'
    return prefix+name+msg
    
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root"
)

c=mydb.cursor()

c.execute("create database if not exists scrapping")
c.execute("use scrapping")
c.execute("create table if not exists input (email varchar(200), series varchar(200))")

print('Enter your Email-ID: ')
email=input()
print('Enter the title of your TV Series: ')
input_string=input()
inp=[]
inp=input_string.split(",")
msg=''
for i in inp:
    c.execute("insert into input values('"+email+"','"+i+"')")
    temp=scrap(email, i)
    if temp!='':
        msg+=temp+'\n'
send_mail(email, msg)