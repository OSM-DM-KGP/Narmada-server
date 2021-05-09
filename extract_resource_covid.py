text_org = input("Enter text, or press return for an example: ")
import location
import pudb
if text_org == "":
    text_org = "Oxygen producing unit at Princess Esra Hospital (Owaisi Group of Hospitals). #Oxygen #IndiaNeedsOxygen #IndiaFightsCOVID19 @aimim_national @imShaukatAli @asadowaisi @imAkbarOwaisi  @warispathan @syedasimwaqar @Syed_Ruknuddin5 @ShahnawazAIMIM_ @Akhtaruliman5  https://t.co/vdZamB1wJl"
text = text_org.lower()

places = location.return_location_list(text)
each_loc = [place[0] for place in places]
resources = {
    "oxygen": "Oxygen",
    "o2": "Oxygen",
    "ventilator": "Ventilator",
    "bed": "Beds",
    "icu": "Beds",
    "remdes": "Remdesivir",
    "plasma": "Plasma",
    "consultation": "Doctor"
}

places_to_remove = []
resource_text = ""
for resource in resources:
    if resource in each_loc:
        places_to_remove.append(each_loc.index(resource))
    if resource in text:
        resource_text = resource_text+resources[resource]+" "

places_to_remove.sort(reverse=True)
for ptr in places_to_remove:
    del places[ptr]

print("\n\n\nText: "+str(text_org))
print("\nLocation: "+str(places))
print("\nResources: "+resource_text)