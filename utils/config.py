import json

class Config():
    def __init__(self):
        with open("config.json","r") as f:
            self.config = json.load(f)

    def get_config(self):
        return self.config
    
    def write_config(self, conf):
        with open("config.json","w") as f:
            json.dump(conf, f)