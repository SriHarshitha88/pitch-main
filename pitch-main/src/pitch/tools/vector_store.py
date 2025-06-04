from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
import os
from typing import List, Dict, Any
import json

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize or get existing index
        index_name = "pitch-analyzer"
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embeddings dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-west-2"
                )
            )
        self.index = self.pc.Index(index_name)

    async def store_knowledge_file(self, file_content: str, metadata: Dict[str, Any]) -> str:
        """Store a knowledge file in the vector database"""
        # Generate embedding for the content
        embedding = await self.embeddings.aembed_query(file_content)
        
        # Create a unique ID for the document
        doc_id = f"kb_{metadata['filename']}_{metadata['upload_date']}"
        
        # Store in Pinecone
        self.index.upsert(
            vectors=[{
                "id": doc_id,
                "values": embedding,
                "metadata": metadata
            }]
        )
        return doc_id

    async def store_pitch_deck(self, deck_content: str, metadata: Dict[str, Any]) -> str:
        """Store a pitch deck in the vector database"""
        embedding = await self.embeddings.aembed_query(deck_content)
        doc_id = f"deck_{metadata['filename']}_{metadata['upload_date']}"
        
        self.index.upsert(
            vectors=[{
                "id": doc_id,
                "values": embedding,
                "metadata": metadata
            }]
        )
        return doc_id

    async def store_analysis_result(self, analysis_content: str, metadata: Dict[str, Any]) -> str:
        """Store an analysis result in the vector database"""
        embedding = await self.embeddings.aembed_query(analysis_content)
        doc_id = f"analysis_{metadata['deck_id']}_{metadata['timestamp']}"
        
        self.index.upsert(
            vectors=[{
                "id": doc_id,
                "values": embedding,
                "metadata": metadata
            }]
        )
        return doc_id

    async def semantic_search(self, query: str, filter_criteria: Dict[str, Any] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search across the vector database"""
        # Generate embedding for the query
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Search in Pinecone
        results = self.index.query(
            vector=query_embedding,
            filter=filter_criteria,
            top_k=top_k,
            include_metadata=True
        )
        
        return results.matches

    async def find_similar_decks(self, deck_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar pitch decks"""
        # Get the vector for the deck
        deck_vector = self.index.fetch(ids=[deck_id])
        if not deck_vector.vectors:
            return []
            
        # Search for similar decks
        results = self.index.query(
            vector=deck_vector.vectors[deck_id].values,
            filter={"type": "deck"},
            top_k=top_k,
            include_metadata=True
        )
        
        return results.matches

    async def compare_versions(self, deck_id_1: str, deck_id_2: str) -> Dict[str, Any]:
        """Compare two versions of a pitch deck"""
        # Get both vectors
        vectors = self.index.fetch(ids=[deck_id_1, deck_id_2])
        if not vectors.vectors:
            return {"error": "One or both decks not found"}
            
        # Calculate similarity
        similarity = self.index.query(
            vector=vectors.vectors[deck_id_1].values,
            filter={"id": deck_id_2},
            top_k=1,
            include_metadata=True
        )
        
        return {
            "similarity_score": similarity.matches[0].score if similarity.matches else 0,
            "deck1_metadata": vectors.vectors[deck_id_1].metadata,
            "deck2_metadata": vectors.vectors[deck_id_2].metadata
        } 