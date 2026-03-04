import ollama
import logging
import json

logger = logging.getLogger(__name__)

class LLMWrapper:
    """Wrapper for local Ollama models."""
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.system_prompt = (
            "You are a senior threat hunter. Analyze only the provided data. "
            "Reason step-by-step. Output JSON exactly in this format: "
            "{\"reasoning\": \"...\", \"is_suspicious\": true/false, \"confidence\": 0-100, \"summary\": \"...\", \"recommended_next\": \"...\"}"
        )

    def analyze(self, prompt: str, data: list[dict]) -> dict:
        """Analyzes data using the local LLM with chunking/limits."""
        if not data:
            return {"reasoning": "No data to analyze", "is_suspicious": False, "confidence": 0, "summary": "Empty dataset", "recommended_next": "none"}

        # Senior design: Limit context data and ensure valid JSON before LLM call
        # We take first 10 and last 10 records if data is too large for better signal
        if len(data) > 20:
             data = data[:10] + [{"...": "skipping records"}] + data[-10:]

        serializable_data = []
        for row in data:
            new_row = {}
            for k, v in row.items():
                new_row[k] = v.isoformat() if hasattr(v, 'isoformat') else v
            serializable_data.append(new_row)

        context = json.dumps(serializable_data, indent=2)
        full_prompt = (
            f"Prompt: {prompt}\n\n"
            f"Instructions: {self.system_prompt}\n\n"
            f"Dataset (JSON):\n{context}\n\n"
            f"Focus: Identify patterns of malicious behavior. Be concise."
        )

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': full_prompt}
            ])
            content = response['message']['content']
            
            # Use regex or multi-strategy JSON extraction
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            return {
                "reasoning": content,
                "is_suspicious": "suspicious" in content.lower(),
                "confidence": 50 if "suspicious" in content.lower() else 0,
                "summary": "Partial analysis (non-JSON output)",
                "recommended_next": "unknown"
            }
        except Exception as e:
            logger.error(f"Ollama connection error: {e}. Check if service is running.")
            return {"error": str(e), "is_suspicious": False, "summary": f"Ollama failed: {e}"}

    def generate_query(self, hypothesis: str, tables_schema: str) -> str:
        """Asks the LLM to generate a SQL query based on a threat hypothesis."""
        prompt = (
            f"Hypothesis: {hypothesis}\n"
            f"Available Tables & Schema:\n{tables_schema}\n\n"
            "Task: Generate a single valid DuckDB SQL query to investigate this. "
            "IMPORTANT: Return ONLY the raw SQL code. No markdown, no comments, no explanations."
        )
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            content = response['message']['content'].strip()
            
            # Senior strategy: Extract only the SQL block using regex
            import re
            # Find the first 'SELECT' and everything until the end of that statement
            sql_match = re.search(r'(SELECT.*)', content, re.DOTALL | re.IGNORECASE)
            if sql_match:
                sql = sql_match.group(1).split(';')[0].strip()
                # Remove any markdown backticks if present
                sql = sql.replace("```sql", "").replace("```", "").strip()
                return sql
            
            return content
        except Exception as e:
            logger.error(f"Failed to generate agentic query: {e}")
            return ""
