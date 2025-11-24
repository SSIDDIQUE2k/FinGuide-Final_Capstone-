#!/usr/bin/env python3
"""
Simple diagnostic script to probe common Ollama HTTP endpoints and verify a model responds.
Usage:
  source .venv/bin/activate
  python scripts/check_ollama.py --base http://localhost:11434 --model llama3.1

This script posts a small prompt to several likely endpoints and prints the results.
"""
import argparse
import requests

ENDPOINTS = [
    '/api/generate',
    '/v1/generate',
    '/api/v1/generate',
    '/generate',
]

def check(base, model, prompt='Hello'):
    base = base.rstrip('/')
    payload = {'model': model, 'prompt': prompt}

    for ep in ENDPOINTS:
        url = f"{base}{ep}"
        try:
            print(f'Trying {url} ...', end=' ')
            resp = requests.post(url, json=payload, timeout=8)
            print(f'status={resp.status_code}')
            try:
                print('response body:', resp.json())
            except Exception:
                print('response text:', resp.text[:400])
            if 200 <= resp.status_code < 300:
                print('\nSUCCESS at', url)
                return 0
        except Exception as e:
            print('error:', str(e))
    print('\nAll endpoints failed. Check that `ollama serve` is running and the model is loaded.')
    return 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='http://localhost:11434', help='Ollama base URL')
    parser.add_argument('--model', default='llama3.1', help='Model name to request')
    args = parser.parse_args()
    raise SystemExit(check(args.base, args.model))
