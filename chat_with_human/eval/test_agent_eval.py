"""
ADK Agent Evaluation Tests
"""

import pytest
import os
from dotenv import load_dotenv
from google.adk.evaluation.agent_evaluator import AgentEvaluator

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
if not os.getenv('GOOGLE_API_KEY'):
    raise ValueError("GOOGLE_API_KEY not found in .env file")


@pytest.mark.asyncio
async def test_event_sponsor_basic():
    """Test basic routing and tool usage"""
    await AgentEvaluator.evaluate(
        agent_module="chat_with_human",
        eval_dataset_file_path_or_dir="chat_with_human/eval/event_sponsor_basic.test.json"
    )