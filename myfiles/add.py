"""Read folder's documents, chops them to smaller pieces and adds them to collection.

usage:
    python add.py <folder> <COLLECTION_NAME>
    python add.py .\sources thesis

supported files: .pdf, .md, .txt
Running again updates same files, dosent add duplicates.
"""
import sys
from pathlib import Path

from pypdf import PdfReader

from ai import collection, embed

PIECE_SIZE = 1000
OVERLAP = 200

def lue_sivut(polku):
    """Return a list of (page number, text) pairs."""
    if polku.suffix.lower() == ".pdf":
        lukija = PdfReader(polku)
        return [(i + 1, sivu.extract_text() or "") for i, sivu in enumerate(lukija.pages)]
    return [(1, polku.read_text(encoding="utf-8", errors="ignore"))]


def pilko(teksti):
    text = " ".join(teksti.split())
    chunks = []
    start = 0
    step = PIECE_SIZE - OVERLAP
    while start < len(text):
        chunks.append(text[start:start + PIECE_SIZE])
        start += step
    return [chunk for chunk in chunks if len(chunk) > 50]


def main(folder, name):
    files = [p for p in Path(folder).rglob("*") if p.suffix.lower() in {".pdf", ".md", ".txt"}]
    if not files:
        print(f"No .pdf, .md, or .txt files found in {folder}.")
        return

    ids, texts, metadata = [], [], []
    for file in files:
        for page, text in lue_sivut(file):
            for index, chunk in enumerate(pilko(text)):
                ids.append(f"{file.relative_to(folder)}:p{page}:c{index}")
                texts.append(chunk)
                metadata.append({"source": file.name, "page": page})
        print(f"  read {file.name}")

    print(f"Embedding {len(texts)} chunks...")
    vectors = embed(texts)
    collection(name).upsert(ids=ids, documents=texts, embeddings=vectors, metadatas=metadata)
    print(f"Done: {len(texts)} chunks in collection '{name}'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])