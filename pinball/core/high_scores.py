import json
from datetime import datetime
from pathlib import Path
import os

class HighScoreManager:
    def __init__(self, filepath="high_scores.json", max_entries=3):
        temp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "scores", "high_scores.json"))
        self.filepath = Path(temp_path)
        # print(f"[DEBUG] HighScoreManager initialized with file: {self.filepath}")
        if not self.filepath.exists():
            print(f"[DEBUG] HighScoreManager file does not exist, creating: {self.filepath}")
        else:
            print(f"[DEBUG] HighScoreManager file exists: {self.filepath}")
        self.max_entries = max_entries
        self.scores = self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.scores, f, indent=2)

    def is_high_score(self, score: int) -> bool:
        if len(self.scores) < self.max_entries:
            return True
        return score > min(entry["score"] for entry in self.scores)

    def add_score(self, score: int, name: str = "AAA"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.scores.append({"name": name, "score": score, "timestamp": timestamp})
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:self.max_entries]
        self._save()

    def get_scores(self):
        return self.scores
