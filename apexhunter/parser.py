import yaml
import logging

logger = logging.getLogger(__name__)

class PlaybookParser:
    """Parses and validates ApexHunter playbooks."""
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self) -> dict:
        """Loads playbook securely and validates schema."""
        try:
            with open(self.filepath, 'r') as f:
                playbook = yaml.safe_load(f)
            self._validate(playbook)
            return playbook
        except Exception as e:
            logger.error(f"Failed to parse playbook: {e}")
            raise

    def _validate(self, playbook: dict):
        """Strict validation of the playbook schema."""
        required_top_level = ['name', 'hypothesis', 'steps']
        for field in required_top_level:
            if field not in playbook:
                raise ValueError(f"Playbook missing required top-level field: '{field}'")
        
        if not isinstance(playbook['steps'], list) or len(playbook['steps']) == 0:
            raise ValueError("Playbook must contain a non-empty list of 'steps'")

        step_ids = set()
        for i, step in enumerate(playbook['steps']):
            step_id = step.get('id')
            if not step_id:
                raise ValueError(f"Step {i} is missing an 'id'")
            if step_id in step_ids:
                raise ValueError(f"Duplicate step ID found: '{step_id}'")
            step_ids.add(step_id)

            if 'query' not in step and step.get('query_type') != 'agentic':
                raise ValueError(f"Step '{step_id}' is missing a 'query'")
            if 'description' not in step:
                raise ValueError(f"Step '{step_id}' is missing a 'description'")
            
            # Check chaining references
            for link in ['next_on_hit', 'next_on_miss']:
                target = step.get(link)
                if target and target not in [s.get('id') for s in playbook['steps']]:
                    # We'll allow null, but if a string is provided it must exist
                    if target != "null" and target is not None:
                         logger.warning(f"Step '{step_id}' references non-existent {link}: '{target}'")
