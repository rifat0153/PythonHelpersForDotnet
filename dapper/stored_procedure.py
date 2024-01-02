from dapper.sp_utils import SPUtils
import re


class StoredProcedure:
    def __init__(self, text: str):
        self.sp_text = text
        self.sp_definition = self.extract_stored_procedure_definition()
        self.sp_params_dict = self.retrive_sp_params()
        self.sp_name = self.retrive_sp_name()

    def handler_class_name(self) -> str:
        """
            Returns the name of the handler class.
        """
        sp_type = self.get_sp_type()
        handler_name = f"{SPUtils.snake_case_to_pascal_case(self.sp_name)}{sp_type.capitalize()}Handler"
        return handler_name

    def request_class_name(self) -> str:
        """
            Returns the name of the Dapper request class. Example: AlertAcknowledgeAlertCommand : IRequest<Result<Unit>>
        """
        sp_type = self.get_sp_type()
        handler_name = f"{SPUtils.snake_case_to_pascal_case(self.sp_name)}{sp_type.capitalize()}"
        return handler_name

    def get_sp_type(self):
        """
            Returns the type of the SP whether is a query or a command.
        """
        # look for 'get' or 'select' in the SP name
        if "get" in self.sp_name or "select" in self.sp_name:
            return "query"
        else:
            return "command"

    def has_return_type(self) -> bool:
        """
            Returns True if the SP has a return type.
        """
        # A SP has a return type if:
        # its name contains 'get' or 'retrieve'
        # or it has a RETURN statement.
        # or it has OUT or OUTPUT parameters.

        # check if SP name contains 'get' or 'retrieve'
        if re.search(r'(get|retrieve)', self.sp_name, re.IGNORECASE):
            return True

        # check if SP has RETURN statement
        if re.search(r'\bRETURN\b', self.sp_text, re.IGNORECASE):
            return True

        # check if SP has OUT or OUTPUT parameters
        if re.search(r'\b(OUT|OUTPUT|INOUT)\b', self.sp_text, re.IGNORECASE):
            return True

        return False

    def extract_stored_procedure_definition(self) -> str:
        """
            Returns the stored procedure definition from the SQL script.

            Return everything between CREATE PROCEDURE and AS including CREATE PROCEDURE and AS.
        """
        # Define the pattern to match the stored procedure definition
        pattern = re.compile(
            r'(CREATE\s+PROCEDURE\s*[\s\S]*?\s*AS)', re.IGNORECASE)

        # Search for the pattern in the SQL script
        match = pattern.search(self.sp_text)

        if match:
            procedure_definition = match.group(1)
            return procedure_definition.strip()

        return ""

    def retrive_sp_name(self) -> str:
        """
            Returns the name of the SP from the SP text.

            CREATE PROCEDURE [dbo].[usp_alertTriggerMapping_get_test_location]
                @trigger_id INT,
                @site_name NVARCHAR(60) OUT,
                @site_timezone_id VARCHAR(100) OUT,
                @sensor_type_desc VARCHAR(100) OUT
            AS
            capture everything between CREATE PROCEDURE and the first @
            will return alertTriggerMapping_get_test_location
        """

        # Use a regular expression to find the stored procedure name
        match = re.search(r'usp_(.*?)\s', self.sp_definition, re.IGNORECASE)

        if match:
            # The stored procedure name is the first (and only) group in the match
            sp_name = match.group(1)
            # remove the square brackets
            sp_name = sp_name.replace("[", "").replace("]", "")
            return sp_name
        else:
            return None

    def retrive_sp_params(self) -> dict:
        """
            Returns a dictionary of SP params from the SP text.

            Dict example:
                "name": param_name,
                "camel_case_name": camel_case_name,
                "pascal_case_name": pascal_case_name,
                "type": param_type,
                "csharp_type": csharp_type,
                "sql_db_type": sql_db_type,
                "direction": param_direction
        """
        # split the text into lines
        lines = self.sp_definition.strip().rstrip().split("\n")
        # remove any lines that doesn't start with @
        param_lines = [
            line for line in lines if line.strip().startswith("@")]

        # params dict with key as param name camel case and value as object with name, type and direction
        params = {}

        for line in param_lines:
            # remove leading and trailing spaces
            line = line.strip().replace(",", "")
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
                "pascal_case_name": SPUtils.snake_case_to_pascal_case(param_name),
                "type": param_type,
                "csharp_type": SPUtils.str_to_csharp_type(param_type),
                "sql_db_type": SPUtils.str_to_sql_db_type(param_type),
                "direction": param_direction,
                "csharp_param_direction": SPUtils.str_to_dapper_param_direction(param_direction)
            }

        return params

    def retrive_dynamic_params_section(self):
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
        for param_key, param_value in self.sp_params_dict.items():
            dynamic_params.append(
                f"\tparameters.Add(\"@{param_value['name']}\", request.{param_value['pascal_case_name']}, {param_value['sql_db_type']}, {param_value['csharp_param_direction']});")
        dynamic_params_str = "var parameters = new DynamicParameters(); \n    "
        dynamic_params_str = dynamic_params_str + \
            "\n".join(dynamic_params)
        return dynamic_params_str
