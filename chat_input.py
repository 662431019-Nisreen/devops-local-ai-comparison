"""Single-model chat with explicit local calculator/clock and session history."""
import argparse
import ast
from datetime import datetime
import json
import operator
import re
import shutil
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
from crewai_helper import answer, choose_model, BASE_URL, ROOT

BASE_INSTRUCTION = ('Answer the latest user message directly and briefly. '
    'Use Thai for Thai messages. Respect preferences stated in this conversation. '
    'Do not merely repeat the question. Do not invent facts. '
    'Only answer the latest message; earlier messages are context, not questions to repeat.')


def local_result(text):
    expression = text.strip().rstrip('=? ').strip()
    if len(expression) <= 100 and re.fullmatch(r'[\d\s.+*/()\-]+', expression or 'x') and re.search(r'\d',expression):
        operations={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
        def calculate(node):
            if isinstance(node,ast.Constant) and type(node.value) in (int,float):
                if abs(node.value)>10**12: raise ValueError('Number too large')
                return node.value
            if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
                v=calculate(node.operand)
                return -v if isinstance(node.op,ast.USub) else v
            if isinstance(node,ast.BinOp) and type(node.op) in operations:
                v=operations[type(node.op)](calculate(node.left),calculate(node.right))
                if abs(v)>10**15:raise ValueError('Result too large')
                return v
            raise ValueError('Unsupported expression')
        try:
            value=calculate(ast.parse(expression,mode='eval').body)
            if isinstance(value,float) and value.is_integer():value=int(value)
            return 'เครื่องคิดเลขในโปรแกรม',str(value)
        except ZeroDivisionError:
            return 'เครื่องคิดเลขในโปรแกรม','หารด้วยศูนย์ไม่ได้'
        except (ValueError,SyntaxError,OverflowError,RecursionError):
            return 'เครื่องคิดเลขในโปรแกรม','นิพจน์ไม่ถูกต้องหรือเกินขอบเขตที่รองรับ'
    if any(word in text for word in ('เวลาเท่าไหร่','กี่โมง','เวลาปัจจุบัน')) or re.search(r'\b(?:current time|what time is it)\b',text,re.I):
        now=datetime.now(ZoneInfo('Asia/Bangkok'))
        return 'นาฬิกาเครื่อง',now.strftime('%H:%M:%S น. วันที่ %d/%m/%Y (Asia/Bangkok)')
    return None


def reply(text,model,engine='crewai',history=None):
    local=local_result(text)
    if local:return f'[{local[0]}] {local[1]}'
    free=shutil.disk_usage(ROOT).free/1024**3
    if free<3:raise RuntimeError(f'Only {free:.2f} GiB free; at least 3 GiB required.')
    history=(history or [])[-6:]
    instruction=BASE_INSTRUCTION
    if any('อิสลาม' in m['content'] or 'มุสลิม' in m['content'] or 'muslim' in m['content'].lower() for m in history+[{'content':text}]):
        instruction+=' The user has stated they are Muslim. For food requests, avoid pork and alcohol, suggest halal ingredients and say to check halal preparation. Never assert a restaurant is halal without evidence.'
    if engine=='crewai':
        context=json.dumps(history,ensure_ascii=False)
        result=answer(text,instruction+'\nEarlier messages (context only):\n'+context,model=model,max_tokens=250)
    else:
        request=Request(BASE_URL+'/api/chat',data=json.dumps({
            'model':model,'messages':[{'role':'system','content':instruction}]+history+[{'role':'user','content':text}],
            'stream':False,'keep_alive':0,'options':{'temperature':0,'num_ctx':4096,'num_predict':250}
        }).encode(),headers={'Content-Type':'application/json'})
        with urlopen(request,timeout=300) as response:data=json.load(response)
        if 'error' in data:raise RuntimeError(data['error'])
        result=data['message']['content']
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',choices=['qwen','llama'])
    parser.add_argument('--engine',choices=['crewai','direct'],default='crewai')
    args=parser.parse_args()
    selected=choose_model(args.model)
    print(f'Model: {selected}; engine: {args.engine}; ONE model only.')
    print('Session history: last 6 messages. /clear resets it. /bye exits.')
    print('Arithmetic and time use labeled local program tools, not model answers.')
    history=[]
    while True:
        try:
            text=input('You: ').strip()
            if text.lower() in ('/bye','quit','exit'):break
            if text=='/clear':history=[];print('History cleared.');continue
            if not text:continue
            if len(text)>4000:print('Limit: 4,000 characters.');continue
            result=reply(text,selected,args.engine,history)
            print('Assistant:',result)
            history.extend([{'role':'user','content':text},{'role':'assistant','content':result}])
            history=history[-6:]
        except (EOFError,KeyboardInterrupt):break
        except Exception as exc:print(f'Error: {exc}')

if __name__=='__main__':main()
