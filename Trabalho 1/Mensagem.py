import json

class Mensagem:
    def __init__(self, clock, msg, id, is_ack, n_ack):
        self.clock = clock
        self.id = id
        self.msg = msg
        self.is_ack = is_ack
        self.n_ack = n_ack

    def get_clock(self):
        return self.clock

    def get_id(self):
        return self.id

    def get_is_ack(self):
        return self.is_ack

    def get_msg(self):
        return self.msg

    def get_n_ack(self):
        return self.n_ack

    def set_n_ack(self, n):
        self.n_ack = n

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
