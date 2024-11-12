# src/vector_store.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import NamedVector
from qdrant_client.models import PointStruct, Distance, VectorParams, models
from typing import List, Optional
from src.config import config
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Secure vector storage management with team isolation"""

    def __init__(self):
        self.client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
            api_key=config.QDRANT_API_KEY,
            https=config.QDRANT_HTTPS
        )
        self.collection_name = "pdf_embeddings"
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2

    def setup_collection(self) -> bool:
        """Create or recreate the vector collection"""
        try:
            # Remove existing collection if it exists
            collections = self.client.get_collections().collections
            if any(collection.name == self.collection_name for collection in collections):
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted existing collection '{self.collection_name}'")

            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "custom_vector": VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                }
            )
            logger.info(f"Created collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error setting up collection: {str(e)}")
            raise

    def search_vectors(
            self,
            team_id: str,
            query_vector: List[float],
            limit: int = 10
    ) -> List[PointStruct]:
        """Search vectors within team's authorization scope"""
        try:
            team_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="team_id",
                        match=models.MatchValue(value=team_id)
                    )
                ]
            )

            # Use NamedVector for the query
            return self.client.search(
                collection_name=self.collection_name,
                query_vector=NamedVector(
                    name="custom_vector",
                    vector=query_vector
                ),
                query_filter=team_filter,
                limit=limit
            )

        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise

    def upsert_points(self, points: List[PointStruct]) -> bool:
        """Insert or update points in the Qdrant collection"""
        try:
            response = self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully upserted {len(points)} points")
            return True

        except Exception as e:
            logger.error(f"Error upserting points: {str(e)}")
            raise


# Initialize global vector store
vector_store = VectorStore()