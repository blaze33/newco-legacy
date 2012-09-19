import codecs
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError

from affiliation.models import AffiliationItem, AffiliationItemCatalog, Store
from affiliation.catalogs_tools import csv_url2dict
from utils.tools import get_queries_by_score


def decathlon_product_search(keyword, nb_items=10):
    decathlon, created = Store.objects.get_or_create(
        name="Decathlon", url="http://www.decathlon.fr"
    )

    # Exclude from search already linked items
    d4_object_ids = AffiliationItem.objects.filter(
                        store=decathlon).values_list("object_id", flat=True)
    d4_prods = AffiliationItemCatalog.objects.filter(store=decathlon).exclude(
                            object_id__in=d4_object_ids, store=decathlon)

    query_dict = get_queries_by_score(keyword, ["name"])
    keys = sorted(query_dict.keys(), reverse=True)
    results = list()
    for score in keys:
        query = query_dict.get(score)
        #TODO: better implementation
        item_list = list(d4_prods.filter(query))
        for item in item_list:
            if not results.__contains__(item):
                results.append(item)
        if len(results) >= nb_items:
            break

    return results[:nb_items]


@transaction.commit_manually
def decathlon_db_processing(output_file=None):

    # If file path given in kwargs, writes log in it. Else, stdout.
    if output_file:
        output = codecs.open(output_file, "w+", "utf-8")
    else:
        output = sys.stdout
    output.write("\n-----------\nDECATHLON DB PROCESSING\n-----------\n")

    storing_class = AffiliationItemCatalog
    errors = list()
    decathlon, created = Store.objects.get_or_create(
        name="Decathlon", url="http://www.decathlon.fr"
    )
    transaction.commit()

    # Decathlon stored references. #TODO: store D4 ref in other DB
    d4_items = storing_class.objects.filter(store=decathlon)
    d4_object_ids = list(d4_items.values_list("object_id", flat=True))

    d4_csv_url = "http://flux.netaffiliation.com/catalogue.php" + \
                                            "?maff=A6AB58DCS569B4B545AF92191v3"
    rows = csv_url2dict(d4_csv_url)

    transaction.commit()
    for i, row in enumerate(rows):
        output.write("ENTRY %d --- " % (i + 1))
        entry = storing_class()
        entry.store_init("decathlon", row)

        if entry.object_id in d4_object_ids:
            try:
                item = d4_items.get(object_id=entry.object_id)
            except ObjectDoesNotExist:
                err_msg = "Couldn't load object %s while updating" \
                                                            % entry.object_id
                errors.append(err_msg + "\n")
                output.write(err_msg)
            else:
                if not item.identical(entry):
                    entry.id = item.id
                    entry.save()
                    transaction.commit()
                    output.write("UPDATED: %s" % entry.name[:50])
                else:
                    transaction.commit()
                    output.write("NO CHANGES: %s" % entry.name[:50])
                del d4_object_ids[d4_object_ids.index(entry.object_id)]
        else:
            # Since postgres db not functionnal after an IntegrityError,
            # need to handle transactions manually
            try:
                entry.save()
                transaction.commit()
            except IntegrityError:
                transaction.rollback()
                err_msg = "Object %s already existing in DB" \
                                                        % entry.object_id
                errors.append(err_msg + "\n")
                output.write(err_msg)
            else:
                output.write("CREATED: %s" % entry.name[:50])

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
                err_msg = "Couldn't load object %s while deleting" \
                                                            % object_id
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
