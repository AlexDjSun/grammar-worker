import requests
import json

def correct_text(input_text):
    url = "https://mgc.hpc.ut.ee/v1/completions"
    auth = ('mgc', 'MGCpass')
    data = {
        "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-mix-paragraph-GEC",
        "prompt": f"### Instruction:\nReply with a corrected version of the input essay in Estonian with all grammatical and spelling errors fixed. If there are no errors, reply with a copy of the original essay.\n\n### Input:\n{input_text}\n\n### Response:\n",
        "max_tokens": 1000,
        "temperature": 0.5
    }
    response = requests.post(url, auth=auth, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    return response.json()["choices"][0]["text"].strip() if response.status_code == 200 else None

def generate_correction_log(original, corrected):
    url = "http://artemis20.hpc.ut.ee:8000/v1/completions"
    data = {
        "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-pseudo-m2",
        "prompt": f"### Instruction:\nSa võrdled kahte eestikeelset lauset: keeleõppija kirjutatud algne lause ja parandatud lause. Genereeri vea kaupa paranduste loend.\n\n### Input:\nAlgne tekst: {original}\n\nParandatud tekst: {corrected}\n\n### Response:\n",
        "max_tokens": 200,
        "temperature": 0.8
    }
    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    return response.json()["choices"][0]["text"].strip() if response.status_code == 200 else None

def explain_correction(original, corrected, correction_details, specific_correction):
    url = "http://artemis20.hpc.ut.ee:8001/v1/completions"
    data = {
        "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-explain-from-pseudo-m2",
        "prompt": f"### Instruction:\nSa võrdled kahte eestikeelset lauset: keeleõppija kirjutatud algne lause ja parandatud lause. Selgita ühte parandust.\n\n### Input:\nAlgne lause: {original}\n\nParandatud lause: {corrected}\n\nParandused:\n{correction_details}\n\n{specific_correction}\n\n### Response:\n1. Pikem selgitus (keeleline põhjendus, miks parandust vaja on).\n2. Lühike selgitus (lihtsustatud, et keeleõppija saaks paremini aru).\n3. Vealiik (nt. käändevorm, tegusõna vorm, õigekiri).",
        "max_tokens": 400,
        "temperature": 0.9
    }
    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    return response.json()["choices"][0]["text"].strip() if response.status_code == 200 else None

if __name__ == "__main__":
    sample_sentence = "Loodan, et meil kõik kätte sai."
    corrected_text = correct_text(sample_sentence)
    
    if corrected_text:
        print(f"Original: {sample_sentence}")
        print(f"Corrected: {corrected_text}")
        
        correction_log = generate_correction_log(sample_sentence, corrected_text)
        print(f"\nCorrections:\n{correction_log}")
        
        if correction_log:
            first_correction = correction_log.split("\n")[0]
            explanation = explain_correction(sample_sentence, corrected_text, correction_log, first_correction)
            print(f"\nExplanation for first correction:\n{explanation}")