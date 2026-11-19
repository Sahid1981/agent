"""Mobile-friendly web UI for ask.py.

Run locally:  streamlit run app.py
"""
import streamlit as st

from ai import CHAT_MODEL, client, pro
from ask import INSTRUCTIONS, search

st.set_page_config(page_title="Kysy", page_icon="📚")
st.title("📚 Kysy kokoelmasta")

names = sorted(getattr(c, "name", c) for c in pro.list_collections())
if not names:
    st.warning("Ei kokoelmia. Lisää ensin dokumentteja add.py:llä.")
    st.stop()

name = st.selectbox("Kokoelma", names)

with st.form("ask"):
    question = st.text_area("Kysymys", height=100)
    submitted = st.form_submit_button("Kysy", use_container_width=True)

if submitted and question.strip():
    with st.spinner("Haetaan..."):
        matches = search(name, question.strip())

    if not matches:
        st.info("Lähteistä ei löytynyt riittävän läheisiä kohtia.")
        st.stop()

    context = "\n\n".join(f"[{m['source']}, p. {m['page']}]\n{m['text']}" for m in matches)
    with st.spinner("Vastataan..."):
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": INSTRUCTIONS},
                {"role": "user", "content": f"Source excerpts:\n{context}\n\nQuestion: {question}"},
            ],
        )
    st.markdown(response.choices[0].message.content)

    with st.expander("Löydetyt kohdat"):
        for m in matches:
            st.caption(f"{m['distance']:.3f} · {m['source']}, s. {m['page']}")
            st.text(m["text"][:500])
