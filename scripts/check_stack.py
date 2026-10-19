"""Record real container/API checks. Does not claim host internet disconnection."""
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

BASE='http://127.0.0.1:8080'
ROOT=Path(__file__).resolve().parents[1]

def main():
    with urlopen(BASE+'/health',timeout=10) as response:health=json.load(response)
    prompt='Write a complete small HTML document displaying "Local agent test NISREEN-01". Return only HTML.'
    records=[]
    for model in ['qwen','llama']:
        start=time.perf_counter()
        req=Request(BASE+'/chat',data=json.dumps({'model':model,'prompt':prompt}).encode(),headers={'Content-Type':'application/json'})
        with urlopen(req,timeout=700) as response:data=json.load(response)
        assert data['engine']=='crewai' and data['agent_count']==1 and data['task_count']==1
        records.append({'requested_model':model,'prompt':prompt,'wall_seconds':round(time.perf_counter()-start,2),'result':data})
        print(model, data['model'], data['seconds'], flush=True)
        target=ROOT/'evidence'/'container-agent-test.json'
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps({'health':health,'host_disconnected':False,'tests':records},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
