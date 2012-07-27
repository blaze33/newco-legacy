# -*- coding: utf-8 -*-
import csv, sys, pprint
from decimal import *
from urllib2 import urlopen
from items.models import Item
from affiliation.models import AffiliationItem, Store

def get_aff_items(query): # a vocation a etre une fonction appelee dans views pour chercher parmi les differents catalogues; ds un premier temps tres simple puisque juste Decathlon ici
    entries = AffiliationItem.objects.filter(name_at_store__icontains=query)
    
    return entries


def process_update_affi(view, request, *args, **kwargs):

    name = request.POST['name']
    if len(name) > 3:
        list_items = get_aff_items(name)
        kwargs.update({"list_items": list_items})
                
    if view.form_class:
        form_kwargs = view.get_form_kwargs()
        form_kwargs.update({'request': request})
        form = view.form_class(**form_kwargs)
    else:
        print "\n\n--- In 'not self.form_class'... "
        print "shouldn't there be a form class ? ---\n\n"
        form_class = view.get_form_class()
        form = view.get_form(form_class)
    
    #Seb: TODO trouver comment les form fields peuvent ne pas etre verifies lorsqu'on fait "update" ... je trouve pas !
    return view.render_to_response(view.get_context_data(form=form, **kwargs))


def load_decat_file():
    print "\n---\nEnter in load_decat\n---\n" 
    address_decat = "http://flux.netaffiliation.com/catalogue.php?maff=A6AB58DCS569B4B545AF92191v3"
    csvfile = urlopen(address_decat)
    csvdialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=';')
    csvfile = urlopen(address_decat) ## Seb: I reopen the file because urlopen doesn't provide a way to position the "cursor" like ".seek()" , it's not performant, but as a quickfix it works.
    
    return csv.DictReader(csvfile,
                          dialect=csvdialect)


def delete_entry(ref_to_del):
    print "\n---\nEntered in Ref delete function\n---\n" 
    
    try:
        entry_death_row = AffiliationItem.objects.get(ref_catalog=ref_to_del)
        entry_death_row.delete()
        
    except AffiliationItem.DoesNotExist:
        print "\n---\nDoesNotExists returned - in delete loop !"
        print "\nDuplicate already deleted ?"
        raw_input("Type enter to continue \n---\n")
    
    except AffiliationItem.MultipleObjectsReturned:
        # ici on delete toutes les entrees avec cet ref, afin d'eviter a la 
        # bdd de trop grossir sur un bug de doublons
        
        print "\n---\nMultiple objects returned - in delete loop !"
        print "Was it a doublon in the db ?"
        raw_input("Type enter to continue \n---\n")
        
        entries_to_del = AffiliationItem.objects.filter(ref_catalog=ref_to_del)
        for entry_to_del in entries_to_del:
            print "\n---\nEntry :"
            print entry_to_del.name_at_store, " is on the death row.\n---\n"
        
            ref_test = entry_to_del.ref_catalog
            entry_to_del.delete()
            
            try:
                AffiliationItem.objects.get(ref_catalog=ref_test)
                print "Remains entry with this ref, continuing loop\n---\n"
            except AffiliationItem.MultipleObjectsReturned:
                print "Shit, still MultipleObjectsReturned, "
                print "was more than 2 Entry.ref_catalog=", ref_test, " ?\n---\n"
            except AffiliationItem.DoesNotExist:
                print "Cool it seems it has been deleted correctly !\n---\n"


def load_entry(row):
    entry = AffiliationItem()
    entry.item_id = 1
    entry.store_id = 1
    
    for key, value in row.items():
        #print key, " : ", value
        if key == "Prix":
            entry.price = Decimal(value.replace(",",".")).quantize(Decimal('0.01'))
        elif key == "Url":
            entry.url = value
        elif key == "Url image grande":
            entry.url_img = value
        elif key == "Url image petite":
            entry.url_img_s = value
        elif key == "EAN":
            entry.ean = int(value)
        elif key == "Nom":
            entry.name_at_store = value
        elif key == "Référence interne":
            entry.ref_catalog = int(value)
            
    return entry


def load_decat_in_db():
    decat_catalog = load_decat_file()

    ref_in_db = list(AffiliationItem.objects.all().values_list('ref_catalog', 
                                                               flat=True))
    
    for row in decat_catalog:
        entry = load_entry(row)
        
        if entry.ref_catalog in ref_in_db: # entry exists => update
            try:
                entry.pk = AffiliationItem.objects.get(ref_catalog=entry.ref_catalog).pk
                entry.save()
                
                ref_in_db.pop(ref_in_db.index(int(entry.ref_catalog)))
                print "\n---\nEntry :", entry.name_at_store, 
                print " \nhas been updated\n---\n"
                
            except AffiliationItem.MultipleObjectsReturned:
                print "\n---\nMultipleObjectsReturned when tried to update!"
                print "Was it a doublon in the db ? Deleting entry."
                raw_input("Type enter to continue \n---\n")
                delete_entry(int(entry.ref_catalog))
                
            except AffiliationItem.DoesNotExist:
                print "\n---\nDoesNotExist when tried to update!"
                raw_input("Type enter to continue \n---\n")
            
        else:#entree n'existe pas => on la cree
            print "entry ref catalog:", entry.ref_catalog
            print "entry ean:", entry.ean
            print "entry name:", entry.name_at_store
            
            entry.save()
            print "\n---\nEntry: ", entry.name_at_store
            print " has been created\n---\n"

    if ref_in_db: #If ref was in DB and hasn't been updated = not in catalog anymore => to delete
        print "\nThere is remaining ref_catalog in db not in catalog!\n"
        for ref in ref_in_db:
            delete_entry(ref)
        print len(ref_in_db), " entries have been deleted \n"
        print "\n---\nRef of the deleted entries: \n"
        print ref_in_db, "\n---\n"
    
    print "\n---\nEnd of Decathlon catalog import. Everything seems to have "
    print "worked correctly\n---\n"
    


def main():
    
    #faire ici une boucle sur les differents calalogues a charger en base
    
    load_decat_in_db()
    
    print "\n---\nEnd of catalogs import. Everything seems to have worked "
    print "correctly\n---\n"
    
    
if __name__ == "__main__":
    main()
    