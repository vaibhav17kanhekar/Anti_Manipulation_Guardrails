"""
Data loading and saving utilities
"""

import json
import yaml
import pickle
import csv
from pathlib import Path
from typing import Dict, List, Any, Union
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: Union[str, Path]) -> Dict:
    """
    Load configuration from YAML or JSON file
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
        raise

def save_config(config: Dict, output_path: Union[str, Path]):
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        output_path: Output file path
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if output_path.suffix.lower() in ['.yaml', '.yml']:
            with open(output_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        elif output_path.suffix.lower() == '.json':
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
        else:
            raise ValueError(f"Unsupported config file format: {output_path.suffix}")
        
        logger.info(f"Saved configuration to {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to save configuration to {output_path}: {str(e)}")
        raise

def load_prompts(file_path: Union[str, Path]) -> List[Dict]:
    """
    Load prompts from JSON file
    
    Args:
        file_path: Path to prompts file
    
    Returns:
        List of prompt dictionaries
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.warning(f"Prompts file not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r') as f:
            prompts = json.load(f)
        
        logger.info(f"Loaded {len(prompts)} prompts from {file_path}")
        return prompts
        
    except Exception as e:
        logger.error(f"Failed to load prompts from {file_path}: {str(e)}")
        return []

def save_prompts(prompts: List[Dict], file_path: Union[str, Path]):
    """
    Save prompts to JSON file
    
    Args:
        prompts: List of prompt dictionaries
        file_path: Output file path
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(prompts, f, indent=2)
        
        logger.info(f"Saved {len(prompts)} prompts to {file_path}")
        
    except Exception as e:
        logger.error(f"Failed to save prompts to {file_path}: {str(e)}")
        raise

def load_results(file_path: Union[str, Path]) -> List[Dict]:
    """
    Load experiment results from JSON file
    
    Args:
        file_path: Path to results file
    
    Returns:
        List of result dictionaries
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.warning(f"Results file not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r') as f:
            results = json.load(f)
        
        logger.info(f"Loaded {len(results)} results from {file_path}")
        return results
        
    except Exception as e:
        logger.error(f"Failed to load results from {file_path}: {str(e)}")
        return []

def save_results(results: List[Dict], file_path: Union[str, Path], 
                compress: bool = False):
    """
    Save experiment results to file
    
    Args:
        results: List of result dictionaries
        file_path: Output file path
        compress: Whether to compress the file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if compress:
            # Save as compressed pickle
            with open(file_path.with_suffix('.pkl.gz'), 'wb') as f:
                import gzip
                import pickle
                pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            # Save as JSON
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
        
        logger.info(f"Saved {len(results)} results to {file_path}")
        
    except Exception as e:
        logger.error(f"Failed to save results to {file_path}: {str(e)}")
        raise

def results_to_dataframe(results: List[Dict]) -> pd.DataFrame:
    """
    Convert results to pandas DataFrame for analysis
    
    Args:
        results: List of result dictionaries
    
    Returns:
        pandas DataFrame
    """
    if not results:
        logger.warning("No results to convert to DataFrame")
        return pd.DataFrame()
    
    try:
        # Flatten nested dictionaries
        flattened_results = []
        for result in results:
            flat_result = {
                'experiment_id': result.get('experiment_id', ''),
                'timestamp': result.get('timestamp', ''),
                'model': result.get('model', ''),
                'defense_strategy': result.get('defense_strategy', ''),
                'prompt_id': result.get('prompt_id', ''),
                'prompt': result.get('prompt', ''),
                'response': result.get('response', ''),
                'response_time': result.get('response_time', 0),
                'is_safe': result.get('safety_evaluation', {}).get('is_safe', False),
                'safety_score': result.get('safety_evaluation', {}).get('safety_score', 0),
                'refusal_detected': result.get('safety_evaluation', {}).get('refusal_detected', False),
                'coherence_score': result.get('quality_evaluation', {}).get('coherence_score', 0),
                'specificity_score': result.get('quality_evaluation', {}).get('specificity_score', 0),
                'word_count': result.get('quality_evaluation', {}).get('word_count', 0),
                'input_tokens': result.get('model_metadata', {}).get('input_tokens', 0),
                'output_tokens': result.get('model_metadata', {}).get('output_tokens', 0),
                'total_tokens': result.get('model_metadata', {}).get('total_tokens', 0),
                'manipulation_type': result.get('prompt_metadata', {}).get('manipulation_type', ''),
                'manipulation_level': result.get('prompt_metadata', {}).get('manipulation_level', ''),
                'target_task': result.get('prompt_metadata', {}).get('target_task', ''),
                'original_intent': result.get('prompt_metadata', {}).get('original_intent', '')
            }
            flattened_results.append(flat_result)
        
        df = pd.DataFrame(flattened_results)
        logger.info(f"Converted {len(df)} results to DataFrame with {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Failed to convert results to DataFrame: {str(e)}")
        raise

def save_dataframe(df: pd.DataFrame, file_path: Union[str, Path], 
                  format: str = 'csv'):
    """
    Save DataFrame to file
    
    Args:
        df: pandas DataFrame
        file_path: Output file path
        format: Output format ('csv', 'excel', 'parquet')
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if format == 'csv':
            df.to_csv(file_path, index=False)
        elif format == 'excel':
            df.to_excel(file_path, index=False)
        elif format == 'parquet':
            df.to_parquet(file_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Saved DataFrame with {len(df)} rows to {file_path}")
        
    except Exception as e:
        logger.error(f"Failed to save DataFrame to {file_path}: {str(e)}")
        raise

def load_dataset(dataset_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load dataset from various formats
    
    Args:
        dataset_path: Path to dataset file
    
    Returns:
        Dataset dictionary
    """
    dataset_path = Path(dataset_path)
    
    if not dataset_path.exists():
        logger.error(f"Dataset file not found: {dataset_path}")
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    
    try:
        if dataset_path.suffix == '.json':
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
        elif dataset_path.suffix == '.csv':
            dataset = pd.read_csv(dataset_path).to_dict('records')
        elif dataset_path.suffix in ['.xlsx', '.xls']:
            dataset = pd.read_excel(dataset_path).to_dict('records')
        elif dataset_path.suffix == '.pkl':
            with open(dataset_path, 'rb') as f:
                dataset = pickle.load(f)
        else:
            raise ValueError(f"Unsupported dataset format: {dataset_path.suffix}")
        
        logger.info(f"Loaded dataset from {dataset_path}")
        return dataset
        
    except Exception as e:
        logger.error(f"Failed to load dataset from {dataset_path}: {str(e)}")
        raise

def split_dataset(data: List[Dict], train_ratio: float = 0.7, 
                  val_ratio: float = 0.15, test_ratio: float = 0.15,
                  shuffle: bool = True, seed: int = 42) -> Dict[str, List[Dict]]:
    """
    Split dataset into train, validation, and test sets
    
    Args:
        data: List of data items
        train_ratio: Training set ratio
        val_ratio: Validation set ratio
        test_ratio: Test set ratio
        shuffle: Whether to shuffle the data
        seed: Random seed for shuffling
    
    Returns:
        Dictionary with train, val, test splits
    """
    import random
    
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
        raise ValueError("Ratios must sum to 1.0")
    
    if shuffle:
        random.seed(seed)
        random.shuffle(data)
    
    n = len(data)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    splits = {
        'train': data[:train_end],
        'val': data[train_end:val_end],
        'test': data[val_end:]
    }
    
    logger.info(f"Split dataset: {len(splits['train'])} train, "
                f"{len(splits['val'])} val, {len(splits['test'])} test")
    
    return splits

def export_to_csv(results: List[Dict], output_path: Union[str, Path]):
    """
    Export results to CSV file
    
    Args:
        results: List of result dictionaries
        output_path: Output CSV file path
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Flatten results for CSV export
        flattened = []
        for result in results:
            flat = {
                'experiment_id': result.get('experiment_id', ''),
                'model': result.get('model', ''),
                'defense_strategy': result.get('defense_strategy', ''),
                'prompt_id': result.get('prompt_id', ''),
                'prompt': result.get('prompt', ''),
                'response': result.get('response', ''),
                'response_time': result.get('response_time', 0),
                'is_safe': result.get('safety_evaluation', {}).get('is_safe', False),
                'safety_score': result.get('safety_evaluation', {}).get('safety_score', 0),
                'manipulation_type': result.get('prompt_metadata', {}).get('manipulation_type', ''),
                'manipulation_level': result.get('prompt_metadata', {}).get('manipulation_level', ''),
                'target_task': result.get('prompt_metadata', {}).get('target_task', '')
            }
            flattened.append(flat)
        
        # Write to CSV
        keys = flattened[0].keys() if flattened else []
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(flattened)
        
        logger.info(f"Exported {len(flattened)} results to CSV: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to export results to CSV: {str(e)}")
        raise