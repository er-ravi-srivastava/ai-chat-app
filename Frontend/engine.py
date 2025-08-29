from typing import List, Dict, Any, Tuple
import re, yaml, os

RULES_PATH = os.path.join(os.path.dirname(__file__), "symptom_rules.yaml")

class SymptomEngine:
    def __init__(self):
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f)
        self.conditions = rules.get("conditions", [])
        self.red_flags = rules.get("red_flags", [])
        self.keyword_norm = rules.get("keyword_normalization", {})
        self.stopwords = set(rules.get("stopwords", []))

    def normalize_symptom(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r"[^a-z\\s]", " ", text)
        tokens = [t for t in text.split() if t and t not in self.stopwords]
        mapped = [self.keyword_norm.get(t, t) for t in tokens]
        return mapped

    def extract_symptoms(self, symptom_list: List[str], notes: str) -> List[str]:
        tokens = []
        for s in symptom_list:
            tokens += self.normalize_symptom(s)
        if notes:
            tokens += self.normalize_symptom(notes)
        return list(set(tokens))  # unique symptoms

    def score_condition(self, cond: Dict[str, Any], tokens: List[str], age: int, duration_days: int) -> float:
        score = 0.0
        if cond.get("keywords"):
            hits = sum(1 for k in cond["keywords"] if k in tokens)
            score += hits * cond.get("weights", {}).get("keyword", 1.0)
        if cond.get("negative_keywords"):
            neg_hits = sum(1 for k in cond["negative_keywords"] if k in tokens)
            score -= neg_hits * cond.get("weights", {}).get("negative", 1.0)
        if cond.get("age_band"):
            lo, hi = cond["age_band"]
            if lo <= age <= hi:
                score += cond.get("weights", {}).get("age", 0.5)
        return max(0.0, score)

    def check_red_flags(self, tokens: List[str], age: int) -> Tuple[bool, List[str]]:
        reasons = []
        urgent = False
        for rf in self.red_flags:
            if any(k in tokens for k in rf["keywords"]):
                urgent = True
                reasons.append(rf["message"])
        if age <= 1 or age >= 75:
            reasons.append("Age at higher risk. Please consult a doctor.")
        return urgent, reasons

    def assess(self, age: int, sex: str, symptoms: List[str], duration_days: int, notes: str) -> Dict[str, Any]:
        tokens = self.extract_symptoms(symptoms, notes)
        urgent, reasons = self.check_red_flags(tokens, age)

        scored = []
        for c in self.conditions:
            s = self.score_condition(c, tokens, age, duration_days or 0)
            if s > 0:
                scored.append({"condition": c["name"], "score": round(s, 2)})
        scored.sort(key=lambda x: x["score"], reverse=True)

        triage_level = "urgent" if urgent else "routine"
        if urgent:
            reasons.append("If symptoms worsen, seek emergency care.")

        advice = [
            "This is a demo, not medical advice.",
            "Always consult a qualified doctor.",
            "If symptoms are severe, seek urgent care."
        ]

        return {
            "triage_level": triage_level,
            "triage_reason": reasons,
            "likely_conditions": scored[:5],
            "advice": advice
        }
