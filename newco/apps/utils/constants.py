import re

EMAIL_PATTERN = re.compile(
    "(?P<username>[a-z0-9!#$%&'*+/=?^_`{|}~-]+"
    "(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*)"
    "@(?P<domain>(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+"
    "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
)
