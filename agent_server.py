"""Local HTTP/UI entry point to a single-model CrewAI agent in Docker."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
import time
import uuid
from urllib.request import urlopen
from crewai_helper import answer, resolve_model, BASE_URL

LOCK = threading.Lock()
PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local AI Model Comparison</title>
<style>body{font:16px system-ui;max-width:900px;margin:40px auto;padding:16px;background:#171524;color:#eee}textarea{width:100%;height:150px}button,select{padding:12px;margin:8px 8px 8px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#252235;padding:18px}small{color:#bbb}</style>
<h1>Local AI Model Comparison</h1><p>Docker → CrewAI (one agent) → Ollama → selected model only</p>
<select id="model"><option value="qwen">Qwen 1.5B</option><option value="llama">Llama 1B</option></select>
<textarea id="prompt" placeholder="Enter an identical prompt for each model"></textarea><br><button id="run">Run selected model</button>
<small>No shared model answers. No conversation memory. No cloud model.</small><pre id="result">Ready.</pre>
<script>document.getElementById('run').onclick=async()=>{const b=document.getElementById('run'),out=document.getElementById('result');b.disabled=true;out.textContent='Working locally...';try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:document.getElementById('model').value,prompt:document.getElementById('prompt').value})});const d=await r.json();out.textContent=JSON.stringify(d,null,2)}catch(e){out.textContent=String(e)}finally{b.disabled=false}};</script></html>'''


def run_request(model, prompt):
    selected = resolve_model(model)
    started = time.perf_counter()
    with LOCK:
        result = answer(prompt, 'Complete the user task directly. Use the requested language and format. Do not claim to access the internet. Return the requested content.', model=selected, max_tokens=1500)
    return {'model':selected,'engine':'crewai','agent_count':1,'task_count':1,
            'seconds':round(time.perf_counter()-started,2),'response':result}


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path=='/':
            body=PAGE.encode(); self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers(); self.wfile.write(body)
        elif self.path=='/health':
            try:
                with urlopen(BASE_URL+'/api/tags',timeout=5) as r: models=json.load(r)['models']
                self.send_json(200,{'status':'ready','ollama_url':BASE_URL,'models':[m['name'] for m in models]})
            except Exception as exc:self.send_json(503,{'status':'unavailable','error':str(exc)})
        elif self.path.rstrip('/')=='/v1/models':
            self.send_json(200,{'object':'list','data':[{'id':key,'object':'model','owned_by':'local'} for key in ['qwen','llama']]})
        else:self.send_json(404,{'error':'Not found'})

    def do_POST(self):
        if self.path not in ['/chat','/v1/chat/completions']:
            return self.send_json(404,{'error':'Not found'})
        try:
            size=int(self.headers.get('Content-Length',0))
            if not 0<size<=80000:raise ValueError('Request must be 1-80000 bytes')
            data=json.loads(self.rfile.read(size)); model=data.get('model','')
            prompt=data.get('prompt','')
            if self.path=='/v1/chat/completions':
                users=[m for m in data.get('messages',[]) if m.get('role')=='user']
                if not users:raise ValueError('No user message')
                prompt=users[-1]['content']
                if isinstance(prompt,list):prompt='\n'.join(p.get('text','') for p in prompt if p.get('type')=='text')
            if not isinstance(prompt,str):raise ValueError('Prompt must be text')
            result=run_request(model,prompt)
            if self.path=='/chat':return self.send_json(200,result)
            common={'id':'chatcmpl-'+uuid.uuid4().hex,'created':int(time.time()),'model':result['model']}
            if not data.get('stream'):
                return self.send_json(200,dict(common,object='chat.completion',choices=[{'index':0,'message':{'role':'assistant','content':result['response']},'finish_reason':'stop'}]))
            self.send_response(200); self.send_header('Content-Type','text/event-stream'); self.end_headers()
            for delta,finish in [({'role':'assistant','content':result['response']},None),({},'stop')]:
                event=dict(common,object='chat.completion.chunk',choices=[{'index':0,'delta':delta,'finish_reason':finish}])
                self.wfile.write(('data: '+json.dumps(event,ensure_ascii=False)+'\n\n').encode())
            self.wfile.write(b'data: [DONE]\n\n'); self.wfile.flush()
        except (BrokenPipeError,ConnectionResetError):pass
        except (ValueError,KeyError) as exc:self.send_json(400,{'error':{'message':str(exc)}})
        except Exception as exc:self.send_json(500,{'error':{'message':str(exc)}})

if __name__=='__main__':
    print('Local CrewAI web/API listening on :8080',flush=True)
    ThreadingHTTPServer(('0.0.0.0',8080),Handler).serve_forever()
