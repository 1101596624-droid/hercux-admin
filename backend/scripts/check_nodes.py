"""
Check what nodes exist in the database
"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.models.models import CourseNode


async def check_nodes():
    """Check all nodes in database"""
    async with AsyncSessionLocal() as session:
        # Get all nodes
        result = await session.execute(select(CourseNode))
        nodes = result.scalars().all()

        print(f"Total nodes: {len(nodes)}\n")

        for node in nodes:
            print(f"ID: {node.id}")
            print(f"  node_id: {node.node_id}")
            print(f"  title: {node.title}")
            print(f"  type: {node.type}")
            print(f"  component_id: {node.component_id}")

            # Check timeline_config
            config = node.timeline_config
            if config:
                steps = config.get("steps", [])
                print(f"  steps count: {len(steps)}")
                for i, step in enumerate(steps):
                    step_type = step.get("type", "unknown")
                    print(f"    step {i}: type={step_type}")
                    if step_type == "simulator":
                        print(f"      simulatorId: {step.get('simulatorId')}")
                        print(f"      has simulator_spec: {'simulator_spec' in step}")
            else:
                print(f"  timeline_config: None")
            print()


async def main():
    print("Checking database nodes...\n")
    await check_nodes()


if __name__ == "__main__":
    asyncio.run(main())
