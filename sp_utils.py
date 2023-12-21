class SPUtils:
    """
        SPUtils is a utility class that provides static methods for handling stored procedures (SPs).
    """

    @staticmethod
    def retrive_sp_name(sp_text):
        """
            Returns the name of the SP from the SP text.
        """
        sp_name = sp_text.split(" ")[2]
        return sp_name

    @staticmethod
    def snake_case_to_camel_case(snake_case):
        """
            Converts a string from snake_case to camelCase.
        """
        camel_case = ''.join(x.capitalize() or '_' for x in snake_case.split('_'))
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
    def retrive_sp_params(sp_text):
        """
            Returns a dictionary of SP params from the SP text.
            Dict example:
                "name": param_name,
                "camel_case_name": camel_case_name,
                "type": param_type,
                "csharp_type": csharp_type,
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
                "direction": param_direction
            }
        return params