import requests
from datetime import date,datetime
import os
import sys
import smtplib
import time
from time import ctime

requests = requests.Session()
requests.headers.update({'User-Agent': ''})

email_user = '<from_email@email.com>'
email_password = '<password>'

sent_from = email_user
to = ['<to_email@email.com>']

seconds = 30

today = date.today()
should_email = False

__district = "149" # 188 - Gurgaon

# Gurgaon distrcit id: 188
# Faridabad district id: 199
# Nuh district id: 205
# Jhajjar district id: 189
# Rewari district id: 202
# Alwar district id: 512
# South delhi district id: 149
# South west delhi district  id: 150
# South east delhi district id: 144
# West delhi district id: 142

if len(sys.argv) > 1:
	__district = sys.argv[1]

d1 = today.strftime("%d/%m/%Y")

__date = str(d1).replace("/","-")

def send_email(res):
	# turn on allow less secure apps to get email
	#  https://myaccount.google.com/lesssecureapps
	# suggest to use a backup account for this to preserve security
	
	subject = 'Vaccine slot available in your area'
	body = "Following vaccines centers are found \n\n Query Time :  "+ctime(time.time())+"\n\n" + res

	email_text = """\
From: %s
To: %s 
Subject: %s
%s
""" % (sent_from, ", ".join(to), subject, body)
	print email_text

	try:
	    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	    server.ehlo()
	    server.login(email_user, email_password)
	    server.sendmail(sent_from, to, email_text)
	    server.close()

	    print 'Email sent!'
	except Exception as e:
	    print 'Something went wrong...'
	    print (e)
	

def parse_json(result):
	output = []
	centers = result['centers']
	for center in centers:
		sessions = center['sessions']
		for session in sessions:
			if session['available_capacity'] > 0 and session['min_age_limit'] >= 18:
				res = { 'name': center['name'], 'block_name':center['block_name'],'age_limit':session['min_age_limit'], 'vaccine_type':session['vaccine'] , 'date':session['date'],'available_capacity':session['available_capacity'] }
				output.append(res)
	return output
				
	
def call_api():
    print(ctime(time.time()))
    api = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=" + __district+ "&date="+ __date

#     # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
#     try:
#         import http.client as http_client
#     except ImportError:
#     # Python 2
#         import httplib as http_client
#     http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
#     logging.basicConfig()
#     logging.getLogger().setLevel(logging.DEBUG)
#     requests_log = logging.getLogger("requests.packages.urllib3")
#     requests_log.setLevel(logging.DEBUG)
#     requests_log.propagate = True

    response = requests.get(api)
    # print(api)
    # print(response.request.headers)
    # print(response)

    if response.status_code == 200:
        print 'API call success for district id: {}'.format(__district)
        result = response.json()
        output = parse_json(result)
        if len(output) > 0:
            print "Vaccines available"
            print('\007')
            result_str = ""
            for center in output:

                print center['name']
                print "block:"+center['block_name']
                print "vaccine count:"+str(center['available_capacity'])
                print "vaccines type:" + center['vaccine_type']
                print center['date']
                print "age_limit:"+ str(center['age_limit'])
                print "---------------------------------------------------------"
                result_str = result_str + center['name'] + "\n"
                result_str = result_str + "block:"+center['block_name'] + "\n"
                result_str = result_str + "vaccine count:"+str(center['available_capacity']) + "\n"
                result_str = result_str + "vaccine type:"+ center['vaccine_type'] + "\n"
                result_str = result_str + center['date'] + "\n"
                result_str = result_str + "age_limit:"+str(center['age_limit'])+"\n"
                result_str = result_str + "-----------------------------------------------------\n"
            if should_email:
		        send_email(result_str)

        else:
            
            print "Vaccines not available \n"

t = datetime.now()

if __name__ == '__main__':
    while True:
        call_api(); time.sleep(seconds)
