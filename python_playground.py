from country_list import countries_for_language

all_countries = [{k: v} for (k, v) in dict(countries_for_language('en')).items()]
print(all_countries)