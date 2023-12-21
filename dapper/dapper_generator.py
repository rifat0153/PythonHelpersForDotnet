from dapper.sp_utils import SPUtils
from dapper.dapper_handler_generator import DapperHandlerGenerator
from dapper.dapper_request_generator import DapperRequestGenerator
from typing import Dict


class DapperGenerator:
    def __init__(self, sp_text: str):
        self.sp_text = sp_text
        self.sp_name = SPUtils.retrive_sp_name(sp_text)
        self.sp_params_dict = SPUtils.retrive_sp_params(sp_text)

    def generate_request_class(self):
        return DapperRequestGenerator.generate(self.sp_name, self.sp_params_dict)
