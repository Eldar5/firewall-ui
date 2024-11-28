import unittest
from src.models.rule import Rule, Protocol, Action, Direction

class TestRuleModel(unittest.TestCase):
    def test_rule_creation(self):
        rule = Rule(
            id=1,
            source_address="192.168.1.0/24",
            source_port=80,
            destination_address="10.0.0.1",
            destination_port=443,
            protocol=Protocol.TCP,
            action=Action.ACCEPT,
            direction=Direction.INBOUND,
            description="Test rule"
        )
        
        self.assertEqual(rule.id, 1)
        self.assertEqual(rule.source_address, "192.168.1.0/24")
        self.assertEqual(rule.source_port, 80)
        self.assertEqual(rule.destination_address, "10.0.0.1")
        self.assertEqual(rule.destination_port, 443)
        self.assertEqual(rule.protocol, Protocol.TCP)
        self.assertEqual(rule.action, Action.ACCEPT)
        self.assertEqual(rule.direction, Direction.INBOUND)
        self.assertEqual(rule.description, "Test rule")

    def test_rule_validation(self):
        valid_rule = Rule(
            id=1,
            source_address="192.168.1.0/24",
            source_port=80,
            destination_address="10.0.0.1",
            destination_port=443,
            protocol=Protocol.TCP,
            action=Action.ACCEPT,
            direction=Direction.INBOUND
        )
        self.assertTrue(valid_rule.validate())

        invalid_rule = Rule(
            id=1,
            source_address="invalid_ip",
            source_port=80,
            destination_address="10.0.0.1",
            destination_port=443,
            protocol=Protocol.TCP,
            action=Action.ACCEPT,
            direction=Direction.INBOUND
        )
        with self.assertRaises(ValueError):
            invalid_rule.validate()

    def test_rule_to_dict(self):
        rule = Rule(
            id=1,
            source_address="192.168.1.0/24",
            source_port=80,
            destination_address="10.0.0.1",
            destination_port=443,
            protocol=Protocol.TCP,
            action=Action.ACCEPT,
            direction=Direction.INBOUND,
            description="Test rule"
        )
        rule_dict = rule.to_dict()
        
        self.assertIsInstance(rule_dict, dict)
        self.assertEqual(rule_dict['id'], 1)
        self.assertEqual(rule_dict['source_address'], "192.168.1.0/24")
        self.assertEqual(rule_dict['source_port'], 80)
        self.assertEqual(rule_dict['destination_address'], "10.0.0.1")
        self.assertEqual(rule_dict['destination_port'], 443)
        self.assertEqual(rule_dict['protocol'], "TCP")
        self.assertEqual(rule_dict['action'], "ACCEPT")
        self.assertEqual(rule_dict['direction'], "INBOUND")
        self.assertEqual(rule_dict['description'], "Test rule")

if __name__ == '__main__':
    unittest.main()