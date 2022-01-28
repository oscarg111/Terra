#Import all packages needed
import requests
from difflib import SequenceMatcher as sm
import urllib.request
import simplejson
import geocoder
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

#global variables
barcode_spider_api_key = "****************"
material_file = "materials.txt"
material_array = ""
wms_url = "https://www.google.com/search?q="
earth911_url = 'http://api.earth911.com/'
earth911_api_key = '****************'
wms_product_search = '+"packaging material"'
geocoder = Nominatim(user_agent="geoapiExercises")
geocode = RateLimiter(geocoder.geocode,min_delay_seconds = 1, return_value_on_exception = None)
about_us = ""
splash = '''

████████ ███████ ██████  ██████   █████  
   ██    ██      ██   ██ ██   ██ ██   ██ 
   ██    █████   ██████  ██████  ███████ 
   ██    ██      ██   ██ ██   ██ ██   ██ 
   ██    ███████ ██   ██ ██   ██ ██   ██ 
                                         
                                         
                                                    
'''

#Similarity recognition function
def similar(a, b):
    return sm(None, a, b).ratio()




#Opening the materials.txt file
def readMaterialFile(filename):
    try:
        text_file = open(filename, "r")
        lines = text_file.read().splitlines()
        text_file.close()
        return lines
    except(FileNotFoundError):
        return['-1']

material_array = (readMaterialFile(material_file))


#This code recieves a upc barcode string and searches it on barcode spider using their API
def BarcodeProduct(barcode,api):

    barcode_url = "https://api.barcodespider.com/v1/lookup"

    barcode_query = {"upc":barcode}

    barcode_headers = {
        'token': api,
        'Host': "api.barcodespider.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
        }
    try:
        barcode_response = requests.request("GET", barcode_url, headers=barcode_headers, params=barcode_query)

        barcode_api_response = barcode_response.json()

        product_data = barcode_api_response['item_attributes']
        manu = product_data['manufacturer']
        brand = product_data['brand']
        product_description = product_data['description'] + " " + product_data['category'] + " " + product_data['title'] + " " + product_data['parent_category'] + " " + product_data['category']

        #product_description = str(product_data)
        #product_data
        return {"manu": manu, "brand": brand, "description": barcode, "temp1": product_data['description']}
    except(KeyError):
        return {"manu": "00000", "brand": "00000", "description": "00000", "temp1": "00000"}
    except(requests.ConnectionError):
        return{"manu": "11111", "brand": "11111", "description": "11111", "temp1": "11111"}


#print(BarcodeProduct("049000051995",barcode_spider_api_key))

# Web material search
def getMaterial(brand, barcode_result):
    material_array_hit = [0] * len(material_array)
    brand = brand.replace(" ", "+")
    brand = brand.lower()
    largest_instance = ""
    largest_instance_num = 0
    page = requests.get(wms_url + barcode_result + wms_product_search  + " " + brand )

    if(int(page.status_code)!= 200):
        return 0
    content = str(page.text)

    
     
    content_array = content.split()

    for ma in material_array:
        for ca in content_array:
            if (similar(ma, ca) > 0.75):
                material_array_hit[material_array.index(ma)] += 1
                #print(ma + " : " + str(material_array_hit[material_array.index(ma)])+ " : " + str(similar(ma,ca)) + "           " + ca)
                #if (content.count(ma)>largest_instance_num):
                    #largest_instance_num = content.count(ma)
                    #largest_instance = ma
    largest_instance = (material_array[material_array_hit.index(max(material_array_hit))])
    if (largest_instance == material_array[0]):
        return "22222"
    print("Most Likely Material the Product is Made of is: " + largest_instance)
    while(True):
        overide = input("Is this correct? (y/n): ")
        if (overide == "y"):
            return largest_instance

        if (overide == "n"):
            for ov in range(len(material_array)):
                print(str(ov) + " : " + material_array[ov])
            print("Please choose a material from this list using the number listed beside the item (ex. 1 : Plastic):\n")

            while(True):
                try:
                    return material_array[int(input(">"))]
                except:
                    print("Invalid ID")
    
        print("Invalid Option")
       



    #print("Result: " + largest_instance)       
        

#getMaterial("Horizon Milk")

#Test barcode: 049000028904


def searchEarth911Products(item):
    earth911_query = (earth911_url + 'earth911.getProductDetails?api_key=' + earth911_api_key +'&upc=' + item)
    text = urllib.request.urlopen(earth911_query).read()
    result = simplejson.loads(text)
    if 'error' in result:
        return 0 
    else:
        return result['result']

#Earth911 Search
def searchEarth911(item, lat, lon):
    item = item.replace(' ', '+')
    earth911_query = (earth911_url + 'earth911.searchMaterials?api_key=' + earth911_api_key +'&query=' + item + '&max_results=1')

    text = urllib.request.urlopen(earth911_query).read()
    result = simplejson.loads(text)
    if 'error' in result:
        return 0
    
    found_material = result['result']
    found_materialv2 = found_material[0]
    found_materialv3 = found_materialv2['material_id']
    print("Searching Database, please wait, the system takes about a minute to search.")
    earth911_location_query = (earth911_url + 'earth911.searchLocations?api_key=' + earth911_api_key + '&latitude=' + str(lat) + '&longitude=' + str(lon) + '&material_id=' + str(found_materialv3))
    
    text = urllib.request.urlopen(earth911_location_query).read()

    result = simplejson.loads(text)
    if 'error' in result:
        return 0
    else:
        print("")
        for res in result['result']:
            #try:
            #print(res['description'])
                
            print("\nFound a result:\n" + "Location: " + res['description'] + "\nDistance from city center: " + str(res['distance']) + "mi.\nIs it curbside?: " + str(res['curbside']))

            #except:
                #print("")

    

#Main Menu
print(splash + "By: Gabriel, 1/13/2022")
while(True):
    option = input("\nPlease Select an Option \nSearch for Product (s) \nAbout Us (a) \n>")
    optionlist = ['s', 'a']

    if(option == optionlist[0]):
        print(" \nProduct Search\n ")
       
        location = geocode(input("Input your city of residence (ex: Fairfax, VA): "))
        location_data = location.raw
        time.sleep(1)

        userinput = input("\nInput Product Barcode: ")
        print("Searching History. . .")
        earth911output = searchEarth911Products(userinput)
        if(len(earth911output) == 0):
            print("did not find in history, searching the internet. . . .")
            product_data = BarcodeProduct(userinput, barcode_spider_api_key)
            
            if(product_data == {"manu": "11111", "brand": "11111", "description": "11111", "temp1": "11111"}):
                print("No Internet Connection, please check your modem or router and try again")
            elif(product_data == {"manu": "00000", "brand": "00000", "description": "00000", "temp1": "00000"}):
                print("UPC barcode not found in database, please try again")
            else:
                print("\nHere is what I found: \nManufacturer: " + product_data["manu"] + "\nBrand: " + product_data["brand"] + "\n" + "Description from database:\n " + product_data['temp1'])

                likely_material = getMaterial(product_data["manu"], product_data["description"])
                print(likely_material)
                if(likely_material == 0):
                    print("Website did not respond, check your internet connection and try again")
                else:
                    if (likely_material == "22222"):
                        print("Item can not be confirmed as recyclable or not, please check manually. Sorry for the inconvience.")
                    else:
                        print("Searching Material {0} in Database: ".format(likely_material))
                        searchEarth911(likely_material, str(location_data['lat']), str(location_data['lon']))
                    print("\n_________________________________\n")
                    
                    
        else:
            print(earth911output)

      
    elif(option == optionlist[1]):
        print(about_us)
    
        
    else:
        print("Not Valid")
        
    print("_________________________________")


