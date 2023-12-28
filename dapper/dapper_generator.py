from dapper.sp_utils import SPUtils
from dapper.dapper_handler_generator import DapperHandlerGenerator
from dapper.dapper_request_generator import DapperRequestGenerator
from typing import Dict

from dapper.stored_procedure import StoredProcedure


class DapperGenerator:
    def __init__(self, sp_text: str):
        self.sp_text = sp_text

        sp = StoredProcedure(sp_text)

        self.sp_definition = sp.sp_definition
        self.sp_name = sp.sp_name
        self.sp_params_dict = sp.sp_params_dict
        self.sp_is_query = sp.get_sp_type() == 'query'

        self.request_generator = DapperRequestGenerator(sp)
        self.handler_generator = DapperHandlerGenerator(sp)

    def generate_request_class(self):
        return self.request_generator.generate()

    def generate_handler_class(self):
        return self.handler_generator.generate()
