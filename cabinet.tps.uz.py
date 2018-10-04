#!/usr/bin/python3

import sys
import getopt
import requests
import re
from bs4 import BeautifulSoup

if len(sys.argv) <= 1:
    print (sys.argv[0],' -u <user> -p <password> -f <output format>')
    sys.exit(1)

def main(argv):
   user = ''
   password = ''
   oformat = 'txt'
   try:
      opts, args = getopt.getopt(argv,"hu:p:f:",["user=","password="])
   except getopt.GetoptError:
      print (sys.argv[0],' -u <user> -p <password> -f <output format>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print (sys.argv[0],' -u <user> -p <password> -f <output format>')
         sys.exit()
      elif opt in ("-u", "--user"):
         user = arg
      elif opt in ("-p", "--password"):
         password = arg
      elif opt in ("-f", "--format"):
         oformat = arg
      else:
        assert False, "unhandled option" 
       
#   print ('user is "', user)
#   print ('password is "', password)
#   print ('output format', oformat)

   url_login = r'https://cabinet.tps.uz/ru/login'
   url_main = r'https://cabinet.tps.uz/ru'
  
   payload = {
              'LoginForm[username]': user,
              'LoginForm[password]': password,
                  }
   
   headers = {
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate',
              'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
              'Connection': 'keep-alive',
              'Host': 'cabinet.tps.uz',
              'X-Requested-With': 'XMLHttpRequest'
                                  }
   

   with requests.Session() as s:
    r = s.post(url_login, data=payload, headers=headers)
    cookies = {'PHPSESSID': requests.utils.dict_from_cookiejar(s.cookies)['PHPSESSID']}
    
   r2 = requests.get(url_main, cookies=cookies, headers=headers)
     
   #print(r2.status_code)
   #print(r2.url)
   #print(r2.text)


   tariff = 0
   tariff_date = 0
   login = 0
   ipaddr = 0
   tariff_pay = 0
   status = 0
   balance = 0
   jet_balance = 0
   used = 0
   unused = 0


# Create a BeautifulSoup object
   soup = BeautifulSoup(r2.text, 'html.parser')


# get profile
   block_left_list = soup.find(class_='profile')
#print(block_left_list) 
   block_left_list_items = block_left_list.find_all('strong')

   for block_left in block_left_list_items:
    tariff = block_left.contents[0]
    print(block)

# Get service tarif info and status

   service_list = soup.find(class_='service')
#print(service_list) 
   service_header = service_list.find('p')
#print(service_header.contents[0].contents[0])
   tariff = service_header.contents[0].contents[0]
#print(service_header.contents[1].strip())
   tariff_date = service_header.contents[1].strip()
   service_list_items = service_list.find_all('td')


   login = service_list_items[0].contents[0]
   ipaddr = service_list_items[1].contents[0]
   tariff_pay = service_list_items[2].contents[0]
   status = service_list_items[3].contents[0]

# Get balance

   balance = soup.find('strong', {'class':'balance'})
#print(balance.contents[0]) 
   balance = balance.contents[0]
#block_left_list_items = block_left_list.find_all('p')

#for block_left in block_left_list_items:
# block = block_left.contents[0]
# print(block)

# get jet points
   block_left_fl = soup.find('div', {'class':'block left'} )
   block_left_jet = block_left_fl.find_next('div', {'class':'block left'} )

   jetpoints = block_left_jet.find('span')

#print(jetpoints.contents[0])
   jet_balance=jetpoints.contents[0]

   traffic = re.compile("(\w+): '(.*?)'")
   script = soup.find("script", text=traffic)
#print(script.text)

   traffic_data = re.findall("value:\s+(\d+.\d+)", script.text)

#print(traffic_data)
#print(traffic_data[0])
#print(traffic_data[1])
   used = traffic_data[0]
   unused = traffic_data[1]

   if oformat == 'txt':
     print("Тариф: ",tariff,' (',tariff_date,')', sep="")
     print("Абон. плата:",tariff_pay)
     print("Статус:",status)
     print("Баланс:",balance)
     print("JetPoints:",jet_balance)
     print("Логин:",login)
     print("IP адрес:",ipaddr)
     print("Использовано:",used)
     print("Осталось:",unused)
   elif oformat == 'json':
     print("{")
     print('"tariff": "',tariff,'",', sep="")
     print('"tariff_date": "',tariff_date,'",', sep="")
     print('"tariff_pay": "',tariff_pay,'",', sep="")
     print('"status": "',status,'",', sep="")
     print('"balance": "',balance,'",', sep="")
     print('"jet_balance": "',jet_balance,'",', sep="")
     print('"login": "',login,'",', sep="")
     print('"used": "',used,'",', sep="")
     print('"unused": "',unused,'",', sep="")
     print("}")
   elif oformat == 'used':
     print(used,'/',unused)

if __name__ == "__main__":
   main(sys.argv[1:])
