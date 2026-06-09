import os
import json
import time
import uuid
from typing import List, Dict, Any

class ConversationStore:
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "memory", "history.json")
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Load or initialize database file
        if not os.path.exists(self.db_path):
            self._write_db({})
            
    def _read_db(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading history.json: {e}")
        return {}
        
    def _write_db(self, data: Dict[str, Any]):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing history.json: {e}")

    def save_generation(
        self,
        prompt: str,
        industry: str,
        ba_output: str,
        pm_output: str,
        qa_output: str,
        final_prd: str,
        project_id: str = None
    ) -> str:
        """
        Saves a generation run persistently to the local JSON file.
        """
        if not project_id:
            project_id = str(uuid.uuid4())
            
        timestamp = time.time()
        db = self._read_db()
        
        db[project_id] = {
            "project_id": project_id,
            "prompt": prompt,
            "industry": industry,
            "timestamp": timestamp,
            "ba": ba_output,
            "pm": pm_output,
            "qa": qa_output,
            "final": final_prd
        }
        
        self._write_db(db)
        return project_id

    def list_generations(self) -> List[Dict[str, Any]]:
        """
        Lists historical generations sorted by timestamp descending.
        """
        db = self._read_db()
        generations = [
            {
                "project_id": k,
                "prompt": v["prompt"],
                "industry": v["industry"],
                "timestamp": v["timestamp"]
            }
            for k, v in db.items()
        ]
        generations.sort(key=lambda x: x["timestamp"], reverse=True)
        return generations

    def get_generation(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieves a specific generation session.
        """
        db = self._read_db()
        return db.get(project_id, {})
