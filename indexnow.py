"""Ping IndexNow (Bing, Yandex, etc.) with every URL in dist/sitemap.xml. Run after deploy: python3 indexnow.py"""
import json,re,urllib.request,urllib.error
src=open("build.py").read()
KEY=re.search(r'INDEXNOW_KEY="([0-9a-f]+)"',src).group(1)
urls=re.findall(r"<loc>(.*?)</loc>",open("dist/sitemap.xml").read())
host="usethissi.vercel.app"
body=json.dumps({"host":host,"key":KEY,"keyLocation":f"https://{host}/{KEY}.txt","urlList":urls}).encode()
req=urllib.request.Request("https://api.indexnow.org/indexnow",data=body,headers={"Content-Type":"application/json; charset=utf-8"})
try:
    r=urllib.request.urlopen(req,timeout=30); print(r.status,len(urls),"urls")
except urllib.error.HTTPError as e:
    print(e.code,e.read()[:300],len(urls),"urls")
