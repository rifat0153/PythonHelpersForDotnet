import os
from dapper.dapper_generator import DapperGenerator
from dapper.sp_utils import SPUtils
from dapper.dapper_handler_generator import DapperHandlerGenerator
from dapper.dapper_request_generator import DapperRequestGenerator


class DapperFileGenerator:
    def generate(self, folder_path: str, root_namespace: str):
        """
            Read all the sql file in the given folder and generate the request and handler classes for them.
        """
        files = os.listdir(folder_path)
        files_sql = filter(lambda file: file.endswith('.sql'), files)

        for file in files_sql:
            # read the contents of the file
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r') as file:
                sp_text = file.read()
                dapper_generator = DapperGenerator(sp_text)

                namespace = f"{root_namespace}.{folder_path}"
                dapper_generator.generate(folder_path, root_namespace)
