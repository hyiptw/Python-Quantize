import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def send_ifttt(v1):   # 定義函式來向 IFTTT 發送 HTTP 要求
    url = ('https://maker.ifttt.com/trigger/名稱/with/'+
          'key/私鑰' +
          '?value1='+str(v1))
    r = requests.get(url)      # 送出 HTTP GET 並取得網站的回應資料
    if r.text[:5] == 'Congr':  # 回應的文字若以 Congr 開頭就表示成功了
        print('Success send (' +str(v1)+') to Line')
    return r.text
