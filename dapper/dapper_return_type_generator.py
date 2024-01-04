import re
from dapper.sp_utils import SPUtils
from dapper.stored_procedure import StoredProcedure


class DapperReturnTypeGenerator:
    def __init__(self, sp: StoredProcedure):
        self.sp = sp

    # return a tuple with name of the return type and the return type class definition if it has one.
    def generate_return_type(self) -> tuple[str, str | None]:
        """
            Returns the return type of the SP. If the SP has no return type, meaning its a command, then returns Result<Unit>.
            A SP has a return type if:
                it has a RETURN statement.
                or if it has OUT parameters.
                or if it has a SELECT statement. The select has to be the first statement After Begin.
            This method will return a tuple with name of the return type and the return type class definition if it has one.
            Unit will return Unit with no class definition.
        """
        sp = self.sp

        sp_has_return_type = sp.has_return_type()

        # if SP has no return type, then return Unit
        if not sp_has_return_type:
            return "Unit", None

        sp_definition = sp.sp_definition
        sp_params_dict = sp.sp_params_dict
        sp_name = sp.sp_name

        # get the return type name
        return_type_name = self.get_return_type_name()

        # if the SP is a command and has a return type, meaning it has a RETURN statement, then return Result<Unit>
        # create a class definition for the return type with the OUT parameters
        if sp.get_sp_type() == "command":
            return_type_class_definition = self.get_command_return_type_class_definition()
            return f"{return_type_name}", return_type_class_definition

        else:
            # if the SP is a query and has a return type, meaning it has a RETURN statement, then return Result<Unit>
            # create a class definition for the return type with the OUT parameters
            return_type_class_definition = self.get_query_return_type_class_definition()

            # if the SP has a SELECT Top 1 statement, then return Result<T>
            # Otherwise, return Result<List<T>>

            has_top_1_select_statement = re.search(
                r'SELECT TOP 1', sp_definition, re.IGNORECASE)

            if has_top_1_select_statement:
                return_type_class_definition = self.get_query_return_type_class_definition()
                return f"{return_type_name}", return_type_class_definition

            return f"List<{return_type_name}>", return_type_class_definition

    def get_query_return_type_class_definition(self) -> str:
        sp_text = self.sp.sp_text
        sp_definition = self.sp.sp_definition
        sp_params_dict = self.sp.sp_params_dict
        sp_name = self.sp.sp_name

        # get the return type name
        return_type_name = self.get_return_type_name()

        # Extract the part of the stored procedure after AS BEGIN
        match = re.search(r'AS\s+BEGIN(.*)', sp_text,
                          re.DOTALL | re.IGNORECASE)
        if match:
            sp_text_after_as_begin = match.group(1)

            # There can be multiple SELECT statements in the SP. We only want the first one.
            # if the 1st SELECT statement returns *, then return an empty class definition
            has_select_star_statement = re.search(
                r'SELECT\s+\*\s+FROM', sp_text_after_as_begin, re.IGNORECASE)

        if has_select_star_statement:
            return f"public class {return_type_name}\n{{\n}}"

        # Find the position of the first SELECT after the CREATE PROCEDURE section
        create_proc_end = re.search(r'\bAS\b', sp_text, re.IGNORECASE).end()
        select_match = re.search(
            r'SELECT\s(.*?)\s+FROM', sp_text[create_proc_end:], re.DOTALL | re.IGNORECASE)

        if not select_match:
            return f"public class {return_type_name}\n{{\n}}"

        select_statement = select_match.group(1)
        # create a dict to hold the column names and types
        columns = {}

        # separate the columns by comma
        columns_list = select_statement.split(",")
        # process the column line and add to the columns dict
        # examples of column lines:
        # vwAlertLocalTime.acknowledged_by AS acknowledged_by_user_id
        # tblAlertState.alert_state_description
        # COALESCE(tblLocation.location_desc, '-- No mapped location --') AS location_desc

        for column_line in columns_list:
            column_name, column_type = self.extract_column_name_and_type(
                column_line)

            columns[column_name] = column_type

        # create the class definition
        class_definition = []

        for column_name, column_type in columns.items():
            class_definition.append(
                f"public {column_type} {SPUtils.snake_case_to_pascal_case(column_name)} {{ get; init; }}")

        class_definition_str = "\n    ".join(class_definition)
        class_definition = f"\npublic class {return_type_name}\n{{\n    {class_definition_str}\n}}\n"

        return class_definition

    def get_csharp_type(self, column_name: str) -> str:
        """
        Generates the C# type based on naming conventions.
        """
        # Convert to lowercase for case-insensitive matching
        lower_column_name = column_name.lower()

        if 'id' in lower_column_name:
            return 'int'
        elif lower_column_name.startswith('is_'):
            return 'bool'
        elif lower_column_name in ('created_at', 'updated_at'):
            return 'DateTime'
        else:
            return 'string'

    def extract_column_name_and_type(self, column_line: str) -> tuple[str, str]:
        """
        Extracts the column name and type from a column line.
        Example:
        column_line: vwAlertLocalTime.acknowledged_by AS acknowledged_by_user_id or
        column_line: tblAlertState.alert_state_description or
        column_line: COALESCE(tblLocation.location_desc, '-- No mapped location --') AS location_desc
        will return: (acknowledged_by_user_id, int)
        """
        # remove leading and trailing spaces
        column_line = column_line.strip()

        # Check if there is an alias (AS) and split accordingly
        if ' AS ' in column_line:
            column_parts = column_line.split(' AS ')
            column_name = column_parts[-1]
        else:
            parts = column_line.split('.')
            column_name = parts[-1].strip()

        # Use the get_csharp_type function to determine the C# type
        column_type = self.get_csharp_type(column_name)

        return column_name, column_type

    def get_command_return_type_class_definition(self) -> str:
        """
            Returns the class definition for the return type of a command SP.
            Example:
            For the following SP:
            CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
                @acknowledged_at DATETIME OUTPUT,
                @user_id INT,
                @alert_id INT
            AS
            The following class definition will be returned:
            public record UspAlertAcknowledgeAlertResult
            {
                public DateTime AcknowledgedAt { get; init; }
                public int UserId { get; init; }
                public int AlertId { get; init; }
            }
        """

        sp_params_dict = self.sp.sp_params_dict
        return_type_class_definition = []

        for param_key, param_value in sp_params_dict.items():
            if param_value["direction"] == "OUTPUT" or param_value["direction"] == "INOUT" or param_value["direction"] == "OUT":
                return_type_class_definition.append(
                    f"public {param_value['csharp_type']} {param_value['pascal_case_name']} {{ get; init; }}")

        return_type_class_definition_str = "\n    ".join(
            return_type_class_definition)
        return_type_class_definition = f"\npublic record {self.get_return_type_name()}\n{{\n    {return_type_class_definition_str}\n}}\n"
        return return_type_class_definition

    def get_return_type_name(self):
        """
            Returns the name of the return type. for sp name: usp_get_alert_acknowledge_alert, the return type name will be UspGetAlertAcknowledgeAlertResult.
        """
        sp = self.sp
        return_type_name = f"{SPUtils.snake_case_to_pascal_case(sp.sp_name)}Result"
        return return_type_name
