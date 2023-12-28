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
    def retrive_sp_name(sp_text):
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
        # will return alertTriggerMapping_get_test_location
        text = sp_text.strip().rstrip().split("\n")[0]
        sp_name = text[text.find(
            "[dbo].[usp_") + len("[dbo].[usp_"):text.find("@")].strip().rstrip().lstrip()
        return sp_name

    @staticmethod
    def get_sp_type(sp_name: str):
        """
            Returns the type of the SP whether is a query or a command.
        """
        # look for 'get' or 'select' in the SP name
        if "get" in sp_name or "select" in sp_name:
            return "query"
        else:
            return "command"

    @staticmethod
    def snake_case_to_camel_case(snake_case):
        """
            Converts a string from snake_case to camelCase.
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

    @staticmethod
    def handler_class_name(sp_name: str) -> str:
        """
            Returns the name of the handler class.
        """
        sp_type = SPUtils.get_sp_type(sp_name)
        handler_name = f"{SPUtils.snake_case_to_camel_case(sp_name)}{sp_type.capitalize()}Handler"
        return handler_name

    @staticmethod
    def request_class_name(sp_name: str) -> str:
        """
            Returns the name of the request class.
        """
        sp_type = SPUtils.get_sp_type(sp_name)
        handler_name = f"{SPUtils.snake_case_to_camel_case(sp_name)}{sp_type.capitalize()}"
        return handler_name

    @staticmethod
    def create_dynamic_params_section(params_dict):
        """
            Returns the dynamic params section of the handler.
            Example:

            For the following SP:

            CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
                @alert_id INT,
                @user_id INT
            AS

            The following dynamic params section will be generated:

            var parameters = new DynamicParameters();
            parameters.Add("@user_id", request.UserId, DbType.Int32);
            parameters.Add("@alert_id", request.AlertId, DbType.Int32);
        """

        dynamic_params = []
        for param_key, param_value in params_dict.items():
            if param_value["direction"] != "OUT":
                dynamic_params.append(
                    f"\tparameters.Add(\"@{param_value['name']}\", request.{param_value['camel_case_name']}, {param_value['sql_db_type']});")
        dynamic_params_str = "var parameters = new DynamicParameters(); \n    "
        dynamic_params_str = dynamic_params_str + \
            "\n".join(dynamic_params)
        return dynamic_params_str

    @staticmethod
    def retrive_sp_params(sp_text):
        """
            Returns a dictionary of SP params from the SP text.
            Dict example:
                "name": param_name,
                "camel_case_name": camel_case_name,
                "type": param_type,
                "csharp_type": csharp_type,
                "sql_db_type": sql_db_type,
                "direction": param_direction
        """
        # split the text into lines
        lines = sp_text.strip().rstrip().split("\n")
        # remove the first and last lines
        param_lines = lines[1:-1]
        # params dict with key as param name camel case and value as object with name, type and direction
        params = {}
        for line in param_lines:
            # remove leading and trailing spaces
            line = line.strip()
            # split by space
            parts = line.split(" ")
            # get the param name without @
            param_name = parts[0][1:]
            # get the param type
            param_type = parts[1]
            # get the param direction
            param_direction = "IN"
            if "OUT" in parts:
                param_direction = "OUT"
            elif "INOUT" in parts:
                param_direction = "INOUT"
            # add to params dict
            params[param_name] = {
                "name": param_name,
                "camel_case_name": SPUtils.snake_case_to_camel_case(param_name),
                "type": param_type,
                "csharp_type": SPUtils.str_to_csharp_type(param_type),
                "sql_db_type": SPUtils.str_to_sql_db_type(param_type),
                "direction": param_direction
            }
        return params
