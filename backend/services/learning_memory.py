"""
[15] LEARNING MEMORY - Adaptive storage and retrieval of successful queries
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import os

logger = logging.getLogger(__name__)


class LearningMemory:
    """
    Store and retrieve successful queries, high-quality sources, and verdicts.
    Enables adaptive learning and improved query expansion over time.
    """
    
    def __init__(self, db_path: str = "truthlens_memory.db"):
        """Initialize learning memory with SQLite backend."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for memory storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table 1: Successful queries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_memory (
                    id INTEGER PRIMARY KEY,
                    original_claim TEXT NOT NULL,
                    queries TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    retrievals INTEGER DEFAULT 1
                )
            """)
            
            # Table 2: High-quality sources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_quality (
                    id INTEGER PRIMARY KEY,
                    domain TEXT UNIQUE NOT NULL,
                    quality_score REAL NOT NULL,
                    times_used INTEGER DEFAULT 1,
                    times_reliable INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 3: Verdict history for similar claims
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verdict_history (
                    id INTEGER PRIMARY KEY,
                    claim_hash TEXT NOT NULL,
                    original_claim TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    explanation TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("[LEARNING] ✅ Memory database initialized")
        
        except Exception as e:
            logger.warning(f"[LEARNING] ⚠️ Database init error: {e}")
    
    def store_query(self, claim: str, queries: List[str], verdict: str, confidence: float):
        """
        Store a successful query and verdict.
        
        Args:
            claim: Original claim analyzed
            queries: List of search queries used
            verdict: Resulting verdict (TRUE/FALSE/UNCERTAIN)
            confidence: Confidence score (0-1)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            queries_json = json.dumps(queries)
            
            cursor.execute("""
                INSERT INTO query_memory (original_claim, queries, verdict, confidence)
                VALUES (?, ?, ?, ?)
            """, (claim, queries_json, verdict, confidence))
            
            conn.commit()
            conn.close()
            logger.debug(f"[LEARNING] Stored query: {claim[:50]}... → {verdict}")
        
        except Exception as e:
            logger.warning(f"[LEARNING] Error storing query: {e}")
    
    def retrieve_similar_queries(self, claim: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve similar claims from memory.
        
        Args:
            claim: Current claim to find similar memories for
            limit: Max results to return
            
        Returns:
            List of dict: [{'claim': str, 'queries': List[str], 'verdict': str, 'confidence': float}]
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple keyword matching (could be upgraded to semantic similarity)
            keywords = claim.split()[:3]  # First 3 words as search terms
            
            results = []
            for keyword in keywords:
                cursor.execute("""
                    SELECT original_claim, queries, verdict, confidence, retrievals
                    FROM query_memory
                    WHERE original_claim LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{keyword}%", limit))
                
                for row in cursor.fetchall():
                    if row not in results:
                        results.append({
                            'claim': row[0],
                            'queries': json.loads(row[1]),
                            'verdict': row[2],
                            'confidence': row[3],
                            'times_retrieved': row[4]
                        })
            
            conn.close()
            
            logger.debug(f"[LEARNING] Retrieved {len(results)} similar queries")
            return results[:limit]
        
        except Exception as e:
            logger.warning(f"[LEARNING] Error retrieving queries: {e}")
            return []
    
    def update_source_quality(self, domain: str, reliable: bool):
        """
        Update source quality score based on reliability feedback.
        
        Args:
            domain: Source domain (e.g., 'bbc.com')
            reliable: Whether this source proved reliable
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if domain exists
            cursor.execute("SELECT id, times_used, times_reliable FROM source_quality WHERE domain = ?", (domain,))
            row = cursor.fetchone()
            
            if row:
                # Update existing
                times_used = row[1] + 1
                times_reliable = row[2] + (1 if reliable else 0)
                quality_score = times_reliable / times_used
                
                cursor.execute("""
                    UPDATE source_quality
                    SET times_used = ?, times_reliable = ?, quality_score = ?
                    WHERE domain = ?
                """, (times_used, times_reliable, quality_score, domain))
            else:
                # Insert new
                times_reliable = 1 if reliable else 0
                quality_score = times_reliable
                
                cursor.execute("""
                    INSERT INTO source_quality (domain, quality_score, times_used, times_reliable)
                    VALUES (?, ?, 1, ?)
                """, (domain, quality_score, times_reliable))
            
            conn.commit()
            conn.close()
            logger.debug(f"[LEARNING] Updated source quality: {domain} → reliable={reliable}")
        
        except Exception as e:
            logger.warning(f"[LEARNING] Error updating source quality: {e}")
    
    def get_trusted_domains(self, threshold: float = 0.7) -> List[str]:
        """
        Get list of domains with high reliability scores.
        
        Args:
            threshold: Minimum quality score (0-1)
            
        Returns:
            List of trusted domains
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT domain FROM source_quality
                WHERE quality_score >= ?
                ORDER BY quality_score DESC
            """, (threshold,))
            
            domains = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            logger.debug(f"[LEARNING] Retrieved {len(domains)} trusted domains")
            return domains
        
        except Exception as e:
            logger.warning(f"[LEARNING] Error retrieving trusted domains: {e}")
            return []
    
    def store_verdict(self, claim: str, verdict: str, confidence: float, explanation: str = ""):
        """
        Store verdict in history for future reference.
        
        Args:
            claim: Original claim
            verdict: Final verdict (TRUE/FALSE/UNCERTAIN)
            confidence: Confidence score (0-1)
            explanation: Optional explanation
        """
        try:
            import hashlib
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create hash of claim for deduplication
            claim_hash = hashlib.md5(claim.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO verdict_history (claim_hash, original_claim, verdict, confidence, explanation)
                VALUES (?, ?, ?, ?, ?)
            """, (claim_hash, claim, verdict, confidence, explanation))
            
            conn.commit()
            conn.close()
            logger.debug(f"[LEARNING] Stored verdict: {claim[:40]}... → {verdict}")
        
        except Exception as e:
            logger.warning(f"[LEARNING] Error storing verdict: {e}")
    
    def get_verdict_history(self, claim: str, days: int = 30) -> Optional[Dict]:
        """
        Retrieve previous verdict for identical or very similar claim.
        
        Args:
            claim: Current claim
            days: Look back this many days
            
        Returns:
            Dict with previous verdict or None
        """
        try:
            import hashlib
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            claim_hash = hashlib.md5(claim.encode()).hexdigest()
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT verdict, confidence, explanation, timestamp
                FROM verdict_history
                WHERE claim_hash = ? AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (claim_hash, cutoff_date))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.debug(f"[LEARNING] Found previous verdict for claim")
                return {
                    'verdict': row[0],
                    'confidence': row[1],
                    'explanation': row[2],
                    'timestamp': row[3]
                }
            
            return None
        
        except Exception as e:
            logger.warning(f"[LEARNING] Error retrieving verdict history: {e}")
            return None
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about stored memory."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM query_memory")
            query_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM source_quality")
            source_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM verdict_history")
            verdict_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'stored_queries': query_count,
                'tracked_sources': source_count,
                'verdict_history': verdict_count,
                'database_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            }
        
        except Exception as e:
            logger.warning(f"[LEARNING] Error getting stats: {e}")
            return {}
