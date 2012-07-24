# -*- coding: utf-8 -*-
import csv, sys, pprint
from decimal import *
from urllib2 import urlopen
from items.models import Item
from affiliation.models import AffiliationItem, Store

#def ImportDecat(file_name):
#    csvfile = open(file_name, "rb")
#    csvdialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=';')
#    csvfile.seek(0)
    
#    return csv.DictReader(csvfile,
#                          dialect=csvdialect)

def ImportDecat(address):
    print "\n---\nEnter in ImportDecat\n---\n" 
    csvfile = urlopen(address)
    csvdialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=';')
    #csvfile.seek(0)
    csvfile = urlopen(address) ## Seb: I reopen the file because urlopen doesn't provide a way to position the "cursor" like ".seek()" , it's not performant, but as a quickfix it works.
    
    return csv.DictReader(csvfile,
                          dialect=csvdialect)
   
    
def DeleteEntry(ean_to_del):
    print "\n---\nEntered in EAN delete fct\n---\n" 
    
    try:
        entry_death_row = AffiliationItem.objects.get(ean=ean_to_del)
        entry_death_row.delete()
        
    except AffiliationItem.DoesNotExist:
        print "\n---\nDoesNotExists returned - in delete loop !"
        print "\nDuplicate already deleted ? \n---\n"
    
    except AffiliationItem.MultipleObjectsReturned:
        # ici on delete toutes les entrees avec cet EAN, afin d'eviter a la 
        # base de trop grossir sur un bug
        
        print "\n---\nMultiple objects returned - in delete loop !\n---\n"
        
        entries_to_del = AffiliationItem.objects.filter(ean=ean_to_del)
        for entry_to_del in entries_to_del:
            print "\n---\nEntry :"
            print entry_to_del.name_at_store, " is on the death row.\n---\n"
        
            ean_test = entry_to_del.ean
            entry_to_del.delete()
            
            try:
                AffiliationItem.objects.get(ean=ean_test)
                print "Remains entry with this EAN, continuing loop\n---\n"
            except AffiliationItem.MultipleObjectsReturned:
                print "Shit, still MultipleObjectsReturned, "
                print "was more than 2 Entry.ean=", ean_test, " ?\n---\n"
            except AffiliationItem.DoesNotExist:
                print "Cool it seems it has been deleted correctly !\n---\n"


def main():
    address = "http://flux.netaffiliation.com/catalogue.php?maff=A6AB58DCS569B4B545AF92191v3"
    decat_catalog = ImportDecat(address)

    ean_in_db = list(AffiliationItem.objects.all().values_list('ean', flat=True))
    
    entry = AffiliationItem()
    entry.item_id = 1
    entry.store_id = 1
    
    for row in decat_catalog:
        for key, value in row.items():
            #print key, " : ", value
            if key == "Prix":
                entry.price = Decimal(value.replace(",",".")).quantize(Decimal('0.01'))
            elif key == "Url":
                entry.url = value
            elif key == "Url image grande":
                entry.url_img = value
            elif key == "EAN":
                entry.ean = int(value)
            elif key == "Nom":
                entry.name_at_store = value
            elif key == "Référence interne":
                entry.object_ref = value
        
        if int(entry.ean) in ean_in_db: #entree existe => on la met a jour
            try:
                #print "\n---\nEnter in save\n---\n"
                entry.pk = AffiliationItem.objects.get(ean=entry.ean).pk
                entry.save()
                
                ean_in_db.pop(ean_in_db.index(int(entry.ean)))
                print "\n---\nEntry :", entry.name_at_store, 
                print " \nhas been updated\n---\n"
                
            except AffiliationItem.MultipleObjectsReturned:
                print "\n---\nMultipleObjectsReturned when tried to update!"
                DeleteEntry(int(entry.ean))
                
            except AffiliationItem.DoesNotExist:
                print "\n---\nDoesNotExist when tried to update!"
            
        else:#entree n'existe pas => on la cree
            #print "\n---\nPK test before saving:", entry.pk, "\n---\n"
            
            entry.save()
            
            print "\n---\nEntry: ", entry.name_at_store
            print " has been created\n---\n"
            
            #entry is re-initiated so that it gets a new PK
            entry = AffiliationItem()
            entry.item_id = 1
            entry.store_id = 1
            
    

    if ean_in_db: #If EAN was in DB and hasn't been updated = not in catalog anymore => to delete
        print("\n There is(are) a remaining EAN in db !\n")
        for ean in ean_in_db:
            DeleteEntry(ean)
        print "\n---\nHere is the 'ean_in_db' that remained: \n"
        print ean_in_db, "\n---\n"
                    
    
    print "\n---\nEnd of catalog import. Everything seems to have worked "
    print "correctly\n---\n"
    
if __name__ == "__main__":
    main()
    