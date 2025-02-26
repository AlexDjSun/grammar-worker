import unittest
import requests
import json

class TestLlamaGEC(unittest.TestCase):
    def setUp(self):
        self.url_correction = "https://mgc.hpc.ut.ee/v1/completions"
        self.url_m2 = "http://artemis20.hpc.ut.ee:8000/v1/completions"
        self.url_explanation = "http://artemis20.hpc.ut.ee:8001/v1/completions"
        self.auth = ('mgc', 'MGCpass')
        self.sample_text = "Loodan, et meil kõik kätte sai."

    def test_correction_api(self):
        data = {
            "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-mix-paragraph-GEC",
            "prompt": f"### Instruction:\nReply with a corrected version of the input essay in Estonian with all grammatical and spelling errors fixed. If there are no errors, reply with a copy of the original essay.\n\n### Input:\n{self.sample_text}\n\n### Response:\n",
            "max_tokens": 1000,
            "temperature": 1
        }
        response = requests.post(self.url_correction, auth=self.auth, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertIn("choices", response.json())

    def test_m2_generation_api(self):
        corrected_text = "Loodan, et meile kõik kätte jõuab."
        data = {
            "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-pseudo-m2",
            "prompt": f"### Instruction:\nSa võrdled kahte eestikeelset lauset: keeleõppija kirjutatud algne lause ja parandatud lause. Genereeri vea kaupa paranduste loend.\n\n### Input:\nAlgne tekst: {self.sample_text}\n\nParandatud tekst: {corrected_text}\n\n### Response:\n",
            "max_tokens": 200,
            "temperature": 0.8
        }
        response = requests.post(self.url_m2, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertIn("choices", response.json())

    def test_explanation_api(self):
        corrected_text = "Loodan, et meile kõik kätte jõuab."
        correction_details = "1. käändevorm: meil -> meile\n2. sõnavalik: sai -> jõuab"
        specific_correction = "Selgitus 1: meil -> meile"
        data = {
            "model": "tartuNLP/Llammas-base-p1-GPT-4o-human-error-explain-from-pseudo-m2",
            "prompt": f"### Instruction:\nSa võrdled kahte eestikeelset lauset: keeleõppija kirjutatud algne lause ja parandatud lause. Selgita ühte parandust.\n\n### Input:\nAlgne lause: {self.sample_text}\n\nParandatud lause: {corrected_text}\n\nParandused:\n{correction_details}\n\n{specific_correction}\n\n### Response:\n",
            "max_tokens": 400,
            "temperature": 0.9
        }
        response = requests.post(self.url_explanation, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertIn("choices", response.json())

if __name__ == "__main__":
    unittest.main()
