import os
import base64, io, json, time, urllib.request
from PIL import Image, ImageDraw
im = Image.new('RGB', (640,360), 'white')
d = ImageDraw.Draw(im)
d.rectangle((60,90,220,230), fill='red')
d.ellipse((400,90,550,240), fill='blue')
d.line((240,160,370,160), fill='black', width=7)
d.polygon([(370,160),(350,148),(350,172)], fill='black')
f=io.BytesIO(); im.save(f,format='PNG')
url=os.environ.get('OPENAI_BASE_URL', 'http://127.0.0.1:11445/v1').rstrip('/') + '/chat/completions'
def ask(content,n=150):
 b={'model':'qwen3.8:27b','messages':[{'role':'user','content':content}],'max_tokens':n,'temperature':0,'chat_template_kwargs':{'enable_thinking':False}}
 t=time.monotonic()
 try:
  r=json.load(urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(b).encode(),headers={'Content-Type':'application/json'}),timeout=180))
  print(json.dumps({'seconds':time.monotonic()-t,'response':r}),flush=True)
 except urllib.error.HTTPError as e:
  print(e.code,e.read().decode(),flush=True); raise
ask([{'type':'text','text':'Describe the shapes, their colors and the direction of the arrow in this image. Be brief.'},{'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(f.getvalue()).decode()}}])
for _ in range(3):
 ask('Count from 1 to 80, separated by commas. No explanation.',128)
