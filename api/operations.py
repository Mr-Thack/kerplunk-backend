import cython
from auth import Auth

# Keep human-readable names in 1st list, actual function handler in 2nd

# The human-readable names are actually used in the HTTP Query
# e.g. http://24.99.231.214/api/Auth
# DO NOT SHORTEN THE TUPLES TO LENGTH=1, OR ELSE THEY TURN TO STRINGS
opNames = ('Auth','GetSomething')
# Data stored in ((GET,POST),(another,one)) and each is mapped to a  function
opFuncs = (Auth,Auth) # The second Auth is just a placeholder
# If needed, implement PUT and DELETE
