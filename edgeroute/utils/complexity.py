import re
from typing import Dict, Any

class ComplexityScorer:
    def __init__(self):
        self.reasoning_keywords = [
            "analyze", "compare", "design", "architecture", "proof", "derive",
            "evaluate", "critique", "plan", "strategy", "synthesis", "comprehensive"
        ]

    def estimate_tokens(self, text: str) -> int:
        # Simple heuristic: ~4 chars per token
        return len(text) // 4

    def count_keywords(self, text: str) -> int:
        count = 0
        text_lower = text.lower()
        for kw in self.reasoning_keywords:
            if kw in text_lower:
                count += 1
        return count

    def calculate_complexity(self, prompt: str) -> Dict[str, Any]:
        """
        Calculates complexity score (1-10) and other metrics.
        """
        tokens = self.estimate_tokens(prompt)
        instruction_count = len(re.findall(r'[.!?\n]', prompt)) # Rough sentence/instruction count
        keyword_count = self.count_keywords(prompt)
        
        # Base score
        score = 1
        
        # Adjust based on length
        if tokens > 1000:
            score += 3
        elif tokens > 500:
            score += 2
        elif tokens > 200:
            score += 1
            
        # Adjust based on keywords
        score += min(keyword_count * 2, 6) # Cap at 6, +2 per keyword
        
        # Adjust based on structure/instructions
        if instruction_count > 5:
            score += 2
        elif instruction_count > 2:
            score += 1

        # Cap at 10
        score = min(score, 10)
        
        # Determine reasoning depth
        if score >= 8:
            depth = "high"
        elif score >= 5:
            depth = "medium"
        else:
            depth = "low"

        return {
            "complexity_score": score,
            "estimated_tokens": tokens,
            "reasoning_depth": depth,
            "instruction_count": instruction_count,
            "keyword_match_count": keyword_count
        }

if __name__ == "__main__":
    scorer = ComplexityScorer()
    sample = "Design a distributed consensus protocol for a high-frequency trading platform."
    print(scorer.calculate_complexity(sample))
