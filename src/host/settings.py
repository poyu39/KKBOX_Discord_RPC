import yaml, os

WORKDIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    def __init__(self):
        with open(f'{WORKDIR}/storage/config.yml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        self.CLINET_ID = self.config['client_id']

CONFIG = Config()