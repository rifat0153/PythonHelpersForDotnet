from typing import Dict, Any

class DapperHandlerGenerator:
    def __init__(self, dapper_handler):
        self.dapper_handler = dapper_handler

    # strongly type the params_dict
    def generate(params_dict: Dict[str, str]) -> str:
        return "dapper_handler_dummy"
