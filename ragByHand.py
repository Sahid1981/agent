import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ["api_key"],
    base_url=os.environ["base_url"],
)

DOKUMENTIT = [
    "Ajoksen silta, Kemi 2023: rakennuttajakonsultointi sillan peruskorjauksessa, arvo 4,2 M€. Haasteena talvityöt ja meriolosuhteet.",
    "Vt 4 Kempele 2021: työmaavalvonta tien parannushankkeessa, liikenne pidettiin auki koko rakentamisen ajan.",
    "Oulujoen ratasilta 2024: projektinjohto uuden ratasillan rakentamisessa, junaliikenteen katkot ajoitettiin yöhön.",
    "Tornion koulukeskus 2022: rakennuttaminen, uusi koulukeskus 800 oppilaalle, puurakenteinen.",
    "Raahen tehdaslaajennus 2020: valvonta teollisuushallin laajennuksessa, tiukka aikataulu tuotantokatkon takia.",
]

def upota(tekstit):
    vastaus = client.embeddings.create(model="text-embedding-3-small", input=tekstit)
    return np.array([d.embedding for d in vastaus.data])

def hae(kysymys, vektorit, k=2):
    q = upota([kysymys])[0]
    # Kosinisamankaltaisuus: kuinka samaan suuntaan vektorit osoittavat
    samankaltaisuus = vektorit @ q / (np.linalg.norm(vektorit, axis=1) * np.linalg.norm(q))
    parhaat = np.argsort(samankaltaisuus)[::-1][:k]
    return [(DOKUMENTIT[i], round(float(samankaltaisuus[i]), 3)) for i in parhaat]

vektorit = upota(DOKUMENTIT)   # tehdään kerran, oikeassa sovelluksessa tallennetaan
print(f"Vektorin pituus: {vektorit.shape[1]} lukua per dokumentti\n")

kysymys = "Onko meillä kokemusta hankkeista, joissa liikenne piti pitää käynnissä työn aikana?"
osumat = hae(kysymys, vektorit)
for teksti, pisteet in osumat:
    print(f"{pisteet}  {teksti}")

# Generointi: annetaan haetut dokumentit mallille kontekstiksi
konteksti = "\n".join(t for t, _ in osumat)
vastaus = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "Vastaa vain annettujen dokumenttien perusteella ja mainitse hanke, josta tieto on. Jos vastausta ei löydy, sano se."},
        {"role": "user", "content": f"Dokumentit:\n{konteksti}\n\nKysymys: {kysymys}"},
    ],
)
print("\n" + vastaus.choices[0].message.content)