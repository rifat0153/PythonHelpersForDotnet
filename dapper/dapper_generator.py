import os
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

    def generate(self, folder_path: str, root_namespace: str):
        """
        Generates the request and handler classes for all the stored procedures in the given folder.
        Create a folder with the namespace name and generate the classes there.
        Each stored procedure will have its own folder with the name of the stored procedure.
        The namespace will be root_namespace + folder_path
        """
        # Create a namespace for the stored procedures
        namespace = f"{root_namespace}.{folder_path}"

        # Create the folder for the stored procedures
        sp_folder_path = os.path.join(folder_path, namespace)
        os.makedirs(sp_folder_path, exist_ok=True)

        # Generate the request and handler classes
        request_class = self.generate_request_class()
        handler_class = self.generate_handler_class()

        # add the namespace to the classes. use file scope namespace
        request_class = f"namespace {namespace};\n\n{request_class}"
        handler_class = f"namespace {namespace};\n\n{handler_class}"

        # Write the classes to files in the appropriate folders
        request_file_path = os.path.join(
            sp_folder_path, f"{self.sp_name}_Request.cs")
        handler_file_path = os.path.join(
            sp_folder_path, f"{self.sp_name}_Handler.cs")

        with open(request_file_path, 'w') as request_file:
            request_file.write(request_class)

        with open(handler_file_path, 'w') as handler_file:
            handler_file.write(handler_class)

    def generate_request_class(self):
        return self.request_generator.generate()

    def generate_handler_class(self):
        return self.handler_generator.generate()
