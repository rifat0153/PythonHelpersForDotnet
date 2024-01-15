import os
from dapper.dapper_generator import DapperGenerator
from dapper.sp_utils import SPUtils
from dapper.dapper_handler_generator import DapperHandlerGenerator
from dapper.dapper_request_generator import DapperRequestGenerator


class DapperFileGenerator:
    def generate(self, sp_folder_path: str, output_folder_path: str, root_namespace: str):
        """
            Read all the sql file in the given folder and generate the request and handler classes for them.
        """
        files = os.listdir(sp_folder_path)
        files_sql = filter(lambda file: file.endswith('.sql'), files)

        for file in files_sql:
            # read the contents of the file
            file_path = os.path.join(sp_folder_path, file)
            with open(file_path, 'r') as file:
                sp_text = file.read()
                dapper_generator = DapperGenerator(sp_text)

                namespace = f"{root_namespace}.{sp_folder_path}"
                request_class, return_class = dapper_generator.generate_request_class()
                handler_class = dapper_generator.generate_handler_class()

                # queries will be in a folder called queries and commands will be in a folder called commands
                # the namespace will be root_namespace + SP_TYPE (query or command) + SP_NAME
                sp_type = dapper_generator.sp_is_query and 'queries' or 'commands'
                sp_name = dapper_generator.sp_name
                namespace = f"{namespace}.{sp_type}.{sp_name}"
                # split the namespace by dot and
                # convert the namespace to pascal case
                namespace = '.'.join(
                    map(lambda x: SPUtils.to_pascal_case(x), namespace.split('.')))
                sp_name_pascal_case = SPUtils.to_pascal_case(sp_name)

                # add the namespace to the classes. use file scope namespace
                request_class = f"namespace {namespace};\n\n{request_class}"
                if return_class:
                    return_class = f"namespace {namespace};\n\n{return_class}"
                handler_class = f"namespace {namespace};\n\n{handler_class}"

                request_file_name = SPUtils.to_pascal_case(
                    f"{sp_name}_Request.cs")
                return_file_name = SPUtils.to_pascal_case(
                    f"{sp_name}_Result.cs")
                handler_file_name = SPUtils.to_pascal_case(
                    f"{sp_name}_Handler.cs")
                # PascalCase the file names
                request_folder_path = os.path.join(
                    output_folder_path, sp_type, sp_name_pascal_case, request_file_name)
                return_folder_path = os.path.join(
                    output_folder_path, sp_type, sp_name_pascal_case, return_file_name)
                handler_folder_path = os.path.join(
                    output_folder_path, sp_type, sp_name_pascal_case, handler_file_name)

                os.makedirs(os.path.dirname(
                    request_folder_path), exist_ok=True)
                if return_class:
                    os.makedirs(os.path.dirname(
                        return_folder_path), exist_ok=True)
                os.makedirs(os.path.dirname(
                    handler_folder_path), exist_ok=True)

                # write the classes to files
                with open(request_folder_path, 'w') as request_file:
                    request_file.write(request_class)

                if return_class:
                    with open(return_folder_path, 'w') as return_file:
                        return_file.write(return_class)

                with open(handler_folder_path, 'w') as handler_file:
                    handler_file.write(handler_class)
