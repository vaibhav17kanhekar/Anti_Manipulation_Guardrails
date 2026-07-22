import yaml
import json
import logging
from typing import Dict, List, Any
from pathlib import Path

from src.attack_generator import AttackGenerator
from src.defense_strategies import DefenseStrategies
from src.models.openai_wrapper import OpenAIWrapper
from src.models.anthropic_wrapper import AnthropicWrapper
from src.models.huggingface_wrapper import HuggingFaceWrapper
from src.evaluator import ResponseEvaluator
from src.utils.logger import setup_logger
from src.utils.data_loader import load_prompts

class ExperimentRunner:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.logger = setup_logger(self.config['logging']['level'], self.config['logging']['file'])
        
        # Initialize components
        self.attack_generator = AttackGenerator()
        self.defense_strategies = DefenseStrategies()
        self.evaluator = ResponseEvaluator()
        
        # Initialize models
        self.models = self._initialize_models()
        
    def _initialize_models(self) -> Dict[str, Any]:
        models = {}
        for model_config in self.config['models']:
            if model_config['enabled']:
                if model_config['provider'] == 'openai':
                    models[model_config['name']] = OpenAIWrapper(api_key=self.config['api_keys']['openai'], model=model_config['name'])
                elif model_config['provider'] == 'anthropic':
                    models[model_config['name']] = AnthropicWrapper(api_key=self.config['api_keys']['anthropic'], model=model_config['name'])
                elif model_config['provider'] == 'huggingface':
                    models[model_config['name']] = HuggingFaceWrapper(api_key=self.config['api_keys']['huggingface'], model=model_config['name'])
        return models
    
    def run(self):
        self.logger.info("Starting experiment")
        
        # Step 1: Load or generate attack prompts
        attack_prompts = self._load_attack_prompts()
        
        # Step 2: Run experiments for each model, defense, and prompt
        results = []
        for model_name, model in self.models.items():
            for defense in self.config['defense_strategies']:
                for prompt in attack_prompts:
                    result = self._run_single_experiment(model, defense, prompt)
                    results.append(result)
        
        # Step 3: Evaluate results
        evaluation = self.evaluator.evaluate_all(results)
        
        # Step 4: Save results
        self._save_results(results, evaluation)
        
        self.logger.info("Experiment completed")
        
    def _load_attack_prompts(self) -> List[Dict]:
        # If attack prompts file exists, load it, else generate new ones
        attack_prompts_path = Path(self.config['data_paths']['attack_prompts'])
        if attack_prompts_path.exists():
            with open(attack_prompts_path, 'r') as f:
                return json.load(f)
        else:
            # Generate attack prompts
            base_queries = [...]  # You would have a list of base queries
            attacks = self.attack_generator.generate_attack_dataset(base_queries, self.config['attack_prompts']['count_per_type'])
            attack_prompts = []
            for attack in attacks:
                attack_prompts.append({
                    'id': attack.id,
                    'prompt': attack.prompt,
                    'metadata': {
                        'manipulation_type': attack.manipulation_type,
                        'manipulation_level': attack.manipulation_level,
                        'target_task': attack.target_task,
                        'original_intent': attack.original_intent
                    }
                })
            # Save the generated prompts
            with open(attack_prompts_path, 'w') as f:
                json.dump(attack_prompts, f, indent=2)
            return attack_prompts
    
    def _run_single_experiment(self, model, defense: str, prompt: Dict) -> Dict:
        self.logger.debug(f"Running experiment for model {model.model_name}, defense {defense}, prompt {prompt['id']}")
        
        # Prepare the system prompt based on defense
        system_prompt = self.defense_strategies.prepare_system_prompt(defense)
        
        # If defense is 'shield_prompt', we use a different method
        if defense == 'shield_prompt':
            user_prompt = self.defense_strategies.shield_prompt_technique(prompt['prompt'], system_prompt)
            system_prompt = "You are a helpful AI assistant."
        else:
            user_prompt = prompt['prompt']
        
        # Generate response
        response = model.generate_response(system_prompt, user_prompt)
        
        return {
            'model': model.model_name,
            'defense': defense,
            'prompt_id': prompt['id'],
            'prompt': prompt['prompt'],
            'response': response,
            'metadata': prompt['metadata']
        }
    
    def _save_results(self, results: List[Dict], evaluation: Dict):
        output_dir = Path(self.config['output']['dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        with open(output_dir / 'evaluation.json', 'w') as f:
            json.dump(evaluation, f, indent=2)
        
        self.logger.info(f"Results saved to {output_dir}")

if __name__ == "__main__":
    runner = ExperimentRunner("config/experiment_config.yaml")
    runner.run()