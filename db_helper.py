from tinydb import TinyDB, Query
import requests
import xmltodict
import re
from data_extraction import insert_new_url
import pymongo
import os


url = os.environ.get("mongodb_url")
client = pymongo.MongoClient(url)


all_recipes_names = []

for i in client["RecipeEater"]["recipes"].find({}):
    all_recipes_names.append(i["recipe_name"])


def insert_sitemap_for_recipe(sitemap_url):
    result = requests.get(sitemap_url).text
    my_dict = xmltodict.parse(result)
    url_list = []   

    for single_url in my_dict["urlset"]["url"]:
        if re.search(
            "https\:\/\/www\.allrecipes\.com\/recipe\/[0-9]+\/[^\/]*\/",
            single_url["loc"],
        ):
            url_list.append({"loc": single_url["loc"]})
    client["RecipeEater"]["recipe_urls"].insert_many(url_list)


def insert_recipe_into_db(json_data):
    client["RecipeEater"]["recipes"].insert_one(json_data)


def query_a_record(key, value):
    result = list(client["RecipeEater"]["recipes"].find({key: value},{"_id": 0}))
    result = result
    return result


def onetime_get_data_from_sitemaps():
    insert_sitemap_for_recipe("https://www.allrecipes.com/sitemap_1.xml")
    insert_sitemap_for_recipe("https://www.allrecipes.com/sitemap_2.xml")
    insert_sitemap_for_recipe("https://www.allrecipes.com/sitemap_3.xml")
    insert_sitemap_for_recipe("https://www.allrecipes.com/sitemap_4.xml")


def onetime_insert_recipes():
    count = 0
    for single_record in client["RecipeEater"]["recipe_urls"].find({}):
        try:
            count = count + 1
            if count > 10000:
                break

            insert_new_url(single_record["loc"])
        except Exception as e:
            print(single_record["loc"])
            print(e)
