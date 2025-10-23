class Reference:
    def __init__(self, env, name):
        self.env = env
        self.name = name
    def get(self):
        return self.env.get(self.name)
    def set(self, value):
        self.env.set(self.name, value)
    def __repr__(self):
        return f"Reference({self.env}, {self.name!r})"
# Gambl/environment.py
# Environment and Scope Management

class Env:
    """
    Environment class for managing variable and function scopes.
    Handles variable storage, lookup, and assignment.
    """
    
    def __init__(self):
        self.variables = {}

    def define(self, name, value):
        """
        Define a new variable in this environment.
        
        Args:
            name (str): Variable name
            value: Variable value
        """
        self.variables[name] = value

    def get(self, name):
        """
        Get a variable's value from this environment.
        
        Args:
            name (str): Variable name
            
        Returns:
            The variable's value
            
        Raises:
            NameError: If the variable is not defined
        """
        if name in self.variables:
            return self.variables[name]
        else:
            raise NameError(f"Undefined variable: {name}")
        
    def set(self, name, value):
        """
        Set a variable's value. Creates the variable if it doesn't exist.
        
        Args:
            name (str): Variable name
            value: New value for the variable
        """
        if name in self.variables:
            self.variables[name] = value
        else:
            self.define(name, value)
            
    def copy(self):
        """
        Create a shallow copy of this environment.
        
        Returns:
            Env: A new environment with copied variables
        """
        new_env = Env()
        new_env.variables = self.variables.copy()
        return new_env
        
    def __repr__(self):
        return f"Env({self.variables})"