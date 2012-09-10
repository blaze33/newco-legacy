import sys
from django.conf import settings


def main():
    if settings.DEBUG:
        pass

    try:
        from affiliation.decathlon.tools import decathlon_db_processing
    except ImportError:
        sys.stdout.write("Decathlon function import failed.\n")
    else:
        errors = decathlon_db_processing(
                                    settings.PROJECT_ROOT + "/cat_db_log.txt")

        if len(errors) != 0:
            sys.stdout.writelines(errors)


if __name__ == "__main__":
    main()
