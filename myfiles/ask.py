"""Query a collection and answer with source citations.

Usage:
    python ask.py <collection_name>            (interactive, stop with an empty line)
    python ask.py <collection_name> "question" (single question)
"""
import sys

from ai import CHAT_MODEL, client, collection, embed

RESULT_COUNT = 5
MAX_DISTANCE = 0.65

INSTRUCTIONS = (
    "Answer only from the provided source excerpts. "
    "Cite each claim using [file, p. X]. "
    "If the sources do not contain the answer, say so directly and do not guess."
)


def search(name, question):
    result = collection(name).query(query_embeddings=embed([question]), n_results=RESULT_COUNT)
    matches = []
    for text, metadata, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        if distance <= MAX_DISTANCE:
            matches.append(
                {"text": text, "source": metadata["source"], "page": metadata["page"], "distance": distance}
            )
    return matches


def answer(name, question):
    matches = search(name, question)

    print("\nRetrieved chunks:")
    for match in matches:
        print(f"  {match['distance']:.3f}  {match['source']}, p. {match['page']}")
    if not matches:
        print("  (no sufficiently close matches)")
        return

    context = "\n\n".join(
        f"[{match['source']}, p. {match['page']}]\n{match['text']}" for match in matches
    )
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": f"Source excerpts:\n{context}\n\nQuestion: {question}"},
        ],
    )
    print("\n" + response.choices[0].message.content + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    if len(sys.argv) > 2:
        answer(name, sys.argv[2])
    else:
        while (question := input("Question: ").strip()):
            answer(name, question)