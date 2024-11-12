from typing import Dict, Any, List, Set, Tuple
from src.ai_service import ai_service
from src.vector_store import vector_store
import logging

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generate answers within team authorization scope"""

    def generate_answer(self, team_id: str, question: str) -> Dict[str, Any]:
        """Generate answers using only team-authorized documents"""
        try:
            # Generate question embedding
            query_vector = ai_service.get_embedding(question)

            # Get relevant documents
            points = vector_store.search_vectors(team_id, query_vector, limit=15)

            if not points:
                return {
                    "answer": "No relevant documents found",
                    "sources": [],
                    "status": "no_context"
                }

            # Process context and sources
            context_parts, sources = self._process_points(points)

            # Generate answer
            answer = self._generate_ai_response(context_parts, question)

            return {
                "answer": answer,
                "sources": list(sources),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": "Error generating answer",
                "sources": [],
                "status": "error",
                "error": str(e)
            }

    def _process_points(self, points: List[Any]) -> Tuple[List[str], Set[Tuple[str, int]]]:
        """Process vector search results"""
        context_parts = []
        sources = set()
        seen_text = set()

        for point in points:
            if point.payload:
                text = point.payload.get('text', '').strip()
                if text in seen_text:
                    continue

                doc_info = f"[Document: {point.payload.get('doc_name')}, Page: {point.payload.get('page_number')}]"
                context_parts.append(f"{doc_info}\n{text}")
                sources.add((
                    point.payload.get('doc_name'),
                    point.payload.get('page_number')
                ))
                seen_text.add(text)

        return context_parts, sources

    def _generate_ai_response(self, context_parts: List[str], question: str) -> str:
        """Generate AI response using context"""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that provides accurate, "
                    "comprehensive answers based on the given context. "
                    "Always cite your sources using [Document: X, Page: Y] format."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Answer this question using only the context provided. "
                    f"If you cannot answer based on the context, say so.\n\n"
                    f"Context:\n{' '.join(context_parts)}\n\n"
                    f"Question: {question}"
                )
            }
        ]

        return ai_service.get_completion(messages)


# Initialize global answer generator
answer_generator = AnswerGenerator()