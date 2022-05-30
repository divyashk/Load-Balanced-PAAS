import requests
url = 'http://127.0.0.1:6969/build-from-hub'
# url = 'http://127.0.0.1:6969/build-from-zip'
res = requests.post(url , data = {'repo' : "digitalocean/flask-helloworld"})
# res = requests.post(url , data = {'appname' : "flask-helloworld"} , files={'file': open('app.zip','rb')})
print(res.text)