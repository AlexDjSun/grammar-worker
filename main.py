from contextlib import asynccontextmanager
import threading
import json
import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from gec_worker import MQConsumer

# LLaMA-based correction API endpoints
GEC_URL = "https://mgc.hpc.ut.ee/v1/completions"
M2_URL = "http://artemis20.hpc.ut.ee:8000/v1/completions"
EXPLANATION_URL = "http://artemis20.hpc.ut.ee:8001/v1/completions"
AUTH = ('mgc', 'MGCpass')

def correct_text(input_text: str) -> str:
    data = {
        "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-mix-paragraph-GEC",
        "prompt": f"### Instruction:\nReply with a corrected version of the input essay in Estonian with all grammatical and spelling errors fixed. If there are no errors, reply with a copy of the original essay.\n\n### Input:\n{input_text}\n\n### Response:\n",
        "max_tokens": 1000,
        "temperature": 0.5
    }
    response = requests.post(GEC_URL, auth=AUTH, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    raise HTTPException(status_code=response.status_code, detail="Error in GEC API")

def generate_correction_log(original: str, corrected: str) -> str:
    data = {
        "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-pseudo-m2",
        "prompt": f"### Instruction:\nSa võrdled kahte eestikeelset lauset: keeleõppija kirjutatud algne lause ja parandatud lause. Genereeri vea kaupa paranduste loend.\n\n### Input:\nAlgne tekst: {original}\n\nParandatud tekst: {corrected}\n\n### Response:\n",
        "max_tokens": 200,
        "temperature": 0.8
    }
    response = requests.post(M2_URL, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    raise HTTPException(status_code=response.status_code, detail="Error in M2 API")

def explain_correction(original: str, corrected: str, correction_details: str, specific_correction: str) -> str:
    data = {
        "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-explain-from-pseudo-m2",
        "prompt": f"### Instruction:\nSa võrdled kahte eestikeelset lauset: keeleõppija kirjutatud algne lause ja parandatud lause. Selgita ühte parandust.\n\n### Input:\nAlgne lause: {original}\n\nParandatud lause: {corrected}\n\nParandused:\n{correction_details}\n\n{specific_correction}\n\n### Response:\n1. Pikem selgitus (keeleline põhjendus, miks parandust vaja on).\n2. Lühike selgitus (lihtsustatud, et keeleõppija saaks paremini aru).\n3. Vealiik (nt. käändevorm, tegusõna vorm, õigekiri).",
        "max_tokens": 400,
        "temperature": 0.9
    }
    response = requests.post(EXPLANATION_URL, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    raise HTTPException(status_code=response.status_code, detail="Error in Explanation API")


def process_request(request_text: str):
    corrected_text = correct_text(request_text)
    correction_log = generate_correction_log(request_text, corrected_text)
    explanation = explain_correction(request_text, corrected_text, correction_log, correction_log.split("\n")[0])
    
    response = {
        "original": request_text,
        "corrected": corrected_text,
        "corrections": correction_log,
        "explanation": explanation
    }
    
    return json.dumps(response)

class Worker:
    def __init__(self):
        self.consumer = MQConsumer(corrector=self)
    
    def process_request(self, request):
        # print("received:", request.text)  # Debugging
        response = process_request(request.text)
        # print("processed:", response)  # Debugging
        return response
    
    def start(self):
        self.consumer.start()

worker = Worker()
mq_thread = threading.Thread(target=worker.start, daemon=True)
mq_thread.start()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health/liveness")
def liveness():
    return "OK"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)