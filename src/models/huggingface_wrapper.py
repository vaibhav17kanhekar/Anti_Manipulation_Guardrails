from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import Dict

class HuggingFaceWrapper:
    def __init__(self, api_key: str, model: str = "meta-llama/Llama-2-7b-chat-hf"):
        self.model_name = model
        self.tokenizer = AutoTokenizer.from_pretrained(model, token=api_key)
        self.model = AutoModelForCausalLM.from_pretrained(
            model,
            token=api_key,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto"
        )
        
    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict:
        try:
            prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"
            
            outputs = self.pipeline(
                prompt,
                max_new_tokens=1000,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                return_full_text=False
            )
            
            response = outputs[0]['generated_text']
            
            return {
                'success': True,
                'content': response,
                'model': self.model_name,
                'usage': {
                    # Note: Transformers doesn't provide token usage easily without manual calculation
                    'input_tokens': len(self.tokenizer.encode(prompt)),
                    'output_tokens': len(self.tokenizer.encode(response))
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'model': self.model_name
            }