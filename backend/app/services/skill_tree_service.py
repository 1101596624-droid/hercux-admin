"""
Skill Tree Service
Manages skill tree data in Neo4j and calculates user skill levels
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.neo4j import Neo4jClient
from app.models.models import LearningProgress, CourseNode, NodeStatus


class SkillTreeService:
    """Service for managing skill tree in Neo4j"""

    def __init__(self, neo4j_client: Neo4jClient, db: AsyncSession):
        self.neo4j = neo4j_client
        self.db = db

    async def initialize_skill_tree(self):
        """
        Initialize the skill tree structure in Neo4j

        Creates a basic skill tree with common programming skills
        """
        # Create skill nodes
        skills = [
            # Programming Fundamentals
            {"id": "prog_basics", "name": "Programming Basics", "category": "fundamentals", "max_level": 3},
            {"id": "data_structures", "name": "Data Structures", "category": "fundamentals", "max_level": 3},
            {"id": "algorithms", "name": "Algorithms", "category": "fundamentals", "max_level": 3},

            # Web Development
            {"id": "html_css", "name": "HTML & CSS", "category": "web", "max_level": 3},
            {"id": "javascript", "name": "JavaScript", "category": "web", "max_level": 3},
            {"id": "react", "name": "React", "category": "web", "max_level": 3},
            {"id": "nodejs", "name": "Node.js", "category": "web", "max_level": 3},

            # Backend Development
            {"id": "python", "name": "Python", "category": "backend", "max_level": 3},
            {"id": "databases", "name": "Databases", "category": "backend", "max_level": 3},
            {"id": "apis", "name": "API Design", "category": "backend", "max_level": 3},

            # DevOps
            {"id": "git", "name": "Git & Version Control", "category": "devops", "max_level": 3},
            {"id": "docker", "name": "Docker", "category": "devops", "max_level": 3},
            {"id": "ci_cd", "name": "CI/CD", "category": "devops", "max_level": 3},
        ]

        # Create skill nodes in Neo4j
        for skill in skills:
            query = """
            MERGE (s:Skill {id: $id})
            SET s.name = $name,
                s.category = $category,
                s.max_level = $max_level
            """
            await self.neo4j.execute_query(query, skill)

        # Create dependencies (prerequisites)
        dependencies = [
            # Programming fundamentals are prerequisites for everything
            ("data_structures", "prog_basics"),
            ("algorithms", "data_structures"),

            # Web development path
            ("javascript", "html_css"),
            ("react", "javascript"),
            ("nodejs", "javascript"),

            # Backend path
            ("databases", "prog_basics"),
            ("apis", "python"),
            ("apis", "databases"),

            # DevOps path
            ("docker", "git"),
            ("ci_cd", "docker"),
        ]

        for skill_id, prerequisite_id in dependencies:
            query = """
            MATCH (s:Skill {id: $skill_id})
            MATCH (p:Skill {id: $prerequisite_id})
            MERGE (s)-[:REQUIRES]->(p)
            """
            await self.neo4j.execute_query(query, {
                "skill_id": skill_id,
                "prerequisite_id": prerequisite_id
            })

    async def get_user_skill_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user's skill tree with current levels and progress

        Returns:
        - List of skills with current level, progress, and dependencies
        """
        # Get all skills from Neo4j
        skills_query = """
        MATCH (s:Skill)
        OPTIONAL MATCH (s)-[:REQUIRES]->(prereq:Skill)
        RETURN s.id as id,
               s.name as name,
               s.category as category,
               s.max_level as max_level,
               collect(prereq.id) as prerequisites
        """
        skills_data = await self.neo4j.execute_query(skills_query)

        # Calculate user's level for each skill based on completed nodes
        skill_tree = []
        for skill in skills_data:
            # Map skills to course tags (simplified mapping)
            # In a real system, you'd have a more sophisticated mapping
            skill_level, progress = await self._calculate_skill_level(
                user_id,
                skill["id"]
            )

            # Check if skill is unlocked (all prerequisites met)
            is_unlocked = await self._check_skill_unlocked(
                user_id,
                skill["prerequisites"]
            )

            skill_tree.append({
                "skill_id": skill["id"],
                "skill_name": skill["name"],
                "category": skill["category"],
                "current_level": skill_level,
                "max_level": skill["max_level"],
                "progress_percentage": progress,
                "is_unlocked": is_unlocked,
                "prerequisites": skill["prerequisites"]
            })

        return skill_tree

    async def _calculate_skill_level(self, user_id: int, skill_id: str) -> tuple[int, float]:
        """
        Calculate user's level for a specific skill

        Returns: (level, progress_percentage)
        """
        # Map skill IDs to course tags (simplified)
        skill_tag_mapping = {
            "prog_basics": ["programming", "basics", "fundamentals"],
            "data_structures": ["data-structures", "algorithms"],
            "algorithms": ["algorithms", "problem-solving"],
            "html_css": ["html", "css", "web"],
            "javascript": ["javascript", "js"],
            "react": ["react", "frontend"],
            "nodejs": ["nodejs", "backend"],
            "python": ["python"],
            "databases": ["database", "sql"],
            "apis": ["api", "rest"],
            "git": ["git", "version-control"],
            "docker": ["docker", "containers"],
            "ci_cd": ["ci-cd", "devops"],
        }

        tags = skill_tag_mapping.get(skill_id, [])
        if not tags:
            return 0, 0.0

        # Get completed nodes related to this skill
        # This is a simplified approach - in reality, you'd have explicit skill-node mappings
        completed_query = select(func.count(LearningProgress.id)).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.status == NodeStatus.COMPLETED
            )
        )
        completed_result = await self.db.execute(completed_query)
        total_completed = completed_result.scalar() or 0

        # Simple level calculation based on total completed nodes
        # Level 0: 0 nodes
        # Level 1: 1-10 nodes
        # Level 2: 11-30 nodes
        # Level 3: 31+ nodes
        if total_completed == 0:
            return 0, 0.0
        elif total_completed <= 10:
            level = 1
            progress = (total_completed / 10) * 100
        elif total_completed <= 30:
            level = 2
            progress = ((total_completed - 10) / 20) * 100
        else:
            level = 3
            progress = min(((total_completed - 30) / 20) * 100, 100)

        return level, round(progress, 2)

    async def _check_skill_unlocked(self, user_id: int, prerequisites: List[str]) -> bool:
        """
        Check if all prerequisite skills are met

        A skill is unlocked if all prerequisites have level >= 1
        """
        if not prerequisites:
            return True

        for prereq_id in prerequisites:
            level, _ = await self._calculate_skill_level(user_id, prereq_id)
            if level < 1:
                return False

        return True

    async def add_skill_node(self, skill_id: str, name: str, category: str, max_level: int = 3):
        """Add a new skill node to the tree"""
        query = """
        MERGE (s:Skill {id: $id})
        SET s.name = $name,
            s.category = $category,
            s.max_level = $max_level
        """
        await self.neo4j.execute_query(query, {
            "id": skill_id,
            "name": name,
            "category": category,
            "max_level": max_level
        })

    async def add_skill_dependency(self, skill_id: str, prerequisite_id: str):
        """Add a prerequisite relationship between skills"""
        query = """
        MATCH (s:Skill {id: $skill_id})
        MATCH (p:Skill {id: $prerequisite_id})
        MERGE (s)-[:REQUIRES]->(p)
        """
        await self.neo4j.execute_query(query, {
            "skill_id": skill_id,
            "prerequisite_id": prerequisite_id
        })
