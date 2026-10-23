"""
Optional project capability: Retrieval-Augmented Generation (RAG).

Implement this module only if this capability is relevant to your application's
user problem. Remove the file if the capability is not used.

Conceptual Overview:
-------------------
Retrieval-Augmented Generation (RAG) enhances model responses by retrieving
relevant external information before passing the prompt to the LLM.

Key concepts to consider when implementing RAG:
1. Document Ingestion: Loading custom domain documents (PDFs, text, markdown).
2. Embeddings & Vector Store: Converting text into dense vector embeddings and
   storing them in a vector database or local index.
3. Retrieval: Searching the vector store for text chunks semantically similar
   to the user query.
4. Grounding: Constructing a prompt that supplies retrieved context to the model,
   reducing hallucinations and grounding answers in verified factual data.

Note:
-----
Do not implement RAG unless your project requires answering questions over
specific custom documents or static domain knowledge bases.
"""

# Implement custom RAG pipeline below if selected for your project.

import csv
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer



from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RECIPES_CSV_PATH = DATA_DIR / "PP_recipes.csv"

class RecipeRAG:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print("Ladataan upotusmallia (Embedding Model)...")
        self.model = SentenceTransformer(model_name)
        self.recipes = []
        self.embeddings = None
        self.load_and_embed_data()

    def load_and_embed_data(self):
        if not RECIPES_CSV_PATH.exists():
            print(f"Varoitus: Tiedostoa {RECIPES_CSV_PATH} ei löytynyt.")
            return

        print("Ladataan reseptejä CSV-tiedostosta...")
        with open(RECIPES_CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Muutetaan tokenit luettavammaksi tekstiksi upotusta varten
                name = row.get("name_tokens", "").replace(",", " ").replace("'", "")
                ingredients = row.get("ingredient_tokens", "").replace(",", " ").replace("'", "")
                
                text_representation = f"Recipe: {name}. Ingredients: {ingredients}"
                
                self.recipes.append({
                    "id": row.get("id") or row.get("i"),
                    "name": name,
                    "ingredients": ingredients,
                    "steps": row.get("steps_tokens", ""),
                    "calorie_level": row.get("calorie_level", ""),
                    "text": text_representation
                })

        if self.recipes:
            texts = [r["text"] for r in self.recipes]
            print(f"Luodaan upotuksia {len(texts)} reseptille (tämä voi viedä hetken ensimmäisellä kerralla)...")
            self.embeddings = self.model.encode(texts, show_progress_bar=True)
            print("RAG-indeksi luotu onnistuneesti!")

    def search(self, query: str, top_k: int = 3) -> list:
        """Hakee semanttisesti parhaiten sopivat reseptit käyttäjän kyselyn perusteella."""
        if self.embeddings is None or len(self.recipes) == 0:
            return [{"error": "Resepti-indeksi on tyhjä tai tiedostoa ei ladattu."}]

        query_embedding = self.model.encode([query])
        
        # Lasketaan kosinisimiliariteetti (cosine similarity)
        similarities = np.dot(self.embeddings, query_embedding.T).flatten() / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            recipe = self.recipes[idx].copy()
            recipe["similarity_score"] = float(similarities[idx])
            results.append(recipe)
            
        return results

# Singleton-instanssi, jota muut moduulit (kuten agent.py tai tools.py) voivat käyttää
_rag_instance = None

def get_rag_search() -> RecipeRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RecipeRAG()
    return _rag_instance

if __name__ == "__main__":
    # Testaa RAG-hakua suoraan ajamalla tämä tiedosto
    rag = get_rag_search()
    test_query = "healthy chicken dinner"
    print(f"\nTestataan hakua: '{test_query}'")
    results = rag.search(test_query, top_k=2)
    print(json.dumps(results, ensure_ascii=False, indent=2))