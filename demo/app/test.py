import unittest
from unittest.mock import MagicMock
import Producer
class TestProducer(unittest.TestCase):

    @patch('kafka.KafkaProducer')
    def test_produce_message(KafkaProducerMock):
        publishToKafkaTopic('data')
        KafkaProducerMock.send.assert_called

    @patch('kafka.KafkaProducer.send')
    def test_vertify_produce_message(KafkaProducerMock):
        publishToKafkaTopic({'key1':'value1', 'key2': 'value2'})
        args = KafkaProducerMock.call_args
        assert(args[0] == (TOPIC_NAME,))
        assert(args[2] == {'value': {'key1':'value1', 'key2': 'value2'}})


if __name__ == "__main__":
    unittest.main()