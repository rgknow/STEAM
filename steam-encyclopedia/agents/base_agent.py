"""
Base Agent Framework for STEAM Encyclopedia Editorial Board
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json


class AgentRole(Enum):
    SCIENTIST = "scientist"
    ENGINEER = "engineer"
    EDUCATOR = "educator"
    CREATIVE = "creative"
    SPECIALIST = "specialist"


class ContentType(Enum):
    CONCEPT = "concept"
    EXPERIMENT = "experiment"
    APPLICATION = "application"
    THEORY = "theory"
    DISCOVERY = "discovery"
    INNOVATION = "innovation"


class AgeGroup(Enum):
    EARLY_YEARS = "1-5"
    ELEMENTARY = "6-11"
    MIDDLE_SCHOOL = "12-14"
    HIGH_SCHOOL = "15-17"
    HIGHER_ED = "18-25"


@dataclass
class ContentItem:
    id: str
    title: str
    content: str
    content_type: ContentType
    domain: str
    age_groups: List[AgeGroup]
    sources: List[str]
    created_at: datetime
    updated_at: datetime
    version: int
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    multimedia_assets: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    review_status: str = "draft"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type.value,
            "domain": self.domain,
            "age_groups": [ag.value for ag in self.age_groups],
            "sources": self.sources,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "tags": self.tags,
            "prerequisites": self.prerequisites,
            "related_concepts": self.related_concepts,
            "multimedia_assets": self.multimedia_assets,
            "quality_score": self.quality_score,
            "review_status": self.review_status
        }


@dataclass
class ReviewFeedback:
    agent_id: str
    agent_role: AgentRole
    content_id: str
    accuracy_score: float
    clarity_score: float
    age_appropriateness_score: float
    completeness_score: float
    suggestions: List[str]
    approved: bool
    timestamp: datetime


class BaseAgent(ABC):
    """Base class for all editorial board agents."""
    
    def __init__(self, agent_id: str, role: AgentRole, domains: List[str], 
                 specializations: List[str] = None):
        self.agent_id = agent_id
        self.role = role
        self.domains = domains
        self.specializations = specializations or []
        self.collaboration_network: Set[str] = set()
        self.active_tasks: Dict[str, Any] = {}
        self.knowledge_base: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {
            "accuracy": 0.95,
            "productivity": 0.85,
            "collaboration": 0.90
        }
    
    @abstractmethod
    async def analyze_content(self, source_data: Dict[str, Any]) -> ContentItem:
        """Analyze raw source data and create structured content."""
        pass
    
    @abstractmethod
    async def review_content(self, content: ContentItem) -> ReviewFeedback:
        """Review content created by other agents."""
        pass
    
    @abstractmethod
    async def adapt_for_age_group(self, content: ContentItem, 
                                  target_age: AgeGroup) -> ContentItem:
        """Adapt content for specific age group."""
        pass
    
    async def collaborate_with_agent(self, other_agent_id: str, 
                                   content_id: str, query: str) -> Dict[str, Any]:
        """Request collaboration or consultation with another agent."""
        # Simulate inter-agent communication
        return {
            "agent_id": other_agent_id,
            "query": query,
            "response": f"Collaboration response for {content_id}",
            "timestamp": datetime.now().isoformat()
        }
    
    def update_knowledge_base(self, new_knowledge: Dict[str, Any]) -> None:
        """Update agent's knowledge base with new information."""
        self.knowledge_base.update(new_knowledge)
    
    def get_expertise_areas(self) -> List[str]:
        """Return list of expertise areas for this agent."""
        return self.domains + self.specializations
    
    def can_handle_domain(self, domain: str) -> bool:
        """Check if agent can handle content in given domain."""
        return domain.lower() in [d.lower() for d in self.get_expertise_areas()]
    
    async def validate_sources(self, sources: List[str]) -> Dict[str, float]:
        """Validate reliability of content sources."""
        # Simulate source validation
        validation_scores = {}
        for source in sources:
            # In real implementation, this would check against trusted source database
            if any(trusted in source.lower() for trusted in 
                  ['nature', 'science', 'ieee', 'arxiv', 'pubmed', 'nasa', 'nsf']):
                validation_scores[source] = 0.95
            elif any(academic in source.lower() for academic in 
                    ['edu', 'university', 'institute', 'laboratory']):
                validation_scores[source] = 0.85
            else:
                validation_scores[source] = 0.70
        return validation_scores
    
    def generate_content_id(self, title: str, domain: str) -> str:
        """Generate unique content ID."""
        import hashlib
        content_string = f"{title}_{domain}_{datetime.now().isoformat()}"
        return hashlib.md5(content_string.encode()).hexdigest()[:12]
    
    async def process_content_pipeline(self, source_data: Dict[str, Any]) -> ContentItem:
        """Main content processing pipeline."""
        # Step 1: Analyze and create content
        content = await self.analyze_content(source_data)
        
        # Step 2: Validate sources
        source_scores = await self.validate_sources(content.sources)
        avg_source_score = sum(source_scores.values()) / len(source_scores) if source_scores else 0.5
        
        # Step 3: Update quality score based on source validation
        content.quality_score = avg_source_score * 0.4 + 0.6  # Base quality + source reliability
        
        # Step 4: Set initial review status
        content.review_status = "pending_review"
        
        return content
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get current status and metrics for this agent."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "domains": self.domains,
            "specializations": self.specializations,
            "active_tasks": len(self.active_tasks),
            "collaboration_network_size": len(self.collaboration_network),
            "performance_metrics": self.performance_metrics,
            "knowledge_base_size": len(self.knowledge_base)
        }


class AgentCommunicationHub:
    """Central hub for agent-to-agent communication and coordination."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: List[Dict[str, Any]] = []
        self.collaboration_history: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the communication hub."""
        self.agents[agent.agent_id] = agent
    
    async def route_collaboration_request(self, from_agent: str, to_agent: str,
                                        request: Dict[str, Any]) -> Dict[str, Any]:
        """Route collaboration request between agents."""
        if to_agent not in self.agents:
            return {"error": f"Agent {to_agent} not found"}
        
        # Log collaboration
        collaboration_record = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "request": request,
            "timestamp": datetime.now().isoformat()
        }
        self.collaboration_history.append(collaboration_record)
        
        # Update collaboration networks
        if from_agent in self.agents:
            self.agents[from_agent].collaboration_network.add(to_agent)
        if to_agent in self.agents:
            self.agents[to_agent].collaboration_network.add(from_agent)
        
        return {"status": "success", "collaboration_id": len(self.collaboration_history)}
    
    def get_best_agent_for_domain(self, domain: str) -> Optional[str]:
        """Find the best agent to handle content in a specific domain."""
        candidates = []
        for agent_id, agent in self.agents.items():
            if agent.can_handle_domain(domain):
                candidates.append((agent_id, agent.performance_metrics.get("accuracy", 0)))
        
        if candidates:
            return max(candidates, key=lambda x: x[1])[0]
        return None
    
    def get_editorial_board_status(self) -> Dict[str, Any]:
        """Get overall status of the editorial board."""
        return {
            "total_agents": len(self.agents),
            "agents_by_role": {
                role.value: len([a for a in self.agents.values() if a.role == role])
                for role in AgentRole
            },
            "total_collaborations": len(self.collaboration_history),
            "active_tasks": sum(len(a.active_tasks) for a in self.agents.values()),
            "average_performance": {
                metric: sum(a.performance_metrics.get(metric, 0) for a in self.agents.values()) / len(self.agents)
                for metric in ["accuracy", "productivity", "collaboration"]
            } if self.agents else {}
        }


# Singleton communication hub
communication_hub = AgentCommunicationHub()