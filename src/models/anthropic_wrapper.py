import anthropic
import time
from typing import Dict

class AnthropicWrapper:
    def __init__(self, api_key: str, model: str = "claude-2"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.rate_limit_delay = 1.0  # seconds
        
    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict:
        time.sleep(self.rate_limit_delay)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                'success': True,
                'content': response.content[0].text,
                'model': self.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'model': self.model
            }