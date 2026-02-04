"""
NLP Helper Module for Semantic Similarity Analysis

Provides utilities for comparing skill descriptions and clustering similar skills
using sentence embeddings and cosine similarity.
"""

import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class NLPHelper:
    """Handles semantic similarity analysis for skill descriptions."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the NLP helper with a pretrained sentence transformer model.
        
        Args:
            model_name: HuggingFace model identifier for sentence embeddings.
                       Lightweight default for fast inference.
        """
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a given text, with caching.
        
        Args:
            text: The text to embed.
            
        Returns:
            Embedding vector as numpy array.
        """
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        self.embeddings_cache[text] = embedding
        return embedding
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        similarity = cosine_similarity([emb1], [emb2])[0][0]
        return float(similarity)
    
    def cluster_skills(
        self,
        skills: List[Dict[str, str]],
        threshold: float = 0.6
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Cluster skills based on semantic similarity of their descriptions.
        
        Args:
            skills: List of skill dicts with 'name' and 'description' keys.
            threshold: Similarity threshold for grouping (0-1). Higher = stricter.
            
        Returns:
            Dictionary mapping cluster IDs to lists of skills.
        """
        if not skills:
            return {}
        
        # Compute embeddings for all descriptions
        embeddings = np.array([
            self.get_embedding(skill.get("description", skill.get("name", "")))
            for skill in skills
        ])
        
        # Compute pairwise similarities
        similarity_matrix = cosine_similarity(embeddings)
        
        # Cluster using a greedy approach
        clusters = {}
        assigned = set()
        cluster_id = 0
        
        for i, skill in enumerate(skills):
            if i in assigned:
                continue
            
            # Start a new cluster
            cluster = [skill]
            assigned.add(i)
            
            # Find similar skills
            for j in range(i + 1, len(skills)):
                if j not in assigned and similarity_matrix[i][j] >= threshold:
                    cluster.append(skills[j])
                    assigned.add(j)
            
            clusters[f"cluster_{cluster_id}"] = cluster
            cluster_id += 1
        
        return clusters
    
    def find_duplicates(
        self,
        skills: List[Dict[str, str]],
        threshold: float = 0.85
    ) -> List[Tuple[Dict[str, str], Dict[str, str], float]]:
        """
        Find potentially duplicate or highly overlapping skills.
        
        Args:
            skills: List of skill dicts.
            threshold: Similarity threshold for considering duplicates.
            
        Returns:
            List of tuples: (skill1, skill2, similarity_score)
        """
        duplicates = []
        
        for i in range(len(skills)):
            for j in range(i + 1, len(skills)):
                similarity = self.compute_similarity(
                    skills[i].get("description", skills[i].get("name", "")),
                    skills[j].get("description", skills[j].get("name", ""))
                )
                
                if similarity >= threshold:
                    duplicates.append((skills[i], skills[j], similarity))
        
        return duplicates
