import json

class Mensagem:
    def __init__(self, id, clock, resource_name, msg_type, reply_port):
        self.id = id
        self.clock = clock
        self.resource_name = resource_name
        self.msg_type = msg_type
        self.reply_port = reply_port

    def get_id(self):
        return self.id

    def get_clock(self):
        return self.clock

    def get_resource_name(self):
        return self.resource_name

    def get_msg_type(self):
        return self.msg_type

    def get_reply_port(self):
        return self.reply_port

    def set_reply_port(self, reply_port):
        self.reply_port = reply_port

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

