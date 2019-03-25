from typing import Dict, Optional, List, Any


class DBConnection(object):

    def __init__(self, data: Optional[Dict]=None):
        data = data or {}
        self.hosts: List[str] = data['hosts']
        self.params: Dict = {} if data.get('params') is None else data.get(
            'params')
        self.password: str = data['password']
        self.ports: List[int] = data['ports']
        self.schema: Optional[str] = data.get('schema')
        self.user: str = data['user']


class Connection(object):

    def __init__(self, data: Optional[Dict]=None):
        data = data or {}
        self.disabled: bool = False if data.get('disabled'
            ) is None else data.get('disabled')
        self.name: str = data['name']
        self.params: DBConnection = None if data['params'
            ] is None else DBConnection(data['params'])
        self.type: str = data['type']

