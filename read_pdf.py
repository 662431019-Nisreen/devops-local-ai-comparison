"""PDF Q&A using one selected model."""
import argparse
from pathlib import Path
from crewai_helper import choose_model, pdf_answer, MODELS

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('pdf',type=Path)
    parser.add_argument('--model',choices=['qwen','llama'])
    parser.add_argument('--start',type=int,default=1)
    parser.add_argument('--pages',type=int,default=3)
    parser.add_argument('--question',default='สรุปเนื้อหาเป็นภาษาไทย')
    args=parser.parse_args()
    model=choose_model(args.model)
    result=pdf_answer(args.pdf,args.question,model,args.start,args.pages)
    key=next(k for k,v in MODELS.items() if v==model)
    folder=Path(__file__).resolve().parent/'pdf-results'/key
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/f'{args.pdf.stem}-pages-{args.start}-{args.pages}.md'
    target.write_text(result,encoding='utf-8')
    print(result)
    print(f'Saved: {target}')

if __name__=='__main__': main()
