import codecs
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError

from affiliation.catalogs_tools import csv_url2dict
from utils.tools import get_search_results


def decathlon_product_search(keyword, storing_class, store, nb_items=10):
    # Exclude from search already linked items
    d4_prods = storing_class.objects.filter(store=store, item=None)

    # Mininum length for words that are used for the search
    min_len = 3
    return get_search_results(d4_prods, keyword, ["name"], min_len, nb_items)


@transaction.commit_manually
def decathlon_db_processing(storing_class, store, output_file=None):

    # If file path given in kwargs, writes log in it. Else, stdout.
    if output_file:
        output = codecs.open(output_file, "w+", "utf-8")
    else:
        output = sys.stdout
    output.write("\n-----------\nDECATHLON DB PROCESSING\n-----------\n")

    errors = list()
    transaction.commit()

    # Decathlon stored references. #TODO: store D4 ref in other DB
    d4_items = storing_class.objects.filter(store=store)
    d4_object_ids = list(d4_items.values_list("object_id", flat=True))

    d4_csv_url = "http://flux.netaffiliation.com/catalogue.php" + \
        "?maff=A6AB58DCS569B4B545AF92191v3"
    rows = csv_url2dict(d4_csv_url)

    transaction.commit()
    for i, row in enumerate(rows):
        output.write("ENTRY %d --- " % (i + 1))
        entry, created = storing_class.objects.get_or_create(
            store=store, object_id=row.get("Id produit", ""))

        if created:
            # Since postgres db not functionnal after an IntegrityError,
            # need to handle transactions manually
            entry.store_init(store, row)
            try:
                entry.save()
                transaction.commit()
            except IntegrityError:
                transaction.rollback()
                err_msg = "Object %s already existing in DB" % entry.object_id
                errors.append(err_msg + "\n")
                output.write(err_msg)
            else:
                output.write("CREATED: %s" % entry.name[:50])
        else:
            new_entry = storing_class()
            new_entry.store_init(store, row)
            if entry.same_as(new_entry):
                transaction.commit()
                output.write("NO CHANGES: %s" % entry.name[:50])
            else:
                new_entry.id = entry.id
                new_entry.save()
                transaction.commit()
                output.write("UPDATED: %s" % entry.name[:50])
            del d4_object_ids[d4_object_ids.index(entry.object_id)]

        output.write("\n")
        output.flush()

    # Delete DB entries that aren't in source
    if d4_object_ids:
        output.write("\n__________\nMismatch between CSV and stored catalog\n")
        output.write("Deleting old entries in Decathlon DB\n__________\n")

        nb_del = len(d4_object_ids)
        for i, object_id in enumerate(d4_object_ids):
            output.write("DELETION %d/%d --- " % (i + 1, nb_del))
            try:
                entry = d4_items.get(object_id=object_id)
            except ObjectDoesNotExist:
                err_msg = "Couldn't load object %s while deleting" % object_id
                output.write(err_msg)
                errors.append(err_msg + "\n")
            else:
                entry.delete()
                transaction.commit()
                output.write("DELETED: %s" % entry.name[:50])

            output.write("\n")
            output.flush()

    output.write("\n-----------\nDECATHLON DB PROCESSING DONE\n-----------\n")

    if len(errors) > 0:
        output.write("\n!!!!!!!!!\nERRORS\n!!!!!!!!!\n")
        output.writelines(errors)

    if output != sys.stdout:
        output.close()

    return errors
