import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ["api_key"],
    base_url=os.environ["base_url"],
)

vastaus = client.chat.completions.create(
    model=os.environ["deployment_name"],
    messages=[
        {"role": "system", "content": "Vastaa kuin rakennuttajakonsultti"},
        {"role": "user", "content": "Mikä on RAG ja miksi yritykset käyttävät sitä?"},
    ],
)

print(vastaus.choices[0].message.content)