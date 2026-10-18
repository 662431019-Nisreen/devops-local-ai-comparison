"""Independent translation, with explicit direct/CrewAI engines."""
import argparse
import json
from pathlib import Path
import shutil
import time
from urllib.request import Request, urlopen
from crewai_helper import choose_model, BASE_URL, ROOT, unload


def target_for(text, target='auto'):
    if target != 'auto': return {'th':'Thai','en':'English'}[target]
    return 'English' if any('\u0e00' <= c <= '\u0e7f' for c in text) else 'Thai'


def translate(text, model, engine, target='auto'):
    free=shutil.disk_usage(ROOT).free/1024**3
    if free<3:
        raise RuntimeError(f'Only {free:.2f} GiB free; at least 3 GiB required.')
    language=target_for(text,target)
    instruction=(f'Translate the supplied source text into {language}. '
        'Preserve meaning, speaker, tense, and whether it is a question. '
        'Translate questions; do NOT answer them. Return only the translated text. '
        'Do not include instructions, explanations, labels, or greetings absent from the source.')
    if engine=='direct':
        req=Request(BASE_URL+'/api/chat',data=json.dumps({
            'model':model,'messages':[{'role':'system','content':instruction},
                {'role':'user','content':text}],
            'stream':False,'keep_alive':0,
            'options':{'temperature':0,'num_ctx':2048,'num_predict':400}
        }).encode(),headers={'Content-Type':'application/json'})
        with urlopen(req,timeout=300) as response:data=json.load(response)
        if 'error' in data:raise RuntimeError(data['error'])
        return data['message']['content']
    from crewai import Agent,Task,Crew,LLM
    llm=LLM(model=f'ollama/{model}',base_url=BASE_URL,temperature=0,max_tokens=400,timeout=300)
    agent=Agent(role='Translator',goal=f'Translate source text into {language}.',
        backstory='You translate text, including questions, without answering it. You preserve meaning and pronouns.',
        llm=llm,allow_delegation=False,max_iter=2,verbose=False)
    task=Task(description=instruction+'\n<source_text>\n'+text+'\n</source_text>',
        expected_output=f'Only the {language} translation of the source text.',agent=agent)
    try:
        return Crew(agents=[agent],tasks=[task],memory=False,verbose=False).kickoff().raw
    finally:
        try:unload(model)
        except Exception:pass


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',choices=['qwen','llama'])
    parser.add_argument('--engine',choices=['crewai','direct'],default='crewai')
    parser.add_argument('--to',choices=['auto','th','en'],default='auto')
    args=parser.parse_args()
    model=choose_model(args.model)
    print(f'Translation | model={model} | engine={args.engine} | target={args.to}')
    print('ONE model only. /end submits; /bye exits. Questions are translated, not answered.')
    while True:
        try:
            lines=[]
            while True:
                line=input('> ')
                if line.strip()=='/bye':return
                # Also accept /end pasted at the end of a sentence.
                if line.rstrip().endswith('/end'):
                    prefix=line.rstrip()[:-4].rstrip()
                    if prefix:lines.append(prefix)
                    break
                lines.append(line)
            text='\n'.join(lines).strip()
            if not text:continue
            if len(text)>4000:
                print('Limit: 4,000 characters.');continue
            print(f'Working: {model}; engine={args.engine}; target={target_for(text,args.to)}',flush=True)
            start=time.perf_counter()
            result=translate(text,model,args.engine,args.to)
            print('\n'+result+'\n')
            folder=Path(__file__).resolve().parent/'translation-results'
            folder.mkdir(exist_ok=True)
            with (folder/'translations.jsonl').open('a',encoding='utf-8') as file:
                file.write(json.dumps({'model':model,'engine':args.engine,'source':text,
                    'target':target_for(text,args.to),'translation':result,
                    'seconds':round(time.perf_counter()-start,2)},ensure_ascii=False)+'\n')
        except (EOFError,KeyboardInterrupt):return
        except Exception as exc:print(f'Error: {exc}')

if __name__=='__main__':main()
