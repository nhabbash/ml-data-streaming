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