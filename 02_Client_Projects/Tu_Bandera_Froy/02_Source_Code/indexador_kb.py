#!/usr/bin/env python3
import os, glob, hashlib, requests
OLLAMA='http://127.0.0.1:11434/api/embed'
QDRANT='http://127.0.0.1:6333'
KB='/opt/hermes/tubandera/kb'
COLLECTION='tubandera_kb'

def embed(text):
    r=requests.post(OLLAMA, json={'model':'nomic-embed-text','input':text}, timeout=30)
    return r.json()['embeddings'][0]

# crear/recrear coleccion limpia
requests.delete(f'{QDRANT}/collections/{COLLECTION}', timeout=10)
r=requests.put(f'{QDRANT}/collections/{COLLECTION}', json={'vectors':{'size':768,'distance':'Cosine'}}, timeout=10)
print('coleccion creada:', r.status_code)

docs=[]
for path in glob.glob(f'{KB}/**/*.md', recursive=True):
    txt=open(path).read()
    for block in txt.split('\n## '):
        if block.strip():
            docs.append({'text':block.strip(),'src':os.path.relpath(path,KB)})
print('chunks:', len(docs))

points=[]
for d in docs:
    vec=embed(d['text'])
    # id numerico de 64 bits desde el hash del texto
    hid=int(hashlib.md5(d['text'].encode()).hexdigest()[:15],16)
    points.append({'id':hid,'vector':vec,'payload':{'text':d['text'],'src':d['src']}})

ok=0
for i in range(0,len(points),20):
    batch=points[i:i+20]
    r=requests.put(f'{QDRANT}/collections/{COLLECTION}/points', json={'points':batch}, timeout=30)
    if r.status_code in (200,202): ok+=len(batch)
print('indexados OK:', ok)

# prueba de busqueda semantica
def search(q, limit=3):
    qv=embed(q)
    r=requests.post(f'{QDRANT}/collections/{COLLECTION}/points/search', json={'vector':qv,'limit':limit,'with_payload':True}, timeout=20)
    return r.json().get('result',[])

print('--- BUSQUEDA: fentanilo ---')
for h in search('que es el fentanilo'): print(' *', h['payload']['text'][:60])

