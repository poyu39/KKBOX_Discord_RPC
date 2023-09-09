import yaml, os, base64

WORKDIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    def __init__(self):
        with open(f'{WORKDIR}/storage/config.yml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        self.CLINET_ID = self.config['client_id']
        
        with open(f'{WORKDIR}/storage/icon_128.png', 'rb') as f:
            img_data = f.read()
            self.ICON = base64.b64encode(img_data)

CONFIG = Config()