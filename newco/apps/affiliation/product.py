# -*- coding: utf-8 -*-
import csv, sys, pprint
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
#    try:
#        catalogue_decat = ImportDecat(sys.argv[1])
#    except:
    address = "http://flux.netaffiliation.com/catalogue.php?maff=A6AB58DCS569B4B545AF92191v3"
    catalogue_decat = ImportDecat(address)

    row = next(catalogue_decat)
    #for ... in catalogue_decat:
    #for :
    for key, value in row.items():
        print key, " : ", value
        
        if key == "Prix":
            price = int(float(value.replace(",",".")))
            
        elif key == "Url":
            url = value
            
        elif key == "Url image grande":
            url_img_grd = value
        
        elif key == "Nom":
            print("\nEnter in the key='Nom'\n")
            name_at_store = value
            #ref = AffiliationItem(name_at_store=value)
                        #ref.item =
            #ref.price =
            # 
            #ref.save()
            
    item = Item.objects.get(pk=1)
    store = Store.objects.get(pk=1)
    AffiliationItem.objects.create(name_at_store=name_at_store,
                     url=url, url_img=url_img_grd, price=price,
                     item=item, store=store)

    
    print next(catalogue_decat)
    
    
    
    print "\n\n\n Separation between 'for' loop and 'pretty print'.\n\n"
    
    
    pprint.pprint(catalogue_decat.fieldnames)  

if __name__ == "__main__":
    main()
    