import re


class SPUtils:
    """
        SPUtils is a utility class that provides static methods for handling stored procedures (SPs).
    """

    @staticmethod
    def retrive_dapper_class_name(sp_text):
        """
            Returns the name of the SP from the SP text.
        """
        # CREATE PROCEDURE [dbo].[usp_alertTriggerMapping_get_test_location]
        #     @trigger_id INT,
        #     @site_name NVARCHAR(60) OUT,
        #     @site_timezone_id VARCHAR(100) OUT,
        #     @sensor_type_desc VARCHAR(100) OUT
        # AS
        # capture everything between CREATE PROCEDURE and the first @
        text = sp_text.strip().rstrip().split("\n")[0]
        sp_name = text[text.find(
            "[dbo].[usp_") + len("[dbo].[usp_"):text.find("@")].strip().rstrip().lstrip()
        return sp_name

    @staticmethod
    def snake_case_to_pascal_case(snake_case):
        """
            Converts a string from snake_case to camelCase.
        """
        camel_case = ''.join(
            x.capitalize() or '_' for x in snake_case.split('_'))
        return camel_case

    @staticmethod
    def snake_case_to_camel_case(snake_case):
        """
            Converts a string from snake_case to camelCase.
        """
        components = snake_case.split('_')
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        camel_case = components[0] + ''.join(x.title() for x in components[1:])
        return camel_case

    @staticmethod
    def to_pascal_case(snake_case):
        """
            Converts a string from snake or camel case to PascalCase.
        """
        camel_case = ''.join(
            x.capitalize() or '_' for x in snake_case.split('_'))
        return camel_case

    @staticmethod
    def str_to_csharp_type(type: str):
        """
            Converts a string to a C# type
        """
        csharp_type = ""
        if type == "INT":
            csharp_type = "int"
        elif type == "VARCHAR":
            csharp_type = "string"
        elif type == "DATETIME":
            csharp_type = "DateTime"
        elif type == "BIT":
            csharp_type = "bool"
        else:
            csharp_type = "string"
        return csharp_type

    @staticmethod
    def str_to_dapper_param_direction(direction: str):
        """
            Converts a string to a C sharp param direction
        """
        csharp_param_direction = ""
        if direction == "IN":
            csharp_param_direction = "ParameterDirection.Input"
        elif direction == "OUT":
            csharp_param_direction = "ParameterDirection.Output"
        elif direction == "INOUT":
            csharp_param_direction = "ParameterDirection.InputOutput"
        return csharp_param_direction

    @staticmethod
    def str_to_sql_db_type(type: str):
        """
            Converts a string to a C# type
        """
        sql_db_type = ""
        if type == "INT":
            sql_db_type = "DbType.Int32"
        elif type == "VARCHAR":
            sql_db_type = "DbType.String"
        elif type == "DATETIME":
            sql_db_type = "DbType.DateTime"
        elif type == "BIT":
            sql_db_type = "DbType.Boolean"
        else:
            sql_db_type = "DbType.String"
        return sql_db_type
