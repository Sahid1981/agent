import os, json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ["api_key"],
    base_url=os.environ["base_url"],
)

kuvaus = """aikonsulttina toimiessamme Kemin Ajoksen sillan peruskorjauksessa
ajalla 11 2025- 12 2026. tämä maksoi noin 4,2 milj. euroa. jäseninä
toimi Maija Virtanen ja valvojana Pekka Korhonen. myös it tukena juha jermalainen"""

skeema = {
    "type": "object",
    "properties": {
        "hanke": {"type": "string"},
        "hanketyyppi": {"type": "string", "enum": ["silta", "tie", "rata", "rakennus", "teollisuus", "muu"]},
        "paikkakunta": {"type": "string"},
        "alkuvuosi": {"type": "integer"},
        "loppuvuosi": {"type": "integer"},
        "arvo_milj_eur": {"type": ["number", "null"]},
        "weladon_rooli": {"type": "string"},
        "henkilot": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["hanke", "hanketyyppi", "paikkakunta", "alkuvuosi",
                 "loppuvuosi", "arvo_milj_eur", "weladon_rooli", "henkilot"],
    "additionalProperties": False,
}

vastaus = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "Poimi hankekuvauksesta tiedot. Jos tietoa ei ole, käytä null."},
        {"role": "user", "content": kuvaus},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "hanke", "schema": skeema, "strict": True},
    },
)

data = json.loads(vastaus.choices[0].message.content)
print(json.dumps(data, ensure_ascii=False, indent=2))