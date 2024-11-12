import pdfplumber
from typing import List, Any
from werkzeug.utils import secure_filename
from src.ai_service import ai_service
from src.vector_store import vector_store
from qdrant_client.models import PointStruct
import uuid
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Secure document processing with team isolation"""

    def process_pdf(
            self,
            pdf_file: Any,
            team_id: str,
            doc_name: str,
            document_id: str,
            chunk_size: int = 500
    ) -> List[PointStruct]:
        """Process PDF with team-scoped authorization"""
        try:
            points = []
            doc_name = secure_filename(doc_name)

            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if not text:
                        continue

                    # Create chunks
                    chunks = self._create_chunks(text, chunk_size)

                    # Generate embeddings
                    embeddings = [ai_service.get_embedding(chunk) for chunk in chunks]

                    # Create points
                    points.extend(self._create_points(
                        chunks, embeddings, team_id, doc_name,
                        document_id, page_num
                    ))

            # Store vectors
            if points:
                vector_store.upsert_points(points)

            return points

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

    def _create_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Create overlapping chunks from text"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[max(0, i - 50):i + chunk_size]
            chunks.append(chunk)
        return chunks

    def _create_points(
            self,
            chunks: List[str],
            embeddings: List[List[float]],
            team_id: str,
            doc_name: str,
            document_id: str,
            page_num: int
    ) -> List[PointStruct]:
        """Create points for vector storage"""
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector={"custom_vector": embedding},
                payload={
                    "team_id": team_id,
                    "doc_name": doc_name,
                    "document_id": document_id,
                    "page_number": page_num,
                    "chunk_index": i,
                    "text": chunk,
                    "embedding_model": "all-MiniLM-L6-v2"
                }
            )
            points.append(point)
        return points


# Initialize global document processor
document_processor = DocumentProcessor()