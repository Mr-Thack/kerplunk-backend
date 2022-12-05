from auth import Auth
from users import Users

# Keep human-readable names in 1st list, actual function handler in 2nd

# The human-readable names are actually used in the HTTP Query
# e.g. http://24.99.231.214/api/Auth
opNames = ('Auth','Users')
# Data stored in ((GET,POST),(another,one)) and each is mapped to a function
opFuncs = (Auth,Users)
# If needed, implement PUT and DELETE
