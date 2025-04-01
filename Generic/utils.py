import requests

url = "https://api.zeptomail.com/v1.1/email"

payload = "{\n\"from\": { \"address\": \"<DOMAIN>\"},\n\"to\": [{\"email_address\": {\"address\": \"edwardprosper001@gmail.com\",\"name\": \"Prosper\"}}],\n\"subject\":\"Test Email\",\n\"htmlbody\":\"<div><b> Test email sent successfully.  </b></div>\"\n}"
headers = {
'accept': "application/json",
'content-type': "application/json",
'authorization': "<SEND_MAIL_TOKEN>",
}

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)