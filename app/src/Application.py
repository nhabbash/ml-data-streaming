import json
from src.Sender import Sender
from src.Receiver import Receiver

class Application:
    def __init__(self):
        self.broker = None
        self.sender = None
        self.receiver = None
        self.config_paths = {}
    
    def _get_conf(self, filename):
        with open(filename, 'r') as f:
            conf = json.load(f)
        return conf

    def setup(self, broker, config_path=None):
        self.broker = broker

        if broker not in self.config_paths:
            self.config_paths[broker] = config_path

        receiver_file = self.config_paths[broker]+"/receiver.json"
        sender_file = self.config_paths[broker]+"/sender.json"

        receiver_conf = self._get_conf(receiver_file)
        sender_conf = self._get_conf(sender_file)
        
        self.receiver = Receiver(conf=receiver_conf, _from=self.broker)
        self.sender = Sender(conf=sender_conf, to=self.broker)
            
        # Broker API differences handled here
        if broker == "kafka":
            admin_file = self.config_paths[broker]+"/admin.json"
            admin_conf = self._get_conf(admin_file)
            self.sender._sender._init_admin_config(conf=admin_conf)
        elif broker == "pubsub":
            pass
        else:
            raise Exception("Non-supported broker")
