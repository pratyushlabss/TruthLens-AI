"""Graph-based propagation risk model using NetworkX."""

import networkx as nx
from typing import Dict, Tuple
import random
import numpy as np

class PropagationModel:
    """
    Analyzes misinformation propagation risk using graph theory.
    """
    
    def __init__(self):
        """Initialize propagation model."""
        self.graph = nx.DiGraph()
    
    def analyze_propagation_risk(self, claim: str, nlp_score: float) -> Dict:
        """
        Analyze propagation risk for a claim.
        
        Args:
            claim: The claim text
            nlp_score: NLP confidence score (0-100)
            
        Returns:
            Dictionary with risk level and score
        """
        # Simulate tweet velocity analysis
        tweet_velocity = self._estimate_tweet_velocity(claim, nlp_score)
        
        # Estimate cluster size
        cluster_size = self._estimate_cluster_size(tweet_velocity)
        
        # Calculate reshare patterns
        reshare_factor = self._estimate_reshare_factor(claim)
        
        # Combined propagation score
        propagation_score = self._calculate_propagation_score(
            tweet_velocity,
            cluster_size,
            reshare_factor
        )
        
        # Determine risk level
        if propagation_score < 30:
            risk = "LOW"
        elif propagation_score < 70:
            risk = "MEDIUM"
        else:
            risk = "HIGH"
        
        return {
            "propagation_risk": risk,
            "propagation_score": propagation_score,
            "tweet_velocity": tweet_velocity,
            "cluster_size": cluster_size,
            "reshare_factor": reshare_factor
        }
    
    def _estimate_tweet_velocity(self, claim: str, nlp_score: float) -> float:
        """Estimate how fast this claim spreads."""
        # Sensational keywords increase velocity
        sensational_keywords = [
            "shocking", "scandal", "coverup", "exposed", "conspiracy",
            "urgent", "breaking", "exclusive", "incredible", "unbelievable"
        ]
        
        claim_lower = claim.lower()
        keyword_count = sum(1 for kw in sensational_keywords if kw in claim_lower)
        
        # Base velocity from claim virality + NLP score
        base_velocity = (nlp_score / 100) * 50  # 0-50
        keyword_boost = keyword_count * 5  # +5 per keyword
        
        velocity = min(100, base_velocity + keyword_boost)
        return velocity
    
    def _estimate_cluster_size(self, velocity: float) -> int:
        """Estimate number of users affected."""
        # Higher velocity = larger cluster
        base_cluster = 100
        size = int(base_cluster * (1 + velocity / 50))
        return min(size, 10000)
    
    def _estimate_reshare_factor(self, claim: str) -> float:
        """Estimate reshare likelihood (0-100)."""
        # Short, punchy claims spread more
        if len(claim) < 100:
            return 75
        elif len(claim) < 200:
            return 60
        else:
            return 40
    
    def _calculate_propagation_score(
        self,
        velocity: float,
        cluster_size: int,
        reshare_factor: float
    ) -> float:
        """Calculate combined propagation score."""
        # Weighted combination
        velocity_weight = 0.5
        cluster_weight = 0.3
        reshare_weight = 0.2
        
        # Normalize cluster size to 0-100
        cluster_normalized = min(100, (cluster_size / 100))
        
        score = (
            velocity_weight * velocity +
            cluster_weight * cluster_normalized +
            reshare_weight * reshare_factor
        )
        
        return round(score, 2)
    
    def build_propagation_graph(self, claim: str, num_nodes: int = 50) -> nx.DiGraph:
        """
        Build a propagation graph for visualization.
        
        Args:
            claim: Claim text
            num_nodes: Number of nodes in graph
            
        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()
        
        # Add source node
        G.add_node(0, label="Original Claim", color="red")
        
        # Add secondary nodes
        for i in range(1, num_nodes):
            G.add_node(i, label=f"User {i}", color="orange" if i < 10 else "yellow")
        
        # Add edges (propagation paths)
        G.add_edge(0, 1)
        for i in range(1, num_nodes - 1):
            targets = random.sample(range(i + 1, num_nodes), k=min(2, num_nodes - i - 1))
            for target in targets:
                G.add_edge(i, target)
        
        self.graph = G
        return G
    
    def get_graph_metrics(self) -> Dict:
        """Get graph analysis metrics."""
        if not self.graph or len(self.graph) == 0:
            return {}
        
        return {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "avg_clustering": nx.average_clustering(self.graph.to_undirected()),
        }
