sp_text = """
CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
  @user_id INT,
  @alert_id INT
AS
"""

def retrive_sp_name(sp_text):
    sp_name = sp_text.split(" ")[2]
    return sp_name

sp_name = retrive_sp_name(sp_text)
print(sp_name)

def retrive_sp_params(sp_text):
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
            "type": param_type,
            "direction": param_direction
        }
    return params


sp_params = retrive_sp_params(sp_text)
print(sp_params)
