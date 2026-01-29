import unittest
from edgeroute.agents.router import RoutingDecisionAgent
from edgeroute.utils.complexity import ComplexityScorer

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = RoutingDecisionAgent()
        self.scorer = ComplexityScorer()

    def test_local_routing(self):
        analysis = {
            "complexity_score": 3,
            "estimated_tokens": 100,
            "reasoning_depth": "low",
            "task_type": "summary"
        }
        decision = self.router.decide(analysis)
        self.assertEqual(decision.route, "local")

    def test_cloud_routing_complexity(self):
        analysis = {
            "complexity_score": 8,
            "estimated_tokens": 100,
            "reasoning_depth": "medium",
            "task_type": "coding"
        }
        decision = self.router.decide(analysis)
        self.assertEqual(decision.route, "cloud")

    def test_cloud_routing_tokens(self):
        analysis = {
            "complexity_score": 3,
            "estimated_tokens": 2000,
            "reasoning_depth": "low",
            "task_type": "summary"
        }
        decision = self.router.decide(analysis)
        self.assertEqual(decision.route, "cloud")

    def test_cloud_routing_depth(self):
        analysis = {
            "complexity_score": 5,
            "estimated_tokens": 100,
            "reasoning_depth": "high",
            "task_type": "reasoning"
        }
        decision = self.router.decide(analysis)
        self.assertEqual(decision.route, "cloud")

class TestComplexity(unittest.TestCase):
    def setUp(self):
        self.scorer = ComplexityScorer()

    def test_simple_prompt(self):
        prompt = "Hello world"
        metrics = self.scorer.calculate_complexity(prompt)
        self.assertLess(metrics["complexity_score"], 4)
        self.assertEqual(metrics["reasoning_depth"], "low")

    def test_complex_prompt(self):
        prompt = "Design a distributed consensus protocol using Paxos, taking latency into account verify the proof."
        metrics = self.scorer.calculate_complexity(prompt)
        # Should detect keywords like Design, architecture (if present), proof.
        self.assertGreaterEqual(metrics["complexity_score"], 1)
        self.assertIn(metrics["reasoning_depth"], ["medium", "high"])

if __name__ == "__main__":
    unittest.main()
