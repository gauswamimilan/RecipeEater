from bs4 import BeautifulSoup
import requests
import re
import db_helper


def get_soup_result(url):
    try:
        soup_result = requests.get(url)
        soup = BeautifulSoup(soup_result.content, "html.parser")
        return soup
    except:
        return False


def get_recipe_name(soup):
    return soup.find("h1", {"id": "article-heading_2-0"}).text.strip().lower()


def get_ingredients(soup):
    result_dict = {"type": "", "data": []}

    ingredients = soup.find("div", {"id": "mntl-structured-ingredients_1-0"})
    ingredient_classes = ingredients.find_all(
        "p", {"class": "mntl-structured-ingredients__list-heading type--goat-bold"}
    )
    type_of_ingredient = "list"

    if len(ingredient_classes) > 0:
        type_of_ingredient = "iterative"
    print(type_of_ingredient)

    if type_of_ingredient == "list":
        ingredient_result_list = []
        ingredients_list = ingredients.find_all("p")
        for single_ingredient in ingredients_list:
            ingredient_division = single_ingredient.find_all("span")
            if len(ingredient_division) == 3:
                quantity = ingredient_division[0].text.strip()
                unit = ingredient_division[1].text
                ingredient = ingredient_division[2].text
                result_dict = {
                    "quantity": quantity,
                    "unit": unit,
                    "ingredient": ingredient,
                    "original": single_ingredient.text,
                }
                ingredient_result_list.append(result_dict)
            else:
                print(len(ingredient_division))
        result_dict = {"type": type_of_ingredient, "data": ingredient_result_list}
    elif type_of_ingredient == "iterative":
        ingredient_categories = [
            i.text.strip(": ").lower()
            for i in ingredients.find_all(
                "p",
                {"class": "mntl-structured-ingredients__list-heading type--goat-bold"},
            )
        ]
        ingredient_categorical_list = []
        for single_category in ingredients.find_all("ul"):
            tmp_ingredients_list = []
            ingredients_list = single_category.find_all("p")
            for single_ingredient in ingredients_list:
                ingredient_division = single_ingredient.find_all("span")
                if len(ingredient_division) == 3:
                    quantity = ingredient_division[0].text.strip()
                    unit = ingredient_division[1].text
                    ingredient = ingredient_division[2].text
                    result_dict = {
                        "quantity": quantity,
                        "unit": unit,
                        "ingredient": ingredient,
                        "original": single_ingredient.text,
                    }
                    tmp_ingredients_list.append(result_dict)
                    # print(result_dict)
                else:
                    print(len(ingredient_division))
            ingredient_categorical_list.append(tmp_ingredients_list)
        result_dict = {"type": type_of_ingredient, "data": {}}
        for i, value in enumerate(ingredient_categories):
            result_dict["data"][value] = ingredient_categorical_list[i]
    else:
        print("Error No ingredients found")
    return result_dict


def get_recipe_steps(soup):
    recipe_steps = soup.find("div", {"id": "recipe__steps-content_1-0"})
    recipe_steps = [i.find("p").text.strip() for i in recipe_steps.find_all("li")]
    return recipe_steps


def get_nutrician_facts(soup):
    result_nutrician_facts = {}
    nutrician_facts = soup.find("div", {"id": "mntl-nutrition-facts-summary_1-0"})
    nutrician_facts = nutrician_facts.find_all("tr")
    for single_row in nutrician_facts:
        nutrician_values = [i.text.strip().lower() for i in single_row.find_all("td")]
        result_nutrician_facts[nutrician_values[1]] = nutrician_values[0]
    return result_nutrician_facts


def get_recipe_details(soup):
    result_recipe_details = {}
    recipe_details = soup.find("div", {"id": "recipe-details_1-0"})
    recipe_details = recipe_details.find_all(
        "div", {"class": "mntl-recipe-details__item"}
    )
    for single_row in recipe_details:
        tmp_reveipe_values = [
            i.text.strip(" :").lower() for i in single_row.find_all("div")
        ]
        result_recipe_details[tmp_reveipe_values[0]] = tmp_reveipe_values[1]

    return result_recipe_details


def get_recipe_review(soup):
    result_recipe_details = {}

    result_recipe_details["rating"] = (
        soup.find("div", {"id": "mntl-recipe-review-bar__rating_2-0"})
        .text.strip()
        .lower()
    )
    result_recipe_details["no_of_rating"] = (
        soup.find("div", {"id": "mntl-recipe-review-bar__rating-count_2-0"})
        .text.strip(" ()\n")
        .lower()
    )
    result_recipe_details["no_of_reviews"] = (
        soup.find("div", {"id": "mntl-recipe-review-bar__comment-count_2-0"})
        .text.split(" ")[0]
        .strip()
        .lower()
    )

    doc_id = soup.find("button", {"id": "mntl-save__link_3-0"}).attrs["data-doc-id"]

    url = f"https://www.allrecipes.com/servemodel/model.json?modelId=feedbacks&docId={doc_id}&sort=HELPFULCOUNT_DESC&offset=0&limit=9"
    result = requests.get(url).json()

    regex_remove_tags = re.compile("<.*?>")
    result = [re.sub(regex_remove_tags, "", i["review"]) for i in result["list"]]
    result_recipe_details["helpful_reviews"] = result

    return result_recipe_details


def insert_new_url(url):
    try:
        url = url.lower().strip().strip("\/")
        regex = re.compile(
            r"https\:\/\/www\.allrecipes\.com\/recipe\/[0-9]+" r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if re.match(regex, url) is not None:

            result = db_helper.query_a_record("url", url)
            if len(result) > 0:
                return result[0]

            soup = get_soup_result(url)
            if soup is False:
                return False

            recipe_result = {
                "url": url,
                "recipe_name": get_recipe_name(soup),
                "details": get_recipe_details(soup),
                "ingredients": get_ingredients(soup),
                "recipe_steps": get_recipe_steps(soup),
                "nutrician_facts": get_nutrician_facts(soup),
                "recipe_review": get_recipe_review(soup),
            }
        else:
            return False
        db_helper.client["RecipeEater"]["recipes"].insert_one(recipe_result)
        db_helper.all_recipes_names.append(recipe_result["recipe_name"])

        return recipe_result
    except Exception as e:
        print(e)
        return False
