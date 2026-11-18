import os, json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ["api_key"],
    base_url=os.environ["base_url"],
)

# Synteettinen referenssidata (myöhemmin tämä tulee vektorikannasta)
HANKKEET = [
    {"hanke": "Ajoksen silta", "tyyppi": "silta", "alue": "Lappi", "vuosi": 2023, "rooli": "rakennuttaja"},
    {"hanke": "Vt 4 Kempele", "tyyppi": "tie", "alue": "Pohjois-Pohjanmaa", "vuosi": 2021, "rooli": "valvoja"},
    {"hanke": "Oulujoen ratasilta", "tyyppi": "silta", "alue": "Pohjois-Pohjanmaa", "vuosi": 2024, "rooli": "projektinjohto"},
    {"hanke": "Tornion koulukeskus", "tyyppi": "rakennus", "alue": "Lappi", "vuosi": 2022, "rooli": "rakennuttaja"},
    {"hanke": "Raahen tehdaslaajennus", "tyyppi": "teollisuus", "alue": "Pohjois-Pohjanmaa", "vuosi": 2020, "rooli": "valvoja"},
]

def hae_referenssit(tyyppi=None, alue=None, min_vuosi=None):
    tulos = HANKKEET
    if tyyppi:    tulos = [h for h in tulos if h["tyyppi"] == tyyppi]
    if alue:      tulos = [h for h in tulos if h["alue"] == alue]
    if min_vuosi: tulos = [h for h in tulos if h["vuosi"] >= min_vuosi]
    return tulos

TYOKALUT = [{
    "type": "function",
    "function": {
        "name": "hae_referenssit",
        "description": "Hakee Weladon aiempia hankkeita referensseiksi suodattimien perusteella.",
        "parameters": {
            "type": "object",
            "properties": {
                "tyyppi": {"type": "string", "enum": ["silta", "tie", "rata", "rakennus", "teollisuus"]},
                "alue": {"type": "string", "description": "Maakunta, esim. Lappi tai Pohjois-Pohjanmaa"},
                "min_vuosi": {"type": "integer"},
            },
        },
    },
}]

viestit = [
    {"role": "system", "content": "Olet tarjoustiimin apuri. Käytä hakutyökalua, älä keksi hankkeita."},
    {"role": "user", "content": "Tarvitsen tarjoukseen tehdasreferenssejä Pohjois-Suomesta viimeisen 10 vuoden ajalta."},
]

# Agenttisilmukka: jatketaan, kunnes malli ei enää halua kutsua työkaluja
while True:
    vastaus = client.chat.completions.create(model="gpt-5-mini", messages=viestit, tools=TYOKALUT)
    viesti = vastaus.choices[0].message
    viestit.append(viesti)

    if not viesti.tool_calls:
        print(viesti.content)
        break

    for kutsu in viesti.tool_calls:
        args = json.loads(kutsu.function.arguments)
        print(f"[malli kutsuu: {kutsu.function.name}({args})]")
        tulos = hae_referenssit(**args)
        viestit.append({"role": "tool", "tool_call_id": kutsu.id, "content": json.dumps(tulos, ensure_ascii=False)})