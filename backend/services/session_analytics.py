"""
TruthLens AI - Session-Based Analytics
Purpose: Track analytics PER QUERY, not globally
Each user query gets its own isolated analytics.
No mixing, no aggregation across queries.
"""

import logging
import time
import uuid
from typing import Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class QueryMetrics:
    """
    Track metrics for a SINGLE query in ISOLATION.
    """
    
    def __init__(self, query_id: str, user_id: str, session_id: str, claim: str):
        """
        Initialize metrics for a single query.
        
        Args:
            query_id: Unique ID for this query
            user_id: User who made the query
            session_id: Session ID
            claim: The claim being analyzed
        """
        self.query_id = query_id
        self.user_id = user_id
        self.session_id = session_id
        self.claim = claim
        
        # Timing
        self.start_time = time.time()
        self.stages = {}  # Track time per stage
        self.end_time = None
        
        # Evidence metrics
        self.search_urls = []
        self.scraped_sources = []
        self.pinecone_results = []
        self.nli_inferences = []
        
        # Verdict
        self.verdict = None
        self.confidence = None
        self.support_count = 0
        self.contradict_count = 0
        self.neutral_count = 0
        
        # Sources
        self.sources_used = []
        self.avg_source_credibility = 0.0
        
        logger.info(f"📊 Initialized metrics for query {query_id}")
    
    def mark_stage_complete(self, stage_name: str):
        """
        Mark a pipeline stage as complete and record time.
        
        Args:
            stage_name: e.g., 'claim_extraction', 'web_scraping', 'pinecone', 'nli'
        """
        elapsed = time.time() - self.start_time
        self.stages[stage_name] = elapsed
        logger.info(f"⏱️  Stage '{stage_name}' completed in {elapsed:.2f}s")
    
    def add_search_urls(self, urls: Dict[str, str]):
        """Record search URLs generated."""
        self.search_urls = list(urls.values())
        logger.info(f"📍 Generated {len(urls)} search URLs")
    
    def add_scraped_source(self, source: Dict):
        """Record a scraped source."""
        self.scraped_sources.append({
            'url': source.get('url'),
            'title': source.get('title'),
            'length': source.get('length', 0)
        })
    
    def add_pinecone_result(self, result: Dict):
        """Record Pinecone search result."""
        self.pinecone_results.append({
            'title': result['title'],
            'url': result['url'],
            'similarity': result['similarity_score']
        })
    
    def add_nli_inference(self, inference: Dict):
        """Record NLI inference result."""
        self.nli_inferences.append({
            'stance': inference['stance'],
            'confidence': inference['confidence']
        })
    
    def set_verdict(self, verdict: Dict):
        """
        Set final verdict.
        
        Args:
            verdict: {
                'verdict': 'TRUE' | 'FALSE' | 'CONFLICTED',
                'confidence': int,
                'support_count': int,
                'contradict_count': int,
                'neutral_count': int,
            }
        """
        self.verdict = verdict['verdict']
        self.confidence = verdict['confidence']
        self.support_count = verdict['support_count']
        self.contradict_count = verdict['contradict_count']
        self.neutral_count = verdict.get('neutral_count', 0)
        
        logger.info(
            f"✅ Verdict: {self.verdict} ({self.confidence}%) "
            f"[{self.support_count}S / {self.contradict_count}C / {self.neutral_count}N]"
        )
    
    def set_sources(self, sources: List[Dict]):
        """
        Set final sources used.
        
        Args:
            sources: List of {
                'url': str,
                'title': str,
                'stance': 'support' | 'contradict',
                'credibility': 'high' | 'medium' | 'low'
            }
        """
        self.sources_used = sources
        
        # Calculate average credibility
        credibility_map = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
        if sources:
            avg = sum(
                credibility_map.get(s.get('credibility', 'low'), 0.3)
                for s in sources
            ) / len(sources)
            self.avg_source_credibility = avg
        
        logger.info(f"📚 Using {len(sources)} sources (avg credibility: {self.avg_source_credibility:.2f})")
    
    def finalize(self) -> Dict:
        """
        Finalize and return complete metrics.
        CRITICAL: This is a SINGLE QUERY snapshot, not global.
        """
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        # Build complete metrics
        metrics = {
            # Query metadata
            'query_id': self.query_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'claim': self.claim,
            'timestamp': datetime.now().isoformat(),
            
            # Processing timeline
            'total_processing_time_seconds': round(total_time, 2),
            'stage_times': {k: round(v, 2) for k, v in self.stages.items()},
            
            # Evidence summary
            'search_urls_generated': len(self.search_urls),
            'sources_scraped': len(self.scraped_sources),
            'pinecone_results': len(self.pinecone_results),
            'nli_inferences': len(self.nli_inferences),
            
            # Verdict
            'verdict': self.verdict,
            'confidence': self.confidence,
            
            # Stance breakdown
            'supporting_evidence': self.support_count,
            'contradicting_evidence': self.contradict_count,
            'neutral_evidence': self.neutral_count,
            'total_evidence_evaluated': (
                self.support_count + self.contradict_count + self.neutral_count
            ),
            
            # Source quality
            'sources_used': len(self.sources_used),
            'average_source_credibility': round(self.avg_source_credibility, 2),
            
            # Details
            'sources': self.sources_used,
            'processing_stages': list(self.stages.keys()),
        }
        
        logger.info(f"✅ Query {self.query_id} metrics finalized")
        return metrics


class SessionAnalytics:
    """
    Track multiple queries in a session while keeping them ISOLATED.
    """
    
    def __init__(self, user_id: str):
        """
        Initialize session.
        
        Args:
            user_id: The user
        """
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())[:8]
        self.queries = {}  # query_id → QueryMetrics
        self.created_at = datetime.now()
        
        logger.info(f"📱 Session {self.session_id} created for user {user_id}")
    
    def create_query_metrics(self, claim: str) -> QueryMetrics:
        """
        Create metrics for a new query.
        
        Args:
            claim: The claim being analyzed
            
        Returns:
            QueryMetrics object
        """
        query_id = str(uuid.uuid4())[:16]
        metrics = QueryMetrics(query_id, self.user_id, self.session_id, claim)
        self.queries[query_id] = metrics
        return metrics
    
    def get_query_metrics(self, query_id: str) -> QueryMetrics:
        """Get metrics for a specific query."""
        return self.queries.get(query_id)
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of ENTIRE SESSION (not individual queries).
        All queries shown separately.
        """
        query_summaries = []
        for query_id, metrics in self.queries.items():
            # Get metrics for each query
            query_summary = metrics.finalize() if hasattr(metrics, 'finalize') else {}
            query_summaries.append(query_summary)
        
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'total_queries': len(self.queries),
            'queries': query_summaries,  # **EACH QUERY IS SEPARATE**
        }
    
    def get_current_query_analytics(self, query_id: str) -> Dict:
        """
        Get analytics for CURRENT QUERY ONLY.
        This is what should be shown to the user during/after analysis.
        """
        metrics = self.get_query_metrics(query_id)
        if not metrics:
            return {}
        
        # Return ONLY this query's metrics
        return metrics.finalize()


# Singleton session manager
class SessionManager:
    """
    Manage all active sessions.
    """
    
    def __init__(self):
        self.sessions = {}  # user_id → SessionAnalytics
    
    def get_session(self, user_id: str) -> SessionAnalytics:
        """Get or create session for user."""
        if user_id not in self.sessions:
            self.sessions[user_id] = SessionAnalytics(user_id)
        return self.sessions[user_id]
    
    def create_query(self, user_id: str, claim: str) -> QueryMetrics:
        """Create a new query in user's session."""
        session = self.get_session(user_id)
        return session.create_query_metrics(claim)

# Global instance
session_manager = SessionManager()

