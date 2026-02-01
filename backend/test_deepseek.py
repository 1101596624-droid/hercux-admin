import asyncio
import os
from app.services.deepseek_service import get_deepseek_service, Message
from app.core.config import settings

# 设置 API key
os.environ['DEEPSEEK_API_KEY'] = settings.DEEPSEEK_API_KEY

async def test():
    service = get_deepseek_service()
    result = await service.generate_tutor_response(
        user_message='你好',
        context={
            'node': {'id': 1, 'title': 'Test', 'learning_objectives': []},
            'ai_tutor_config': {},
            'current_layer': 'L1',
            'progress': {}
        },
        conversation_history=[]
    )
    print(f'Result: {result[:200]}')

asyncio.run(test())
