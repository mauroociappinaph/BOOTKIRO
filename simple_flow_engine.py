"""
Simple flow engine for testing purposes.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SimpleFlowEngine:
    """Simple flow engine for testing"""

    def __init__(self):
        """Initialize the simple flow engine"""
        self.flows = {}

    async def create_flow(self, flow_data: Dict[str, Any]) -> str:
        """Create a new flow"""
        flow_id = str(uuid.uuid4())
        flow_data['id'] = flow_id
        flow_data['created_at'] = datetime.now().isoformat()
        self.flows[flow_id] = flow_data
        logger.info(f"Created flow: {flow_data['name']}")
        return flow_id

    async def execute_flow(self, flow_id: str) -> Dict[str, Any]:
        """Execute a flow"""
        if flow_id not in self.flows:
            return {'success': False, 'error': 'Flow not found'}

        flow = self.flows[flow_id]
        logger.info(f"Executing flow: {flow['name']}")

        # Simple execution simulation
        result = {
            'success': True,
            'flow_id': flow_id,
            'executed_at': datetime.now().isoformat(),
            'actions_executed': len(flow.get('actions', []))
        }

        return result
