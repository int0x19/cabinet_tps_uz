#!/usr/bin/python3

import sys
import getopt
import requests
import re
from bs4 import BeautifulSoup

user = ''
password = ''
oformat = 'txt'

#r2 = ''
filename = ''

def usage():
    print (sys.argv[0],' -u <user> -p <password> -f <output format: txt, json, used> -i <input_html_file>')

if len(sys.argv) <= 1:
    usage()
    sys.exit(1)

def args(argv):
   try:
      opts, args = getopt.getopt(argv,"hu:p:f:i:",["user=","password="])
   except getopt.GetoptError:
      usage()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         usage()
         sys.exit()
      elif opt in ("-u", "--user"):
         global user
         user = arg
      elif opt in ("-p", "--password"):
         global password
         password = arg
      elif opt in ("-f", "--format"):
         global oformat
         oformat = arg
      elif opt in ("-i"):
         global filename
         filename = arg
      else:
        assert False, "unhandled option" 

def get_data():

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

#   print(r2.status_code)
#   print(r2.url)
#   print(r2.text)
   return r2

def get_file(i):
   data = open(i, 'r').read()
   return data

def parser(data):
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
   package_name = 0
   package_start = 0
   package_end = 0
   package_traffic = 0


# Create a BeautifulSoup object
   if hasattr(data, 'text'):
     soup = BeautifulSoup(data.text, 'html.parser')
   else:
     soup = BeautifulSoup(data, 'html.parser')


# get profile
   block_left_list = soup.find(class_='profile')
   block_left_list_items = block_left_list.find_all('strong')
   for block_left in block_left_list_items:
    tariff = block_left.contents[0]

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

   # get jet points
   block_left_fl = soup.find('div', {'class':'block left'} )
   block_left_jet = block_left_fl.find_next('div', {'class':'block left'} )
   jetpoints = block_left_jet.find('span')
   #print(jetpoints.contents[0])
   jet_balance=jetpoints.contents[0]

   traffic = re.compile("traffic: '(.*?)'")
   #print("traffic:")
   #print(traffic)
   script = soup.find("script", text=traffic)
   #print(script)
   #print(script.text)
   if script:
     traffic_data = re.findall("value:\s+(\d+)", script.text)
     #print("traffic data:")
     #print(traffic_data)
     #print(traffic_data[0])
     #print(traffic_data[1])
   
#     if traffic_data[0]:
     used = traffic_data[0]
#     else:
#      used = "0"
     # print(traffic_data[1])
#     if traffic_data[1]:
     unused = traffic_data[1]
#     else:
#      unused = "0"
   else:
    used = "0"
    unused = "0"
   
   p = soup.find('div', {'id':'package_rest'})
   if p:
    #print(p)
    p_name = p.find('strong') 
    #print(p_name.contents)
    package_name = p_name.contents[0]
    p_start = p_name.find_next('strong')
    #print(p_start.contents)
    package_start = p_start.contents[0]
    p_end = p_start.find_next('strong')
    #print(p_end.contents)
    package_end = p_end.contents[0]
    p_traff = p_end.find_next('strong')
    #print(p_traff.contents)
    package_traffic = re.findall(r'\d+',p_traff.contents[0])[0]

    
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
     if p:
         print("Пакет: ",package_name)
         print(" Активирован: ", package_start)
         print(" Закончится: ", package_end)
         print(" Остаток: ", package_traffic)
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
     if p:
         print('"package_name": "', package_name,'",', sep="")
         print('"package_start": "', package_start,'",', sep="")
         print('"package_end": "', package_end, '",', sep="")
         print('"package_traffic": "', package_traffic, '",', sep="")
     print("}")
   elif oformat == 'used':
     print(used,'/',unused)

def main():
   args(sys.argv[1:])
#   get_data()
   if filename:
    parser(get_file(filename))
   else:
    parser(get_data())

if __name__ == "__main__":
   main()
