"""Usage: python3 caption_image.py diagram.png"""
import os
import base64
import json
import mimetypes
import pathlib
import sys
import urllib.request

image = pathlib.Path(sys.argv[1])
mime = mimetypes.guess_type(image.name)[0] or 'image/png'
payload = {
    'model': 'qwen3.8:27b',
    'messages': [{'role': 'user', 'content': [
        {'type': 'text', 'text': 'Bu ders görselini Türkçe 1-3 cümleyle açıkla. Etiketleri ve temel ilişkiyi belirt. Okunamayan bilgileri uydurma.'},
        {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,' + base64.b64encode(image.read_bytes()).decode()}},
    ]}],
    'max_tokens': 300,
    'chat_template_kwargs': {'enable_thinking': False},
}
request = urllib.request.Request(
    os.environ.get('OPENAI_BASE_URL', 'http://127.0.0.1:11445/v1').rstrip('/') + '/chat/completions',
    data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'},
)
with urllib.request.urlopen(request, timeout=180) as response:
    print(json.load(response)['choices'][0]['message']['content'])
