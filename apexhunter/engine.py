import logging
from .parser import PlaybookParser
from .loader import DataLoader
from .executor import QueryExecutor
from .llm import LLMWrapper
from .enricher import TIEnricher

logger = logging.getLogger(__name__)

class AutonomousEngine:
    """Core engine with TI enrichment and variable context."""
    def __init__(self, playbook_path: str, data_dir: str, model: str = "llama3"):
        self.playbook = PlaybookParser(playbook_path).parse()
        self.loader = DataLoader(data_dir)
        self.conn = self.loader.load_all()
        self.executor = QueryExecutor(self.conn)
        self.llm = LLMWrapper(model=self.playbook.get('global', {}).get('llm_model', model))
        self.enricher = TIEnricher(ti_dir=self.playbook.get('global', {}).get('ti_dir', 'intel'))
        self.results = []
        self.context = {} # Storage for step-to-step variables

    def _get_schema(self) -> str:
        """Fetch the current DuckDB schema for LLM context."""
        try:
            res = self.conn.execute("SELECT table_name, column_name, data_type FROM information_schema.columns").fetchdf()
            return res.to_string()
        except: return "Schema unavailable"

    def run(self):
        """Executes playbook steps iteratively."""
        steps = {step['id']: step for step in self.playbook.get('steps', [])}
        if not steps:
            return []

        current_step_id = self.playbook['steps'][0]['id']
        
        while current_step_id and current_step_id in steps:
            step = steps[current_step_id]
            logger.info(f"Executing step: {step['id']}")
            
            # 1. Prepare Query (Agentic or Static)
            query_type = step.get('query_type', 'sql')
            query = step.get('query', '')

            if query_type == "agentic":
                logger.info("Generating agentic query...")
                schema = self._get_schema()
                hypothesis = step.get('hypothesis', self.playbook.get('hypothesis', ''))
                query = self.llm.generate_query(hypothesis, schema)
                logger.info(f"Generated Query: {query}")

            # Context replacement
            for var, val in self.context.items():
                query = query.replace(f"{{{{{var}}}}}", str(val))

            # 2. Execute
            hits = []
            if query and (query_type == 'sql' or query_type == 'agentic'):
                 try:
                    view_name = step['id']
                    self.conn.execute(f"CREATE OR REPLACE VIEW {view_name} AS {query}")
                    hits = self.executor.execute(f"SELECT * FROM {view_name}", query_type="sql")
                 except Exception as e:
                    logger.error(f"Step {step['id']} query failed: {e}")
            else:
                 hits = self.executor.execute(query, query_type=query_type)
            
            # Enrichment
            enrich_keys = step.get('enrich_keys', [])
            if hits and enrich_keys:
                 hits = self.enricher.enrich_results(hits, enrich_keys)

            # Store variables if specified (e.g., save 'src_ip' from first hit as 'target_ip')
            if hits and 'output_vars' in step:
                 for var_name, source_col in step['output_vars'].items():
                      self.context[var_name] = hits[0].get(source_col)

            # Logic same as before... (Condition evaluation, LLM reasoning)
            condition = step.get('condition', '')
            condition_met = len(hits) > 0 # Simplified default
            if condition.startswith("count >"):
                 try:
                    thresh = int(condition.split(">")[1].strip())
                    condition_met = len(hits) > thresh
                 except: pass

            step_result = {"step_id": step['id'], "description": step['description'], "hits_count": len(hits), "hits": hits, "llm_analysis": None}

            llm_suspicious = True
            if condition_met:
                llm_prompt = step.get('llm_instruction')
                if llm_prompt:
                    analysis = self.llm.analyze(llm_prompt, hits)
                    step_result["llm_analysis"] = analysis
                    llm_suspicious = analysis.get('is_suspicious', False)
                
            self.results.append(step_result)
            current_step_id = step.get('next_on_hit') if (condition_met and llm_suspicious) else step.get('next_on_miss')

        return self.results
