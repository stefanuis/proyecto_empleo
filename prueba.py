import requests


url = "http://10.10.10.50:11434/api/generate"


datos = {

"model": "qwen3:14b",

"prompt": "¿que es un  agujero negro?",

"stream": False

}


respuesta = requests.post(url, json=datos)


print(respuesta.json()["response"])