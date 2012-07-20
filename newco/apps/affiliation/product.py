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
    print("\nEnter in ImportDecatWeb\n")
    csvfile = urlopen(address)
    csvdialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=';')
    #csvfile.seek(0)
    csvfile = urlopen(address) ## Seb: I reopen the file because urlopen doesn't provide a way to position the "cursor" like ".seek()" , it's not performant, but as a quickfix it works.
    
    return csv.DictReader(csvfile,
                          dialect=csvdialect)
    

def main():
    address = "http://flux.netaffiliation.com/catalogue.php?maff=A6AB58DCS569B4B545AF92191v3"
    decat_catalog = ImportDecat(address)

    ean_in_db = list(AffiliationItem.objects.all().values_list('ean', flat=True)) #faire un "list()" pour forcer l'évaluation une seule fois?
    
    entry = AffiliationItem()
    entry.item_id = 1 #Item.objects.get(pk=1)
    entry.store_id = 1 #Store.objects.get(pk=1)
    
    for row in decat_catalog:
        for key, value in row.items():
            print key, " : ", value
            if key == "Prix":
                entry.price = Decimal(value.replace(",",".")).quantize(Decimal('0.01'))
            elif key == "Url":
                entry.url = value
            elif key == "Url image grande":
                entry.url_img = value
            elif key == "EAN":
                entry.ean = value
            elif key == "Nom":
                entry.name_at_store = value
        
        #faire une liste de tout le catalogue au préalable et comparer entre les 2 listes plutôt ... ?
        if int(entry.ean) in ean_in_db: #entree existe => on la met a jour
            try:
                entry.pk = AffiliationItem.objects.get(ean=entry.ean).pk
                entry.save()
                
            except AffiliationItem.MultipleObjectsReturned:
                print("multiple objects returned !")
                entries_to_del = AffiliationItem.objects.filter(ean=entry.ean)
                for entry_to_del in entries_to_del:
                    print("One entry is on the death row")
                    pk_test = entry_to_del.pk
                    entry_to_del.delete()
                    
                    try:
                        AffiliationItem.objects.get(pk=pk_test)
                        print("shit still remains entry(ies)")
                        print(pk_test)
                    except AffiliationItem.MultipleObjectsReturned:
                        print("Shit, still not deleted ...")
                        print(pk_test)
                    except AffiliationItem.DoesNotExist:
                        print("cool it seems it has been deleted !")
                
            
            ean_in_db.pop(ean_in_db.index(int(entry.ean)))
            #print "The following EAN has been poped: ", ean_in_db.pop(ean_in_db.index(int(entry.ean)))
            print("\n The entry existed and has been updated \n")
            
        else:#entree n'existe pas => on la cree
            print("\n\n\n\n PK test before saving  \n\n\n\n")
            print(entry.pk)
            
            entry.save()
            
            entry = AffiliationItem()
            entry.item_id = 1
            entry.store_id = 1
            
            print("\n\n\n\n An object has been created \n\n\n\n")
            print(entry.pk)
#            AffiliationItem.objects.create(name_at_store=entry.name_at_store,
#                         url=entry.url, url_img=entry.url_img,
#                         price=entry.price, ean=entry.ean,
#                         item=entry.item, store=entry.store)
        
        
        ## break for testing purposes
    
    ###faire une boucle qui cherche les entrées qui n'existent plus
    if ean_in_db:
        print("\n There is(are) a remaining EAN in db !\n")
        for ean in ean_in_db:
            print("Entered in ean delete loop")
            
            try:
                entry_death_row = AffiliationItem.objects.get(ean=ean)
                entry_death_row.delete()
                
            except AffiliationItem.MultipleObjectsReturned:
                print("\n\n\n\nMultiple objects returned - in delete loop !\n\n\n")
                #ici on veut tout deleter, mieux vaut trop deleter que de laisser la base grossir dans ce cas.
                entries_to_del = AffiliationItem.objects.filter(ean=ean)
                for entry in entries_to_del:
                    print("One entry is on the death row")
                    entry.delete()
                    
    
    print "\n\n\n End of 'for' loop. \n\n"
    
    print "\n\n\n Here is the 'ean_in_db' that remained: \n\n"
    print ean_in_db
if __name__ == "__main__":
    main()
    