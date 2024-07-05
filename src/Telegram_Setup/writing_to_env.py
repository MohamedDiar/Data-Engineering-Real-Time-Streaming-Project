#%%
"""
Helper script is used to write the environment variables to the .env file
"""

#The update_env_file function is used to append a new line to the .env file.
def update_env_file(env_var, value):
    """Appends a new line to the.env file in the root directory."""
    with open(".env", "a") as f:
        f.write(f"{env_var}={value}\n")