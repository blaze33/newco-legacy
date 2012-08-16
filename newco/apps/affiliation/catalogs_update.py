import sys
from django.conf import settings
from affiliation.decathlon.utils import decathlon_db_processing


def main():
    errors = decathlon_db_processing(settings.PROJECT_ROOT + "/cat_db_log.txt")

    if len(errors) != 0:
        sys.stdout.writelines(errors)


if __name__ == "__main__":
    main()
