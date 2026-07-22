import openai
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OpenAIWrapper:
    """Wrapper for OpenAI API calls with rate limiting and error handling"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.rate_limit_delay = 0.5  # Delay between requests in seconds
        
    def generate_response(self, system_prompt: str, user_prompt: str,
                         temperature: float = 0.7, max_tokens: int = 1000) -> Dict:
        """Generate a response from the model"""
        
        time.sleep(self.rate_limit_delay)  # Rate limiting
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'model': self.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
        except openai.RateLimitError:
            logger.warning(f"Rate limit hit for {self.model}, retrying in 5 seconds...")
            time.sleep(5)
            return self.generate_response(system_prompt, user_prompt, temperature, max_tokens)
            
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'model': self.model
            }
    
    def batch_generate(self, prompts: List[Dict], 
                       system_prompt: str) -> List[Dict]:
        """Generate responses for multiple prompts"""
        
        results = []
        for i, prompt_data in enumerate(prompts):
            logger.info(f"Processing prompt {i+1}/{len(prompts)} with {self.model}")
            
            result = self.generate_response(
                system_prompt=system_prompt,
                user_prompt=prompt_data['prompt'],
                temperature=0.7
            )
            
            result['prompt_id'] = prompt_data['id']
            result['metadata'] = prompt_data['metadata']
            results.append(result)
        
        return results