import cython
from auth import Auth

# Keep human-readable names in 1st, actual in 2nd
opNames = ('Auth','GetSomething')
# Data stored in (GET,POST,PUT,DELETE), and each is a function
opFuncs = (Auth,Auth) # The second Auth is just a placeholder
