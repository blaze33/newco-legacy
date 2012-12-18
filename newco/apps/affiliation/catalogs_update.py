import sys

from django.conf import settings


def main():
    if settings.DEBUG:
        pass

    try:
        from affiliation.models import AffiliationItem, Store
        from affiliation.decathlon.tools import decathlon_db_processing
    except ImportError:
        sys.stdout.write("Imports failed.\n")
    else:
        store = Store.objects.get_store("Decathlon")
        log_path = settings.PROJECT_ROOT + "/decathlon_db_log.txt"
        errors = decathlon_db_processing(AffiliationItem, store, log_path)

        if len(errors) != 0:
            sys.stdout.writelines(errors)


if __name__ == "__main__":
    main()
