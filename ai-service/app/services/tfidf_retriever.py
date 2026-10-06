import json
import os
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TfidfRetriever:
    def __init__(self, kb_path: str):
        self.kb_path = kb_path
        self.articles: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self._load_and_index()

    def _load_and_index(self):
        if not os.path.exists(self.kb_path):
            return

        with open(self.kb_path, 'r', encoding='utf-8') as f:
            self.articles = json.load(f)

        if not self.articles:
            return

        corpus = []
        for art in self.articles:
            # Combine title, symptoms, cause, keywords into indexed document
            symptoms_text = " ".join(art.get("symptoms", []))
            keywords_text = " ".join(art.get("keywords", []))
            doc = f"{art.get('title', '')} {symptoms_text} {art.get('possibleCause', '')} {keywords_text}"
            corpus.append(doc)

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.tfidf_matrix is None or not self.articles:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.05:  # Relevance threshold
                article = self.articles[idx].copy()
                article["tfidfScore"] = score
                results.append(article)

        return results
