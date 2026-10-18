"""Generate one HTML page with one selected model."""
import argparse
from pathlib import Path
import re
from crewai_helper import answer, choose_model, MODELS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['qwen','llama'])
    args = parser.parse_args()
    model = choose_model(args.model)
    key = next(k for k,v in MODELS.items() if v==model)
    prompt = input('Describe the web page (Enter for default): ').strip() or 'Create a complete HTML page showing "My DevOps Project" in a centered white card on a light blue background.'
    result = answer(prompt, 'Return one complete HTML document with embedded CSS and JavaScript when needed. No external resources. Return only code.', model=model, max_tokens=3000)
    folder = Path(__file__).resolve().parent / 'result' / key
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'html-response.txt').write_text(result,encoding='utf-8')
    match = re.search(r'(?:<!doctype html>\s*)?<html\b.*?</html\s*>',result,re.S|re.I)
    if not match:
        raise RuntimeError(f'Incomplete HTML. Original saved to {folder / "html-response.txt"}')
    target = folder/'index.html'
    target.write_text(match.group(),encoding='utf-8')
    print(f'Model: {model}\nSaved: {target}')

if __name__=='__main__': main()
