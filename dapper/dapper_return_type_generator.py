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
                return f"Result<{return_type_name}>", return_type_class_definition

            return f"Result<List<{return_type_name}>>", return_type_class_definition

    def get_query_return_type_class_definition(self) -> str:
        """
            BEGIN
            SELECT vwUserWithBranding.user_id,
                vwUserWithBranding.tenant_id, 
                vwUserWithBranding.first_name,
                vwUserWithBranding.last_name, 
                vwUserWithBranding.full_name,
                vwUserWithBranding.email, 
                vwUserWithBranding.mobile,
                vwUserWithBranding.tenant_role_id,
                vwUserWithBranding.is_global_admin,
                vwUserWithBranding.permissions_last_updated,
                vwUserWithBranding.login_url,
                vwUserWithBranding.email_sender_name,
                vwUserWithBranding.email_sender_email,
                vwUserWithBranding.alert_email_footer
            FROM vwUserWithBranding

            or

                IF (@site_id IS NULL AND @location_group_id IS NULL AND @location_id IS NULL AND @max_date_utc IS NULL AND @only_data_alerts = 1 AND @include_cleared_alerts = 0)
            BEGIN
                -- uses IX_tblAlert__K17_K3_2_6_7_8_F12
                SELECT --DISTINCT
                    --vwAlertLocalTime.alert_id,
                    --vwAlertLocalTime.alert_type,
                    vwAlertLocalTime.alert_state_id,
                    tblAlertState.alert_state_description,
                    vwAlertLocalTime.time_raised,
                    vwAlertLocalTime.message,
                    --vwAlertLocalTime.severity,
                    vwAlertLocalTime.site_name,
                    COALESCE(tblLocation.location_desc, '-- No mapped location --') AS location_desc,
                    tblAlertSeverityImageUrl.image_url--,

            SP with top SELECT statement will return a list of the SELECT statement.
            SP with top SELECT statement that uses Top 1 will return a single object of the SELECT statement.

            SP with SELECT statement that returns * will return a list of the SELECT statement. The class will have no fields in this case.
        """

        sp_definition = self.sp.sp_definition
        sp_params_dict = self.sp.sp_params_dict
        sp_name = self.sp.sp_name

        # get the return type name
        return_type_name = self.get_return_type_name()

        # use RE to check if the SP has a SELECT statement
        select_pattern = re.compile(r'SELECT(.*?)FROM', re.DOTALL)
        select_match = select_pattern.search(sp_definition)

        if select_match:
            # Extract the column names from the SELECT statement
            column_names = re.findall(r'(\w+)(?:,|\n)', select_match.group(1))

            # Generate the class definition
            return_type_class_definition = f"public class {return_type_name}\n{{\n"
            for column_name in column_names:
                return_type_class_definition += f"\tpublic object {column_name} {{ get; set; }}\n"
            return_type_class_definition += "}"

            return return_type_class_definition
        else:
            return None

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
