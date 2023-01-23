import json

class Mensagem:
    def __init__(self, id, clock, msg, type, reply_port):
        self.id = id
        self.clock = clock
        self.msg = msg
        self.type = type
        self.reply_port = reply_port

    def get_clock(self):
        return self.clock

    def get_id(self):
        return self.id

    def get_msg(self):
        return self.msg

    def get_type(self):
        return self.type

    def set_type(self, n):
        self.type = n

    def get_reply_port(self):
        return self.reply_port

    def set_reply_port(self, reply_port):
        self.reply_port = reply_port

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)