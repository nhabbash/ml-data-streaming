import json

class Message:
    """Message class.

        Attributes:
            key (str): Identifier
            value (str): Message payload
    """     
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return f'Message: {self.key}->{self.value}'

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def from_PS(cls, payload):
        payload = json.loads(payload.data)
        # Process output to message class
        msg = cls(key=payload["key"], value=payload["value"])
        return msg

    @classmethod
    def from_kafka(cls, payload):
        key = payload.key().decode("utf-8")
        value = payload.value().decode("utf-8")
        # Process output to Message class
        msg = cls(key=key, value=value)
        return msg