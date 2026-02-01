"""
Course Ingestion Service
Handles importing course packages into the HERCU system
"""
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging
import json

from app.models.models import Course, CourseNode, DifficultyLevel, NodeType
from app.schemas.schemas import (
    CourseManifest,
    PackageNodeConfig,
    CourseIngestionResponse,
    CoursePackageValidation,
    CourseUpdate,
    NodeUpdate
)

logger = logging.getLogger(__name__)

# Supported schema versions
SUPPORTED_SCHEMA_VERSIONS = ["1.0", "1.1"]
CURRENT_SCHEMA_VERSION = "1.1"


class CourseIngestionService:
    """Service for ingesting course packages"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.errors: List[str] = []
        self.warnings: List[str] = []

    async def validate_package(self, manifest: CourseManifest) -> CoursePackageValidation:
        """
        Validate a course package before ingestion

        Args:
            manifest: Course manifest to validate

        Returns:
            CoursePackageValidation with validation results
        """
        errors = []
        warnings = []

        # Check schema version
        package_version = manifest.packageVersion or "1.0"
        if package_version not in SUPPORTED_SCHEMA_VERSIONS:
            errors.append(
                f"Unsupported package version: {package_version}. "
                f"Supported versions: {', '.join(SUPPORTED_SCHEMA_VERSIONS)}"
            )
        elif package_version != CURRENT_SCHEMA_VERSION:
            warnings.append(
                f"Package version {package_version} is outdated. "
                f"Current version is {CURRENT_SCHEMA_VERSION}. "
                f"Consider upgrading your package format."
            )

        # Check basic course info
        if not manifest.courseName or len(manifest.courseName.strip()) == 0:
            errors.append("Course name is required")

        if not manifest.difficulty:
            errors.append("Course difficulty is required")
        elif manifest.difficulty not in ["beginner", "intermediate", "advanced", "expert"]:
            errors.append(f"Invalid difficulty: {manifest.difficulty}")

        # Check nodes
        if not manifest.nodes or len(manifest.nodes) == 0:
            errors.append("Course must have at least one node")
        else:
            # Check for duplicate node IDs
            node_ids = [node.nodeId for node in manifest.nodes]
            if len(node_ids) != len(set(node_ids)):
                errors.append("Duplicate node IDs found")
                # Find and report duplicates
                seen = set()
                duplicates = set()
                for node_id in node_ids:
                    if node_id in seen:
                        duplicates.add(node_id)
                    seen.add(node_id)
                if duplicates:
                    errors.append(f"Duplicate node IDs: {', '.join(duplicates)}")

            # Validate each node
            for idx, node in enumerate(manifest.nodes):
                node_errors = self._validate_node(node, idx, node_ids)
                errors.extend(node_errors)

            # Check parent references
            for node in manifest.nodes:
                if node.parentId and node.parentId not in node_ids:
                    errors.append(f"Node {node.nodeId}: parent {node.parentId} not found")

            # Check for circular dependencies in parent-child relationships
            circular_deps = self._check_circular_dependencies(manifest.nodes)
            if circular_deps:
                errors.append(f"Circular dependencies detected: {circular_deps}")

        # Calculate estimated duration
        estimated_duration = 0.0
        for node in manifest.nodes:
            if node.estimatedMinutes:
                estimated_duration += node.estimatedMinutes / 60.0

        # Warnings
        if not manifest.instructor:
            warnings.append("No instructor specified")

        if not manifest.thumbnailUrl:
            warnings.append("No thumbnail URL provided")

        if estimated_duration == 0:
            warnings.append("No estimated duration provided for any nodes")

        if not manifest.tags or len(manifest.tags) == 0:
            warnings.append("No tags specified - this may affect course discoverability")

        # Log validation results
        if errors:
            logger.warning(f"Package validation failed for '{manifest.courseName}': {len(errors)} errors")
        elif warnings:
            logger.info(f"Package validation passed for '{manifest.courseName}' with {len(warnings)} warnings")
        else:
            logger.info(f"Package validation passed for '{manifest.courseName}' with no issues")

        return CoursePackageValidation(
            isValid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            nodeCount=len(manifest.nodes),
            estimatedDuration=estimated_duration
        )

    def _validate_node(self, node: PackageNodeConfig, index: int, all_node_ids: List[str]) -> List[str]:
        """Validate a single node configuration"""
        errors = []

        # Check required fields
        if not node.nodeId:
            errors.append(f"Node {index}: nodeId is required")

        if not node.type:
            errors.append(f"Node {node.nodeId}: type is required")
        elif node.type not in ["video", "simulator", "quiz", "reading", "practice"]:
            errors.append(f"Node {node.nodeId}: invalid type '{node.type}'")

        if not node.componentId:
            errors.append(f"Node {node.nodeId}: componentId is required")

        if not node.title:
            errors.append(f"Node {node.nodeId}: title is required")

        # Validate timeline config if present
        if node.timelineConfig:
            for step_idx, step in enumerate(node.timelineConfig.steps):
                if not step.stepId:
                    errors.append(f"Node {node.nodeId}, step {step_idx}: stepId is required")

                if not step.type:
                    errors.append(f"Node {node.nodeId}, step {step_idx}: type is required")

                # Type-specific validation
                if step.type == "video" and not step.videoUrl:
                    errors.append(f"Node {node.nodeId}, step {step.stepId}: videoUrl required for video type")

                if step.type == "simulator" and not step.simulatorId:
                    errors.append(f"Node {node.nodeId}, step {step.stepId}: simulatorId required for simulator type")

                if step.type == "quiz":
                    if not step.question:
                        errors.append(f"Node {node.nodeId}, step {step.stepId}: question required for quiz type")
                    if not step.options or len(step.options) < 2:
                        errors.append(f"Node {node.nodeId}, step {step.stepId}: at least 2 options required for quiz")
                    if step.correctAnswer is None:
                        errors.append(f"Node {node.nodeId}, step {step.stepId}: correctAnswer required for quiz")

        # Validate unlock condition
        if node.unlockCondition:
            if node.unlockCondition.type == "all_complete":
                if not node.unlockCondition.nodeIds:
                    errors.append(f"Node {node.nodeId}: nodeIds required for 'all_complete' unlock type")
                else:
                    # Check if referenced nodes exist
                    for ref_node_id in node.unlockCondition.nodeIds:
                        if ref_node_id not in all_node_ids:
                            errors.append(f"Node {node.nodeId}: referenced node {ref_node_id} not found")

        return errors

    def _check_circular_dependencies(self, nodes: List[PackageNodeConfig]) -> Optional[str]:
        """
        Check for circular dependencies in parent-child relationships

        Returns:
            Error message if circular dependency found, None otherwise
        """
        # Build parent-child map
        parent_map = {}
        for node in nodes:
            if node.parentId:
                parent_map[node.nodeId] = node.parentId

        # Check each node for circular dependencies
        for node_id in parent_map:
            visited = set()
            current = node_id

            while current in parent_map:
                if current in visited:
                    # Found a cycle
                    cycle_path = " -> ".join(visited) + f" -> {current}"
                    return f"Circular dependency: {cycle_path}"

                visited.add(current)
                current = parent_map[current]

        return None

    async def ingest_course(
        self,
        manifest: CourseManifest,
        publish_immediately: bool = False
    ) -> CourseIngestionResponse:
        """
        Ingest a course package into the database

        Args:
            manifest: Course manifest
            publish_immediately: Whether to publish the course immediately

        Returns:
            CourseIngestionResponse with ingestion results
        """
        try:
            # Validate first
            validation = await self.validate_package(manifest)
            if not validation.isValid:
                return CourseIngestionResponse(
                    success=False,
                    courseId=0,
                    nodesCreated=0,
                    message="Validation failed",
                    errors=validation.errors
                )

            # Create course
            course = await self._create_course(manifest, publish_immediately)

            # Create nodes
            nodes_created = await self._create_nodes(course.id, manifest.nodes)

            # Commit transaction
            await self.db.commit()
            await self.db.refresh(course)

            return CourseIngestionResponse(
                success=True,
                courseId=course.id,
                nodesCreated=nodes_created,
                message=f"Successfully ingested course '{manifest.courseName}' with {nodes_created} nodes.",
                errors=None
            )

        except Exception as e:
            await self.db.rollback()
            return CourseIngestionResponse(
                success=False,
                courseId=0,
                nodesCreated=0,
                message=f"Ingestion failed: {str(e)}",
                errors=[str(e)]
            )

    async def _create_course(self, manifest: CourseManifest, publish: bool) -> Course:
        """Create course record from manifest"""
        # Map difficulty string to enum
        difficulty_map = {
            "beginner": DifficultyLevel.BEGINNER,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "advanced": DifficultyLevel.ADVANCED,
            "expert": DifficultyLevel.EXPERT
        }

        course = Course(
            name=manifest.courseName,
            description=manifest.courseDescription,
            difficulty=difficulty_map.get(manifest.difficulty, DifficultyLevel.BEGINNER),
            tags=manifest.tags,
            instructor=manifest.instructor,
            duration_hours=manifest.durationHours,
            thumbnail_url=manifest.thumbnailUrl,
            is_published=1 if publish else 0
        )

        self.db.add(course)
        await self.db.flush()  # Get the course ID

        return course

    async def _create_nodes(self, course_id: int, nodes: List[PackageNodeConfig]) -> int:
        """Create course nodes from manifest"""
        # First pass: create all nodes without parent references
        node_id_map: Dict[str, int] = {}  # Maps nodeId to database ID

        for node_config in nodes:
            # Map type string to enum
            type_map = {
                "video": NodeType.VIDEO,
                "simulator": NodeType.SIMULATOR,
                "quiz": NodeType.QUIZ,
                "reading": NodeType.READING,
                "practice": NodeType.PRACTICE
            }

            # Build timeline config JSON
            timeline_config = None
            if node_config.timelineConfig:
                timeline_config = {
                    "steps": [
                        {
                            "stepId": step.stepId,
                            "type": step.type,
                            **{k: v for k, v in step.model_dump().items()
                               if k not in ["stepId", "type"] and v is not None}
                        }
                        for step in node_config.timelineConfig.steps
                    ]
                }

            # Build unlock condition JSON
            unlock_condition = None
            if node_config.unlockCondition:
                unlock_condition = node_config.unlockCondition.model_dump()

            node = CourseNode(
                course_id=course_id,
                parent_id=None,  # Will be set in second pass
                node_id=node_config.nodeId,
                type=type_map.get(node_config.type, NodeType.READING),
                component_id=node_config.componentId,
                title=node_config.title,
                description=node_config.description,
                sequence=node_config.sequence,
                timeline_config=timeline_config,
                unlock_condition=unlock_condition
            )

            self.db.add(node)
            await self.db.flush()  # Get the node ID

            node_id_map[node_config.nodeId] = node.id

        # Second pass: set parent references
        for node_config in nodes:
            if node_config.parentId:
                parent_db_id = node_id_map.get(node_config.parentId)
                if parent_db_id:
                    # Update the node with parent_id
                    result = await self.db.execute(
                        select(CourseNode).where(CourseNode.node_id == node_config.nodeId)
                    )
                    node = result.scalar_one()
                    node.parent_id = parent_db_id

        return len(nodes)

    async def get_course_by_name(self, course_name: str) -> Course | None:
        """Get course by name"""
        result = await self.db.execute(
            select(Course).where(Course.name == course_name)
        )
        return result.scalar_one_or_none()

    async def delete_course(self, course_id: int) -> bool:
        """Delete a course and all its nodes"""
        try:
            # Delete nodes first (due to foreign key)
            result = await self.db.execute(
                select(CourseNode).where(CourseNode.course_id == course_id)
            )
            nodes = result.scalars().all()
            for node in nodes:
                await self.db.delete(node)

            # Delete course
            result = await self.db.execute(
                select(Course).where(Course.id == course_id)
            )
            course = result.scalar_one_or_none()
            if course:
                await self.db.delete(course)
                await self.db.commit()
                return True

            return False

        except Exception as e:
            await self.db.rollback()
            raise e

    async def update_course(self, course_id: int, update_data: CourseUpdate) -> Course | None:
        """
        Update course metadata

        Args:
            course_id: ID of the course to update
            update_data: Fields to update

        Returns:
            Updated course or None if not found
        """
        try:
            result = await self.db.execute(
                select(Course).where(Course.id == course_id)
            )
            course = result.scalar_one_or_none()

            if not course:
                return None

            # Update fields if provided
            if update_data.courseName is not None:
                course.name = update_data.courseName
            if update_data.courseDescription is not None:
                course.description = update_data.courseDescription
            if update_data.difficulty is not None:
                difficulty_map = {
                    "beginner": DifficultyLevel.BEGINNER,
                    "intermediate": DifficultyLevel.INTERMEDIATE,
                    "advanced": DifficultyLevel.ADVANCED,
                    "expert": DifficultyLevel.EXPERT
                }
                course.difficulty = difficulty_map.get(update_data.difficulty, DifficultyLevel.BEGINNER)
            if update_data.instructor is not None:
                course.instructor = update_data.instructor
            if update_data.tags is not None:
                course.tags = update_data.tags
            if update_data.durationHours is not None:
                course.duration_hours = update_data.durationHours
            if update_data.thumbnailUrl is not None:
                course.thumbnail_url = update_data.thumbnailUrl
            if update_data.isPublished is not None:
                course.is_published = update_data.isPublished

            await self.db.commit()
            await self.db.refresh(course)
            return course

        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_course_by_id(self, course_id: int) -> Course | None:
        """Get course by ID"""
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def get_node_by_id(self, node_id: int) -> CourseNode | None:
        """Get node by database ID"""
        result = await self.db.execute(
            select(CourseNode).where(CourseNode.id == node_id)
        )
        return result.scalar_one_or_none()

    async def get_node_by_node_id(self, node_id: str) -> CourseNode | None:
        """Get node by node_id string"""
        result = await self.db.execute(
            select(CourseNode).where(CourseNode.node_id == node_id)
        )
        return result.scalar_one_or_none()

    async def update_node(self, node_id: str, update_data: NodeUpdate) -> CourseNode | None:
        """
        Update a course node

        Args:
            node_id: Node ID string (not database ID)
            update_data: Fields to update

        Returns:
            Updated node or None if not found
        """
        try:
            node = await self.get_node_by_node_id(node_id)

            if not node:
                return None

            # Update fields if provided
            if update_data.title is not None:
                node.title = update_data.title
            if update_data.description is not None:
                node.description = update_data.description
            if update_data.sequence is not None:
                node.sequence = update_data.sequence
            if update_data.guidePrompt is not None:
                # Store in timeline_config or as separate field if needed
                pass
            if update_data.estimatedMinutes is not None:
                # Store in metadata if needed
                pass
            if update_data.tags is not None:
                # Store in metadata if needed
                pass

            # Update parent_id if provided
            if update_data.parentId is not None:
                if update_data.parentId == "":
                    node.parent_id = None
                else:
                    parent_node = await self.get_node_by_node_id(update_data.parentId)
                    if parent_node:
                        node.parent_id = parent_node.id

            # Update timeline config if provided
            if update_data.timelineConfig is not None:
                timeline_config = {
                    "steps": [
                        {
                            "stepId": step.stepId,
                            "type": step.type,
                            **{k: v for k, v in step.model_dump().items()
                               if k not in ["stepId", "type"] and v is not None}
                        }
                        for step in update_data.timelineConfig.steps
                    ]
                }
                node.timeline_config = timeline_config

            # Update unlock condition if provided
            if update_data.unlockCondition is not None:
                node.unlock_condition = update_data.unlockCondition.model_dump()

            await self.db.commit()
            await self.db.refresh(node)
            return node

        except Exception as e:
            await self.db.rollback()
            raise e

    async def delete_node(self, node_id: str) -> bool:
        """
        Delete a course node

        Args:
            node_id: Node ID string (not database ID)

        Returns:
            True if deleted, False if not found
        """
        try:
            node = await self.get_node_by_node_id(node_id)

            if not node:
                return False

            # Check if node has children
            result = await self.db.execute(
                select(CourseNode).where(CourseNode.parent_id == node.id)
            )
            children = result.scalars().all()

            # Delete children first or set their parent_id to None
            for child in children:
                child.parent_id = None

            await self.db.delete(node)
            await self.db.commit()
            return True

        except Exception as e:
            await self.db.rollback()
            raise e

    async def add_node_to_course(self, course_id: int, node_config: PackageNodeConfig) -> CourseNode | None:
        """
        Add a single node to an existing course

        Args:
            course_id: ID of the course
            node_config: Node configuration

        Returns:
            Created node or None if course not found
        """
        try:
            # Check if course exists
            course = await self.get_course_by_id(course_id)
            if not course:
                return None

            # Check if node_id already exists
            existing = await self.get_node_by_node_id(node_config.nodeId)
            if existing:
                raise ValueError(f"Node with ID '{node_config.nodeId}' already exists")

            # Map node type
            type_map = {
                "video": NodeType.VIDEO,
                "simulator": NodeType.SIMULATOR,
                "quiz": NodeType.QUIZ,
                "reading": NodeType.READING,
                "practice": NodeType.PRACTICE
            }

            # Build timeline config
            timeline_config = None
            if node_config.timelineConfig:
                timeline_config = {
                    "steps": [
                        {
                            "stepId": step.stepId,
                            "type": step.type,
                            **{k: v for k, v in step.model_dump().items()
                               if k not in ["stepId", "type"] and v is not None}
                        }
                        for step in node_config.timelineConfig.steps
                    ]
                }

            # Build unlock condition
            unlock_condition = None
            if node_config.unlockCondition:
                unlock_condition = node_config.unlockCondition.model_dump()

            # Get parent_id if specified
            parent_id = None
            if node_config.parentId:
                parent_node = await self.get_node_by_node_id(node_config.parentId)
                if parent_node:
                    parent_id = parent_node.id

            # Create node
            node = CourseNode(
                course_id=course_id,
                parent_id=parent_id,
                node_id=node_config.nodeId,
                type=type_map.get(node_config.type, NodeType.READING),
                component_id=node_config.componentId,
                title=node_config.title,
                description=node_config.description,
                sequence=node_config.sequence,
                timeline_config=timeline_config,
                unlock_condition=unlock_condition
            )

            self.db.add(node)
            await self.db.commit()
            await self.db.refresh(node)
            return node

        except Exception as e:
            await self.db.rollback()
            raise e

