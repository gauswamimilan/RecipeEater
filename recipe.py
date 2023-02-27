from config import *
from db_helper import *
from data_extraction import insert_new_url
from recipe_helper_classes import (
    RecipeDetails,
    Recipeingredients,
    RecipeSteps,
    RecipeReview,
    RecipeNutricianFacts,
    RecipeFunctionHelper,
)

currently_opened_recipe = {}


class Recipe(
    RecipeDetails,
    Recipeingredients,
    RecipeSteps,
    RecipeReview,
    RecipeNutricianFacts,
    RecipeFunctionHelper,
):
    recipe_selected: bool = False
    recipe_json: dict
    unique_id: str
    recipe_name: str

    def __init__(self, unique_id):
        self.unique_id = unique_id
        super().__init__()

    def __str__(self):
        return self.unique_id

    def initialize_recipe(self, recipe):
        self.recipe_name = recipe["recipe_name"]

        self.select_recipe_details(recipe)
        self.select_ingredients(recipe)
        self.select_recipe_steps(recipe)
        self.select_recipe_review(recipe)
        self.select_recipe_facts(recipe)

        if self.recipe_selected != True:
            self.recipe_selected = True
            return f'You have selected "{self.recipe_name}" recipe, you can ask "go to step one" or "what are ingredients"'
        else:
            return f'You have changed to "{self.recipe_name}" recipe, you can ask "go to step one" or "what are ingredients"'

    def search_a_recipe(self, input_text):
        print("inside search_a_recipe")
        input_text = input_text.strip()
        input_text = re.sub("[^A-Za-z0-9 ]+", "", input_text)
        input_text = input_text.split(" ")
        tmp_all_strings = all_recipes_names.copy()
        for single_string in input_text:
            p = re.compile(single_string, re.IGNORECASE)
            tmp_all_strings = [i for i in tmp_all_strings if p.search(i)]

        if len(tmp_all_strings) > 0:
            return self.select_a_recipe(tmp_all_strings[0])

        tmp_all_strings = [i["loc"] for i in client["RecipeEater"]["recipe_urls"].find({})]
        for single_string in input_text:
            p = re.compile(single_string, re.IGNORECASE)
            tmp_all_strings = [i for i in tmp_all_strings if p.search(i)]

        if len(tmp_all_strings) > 0:
            return self.create_new_recipe(tmp_all_strings[0])

        return "Recipe not found, Please try again"

    def select_a_recipe(self, input_text):
        input_text = input_text.replace("select:", "")
        if input_text in all_recipes_names:
            result = query_a_record("recipe_name", input_text)
            if len(result) > 0:
                result = result[0]
                return self.initialize_recipe(result)
        return "Error in selecting recipe"

    def create_new_recipe(self, input_text):
        print("inside search_a_recipe")
        input_text = input_text.replace("url:", "")
        url_result = insert_new_url(input_text)
        if url_result == False:
            return f"url:{input_text} is invalid"
        input_text = url_result["recipe_name"]
        return self.select_a_recipe(input_text)

    def parse_text(self, input_text: str):
        # Do it here
        if self.recipe_selected == False:
            search_regex = self.regex_match_recipe(input_text)
            if search_regex:
                return self.search_a_recipe(search_regex)
            if input_text.startswith("select:"):
                return self.select_a_recipe(input_text)
            if input_text.startswith("url:"):
                return self.create_new_recipe(input_text)
            
            search_regex = self.regex_match_change_recipe(input_text)
            if search_regex:
                return self.search_a_recipe(search_regex)
            return 'To search for recipe say it like "Find pumpkin crumb cake recipe" or "How to make pumpkin crumb cake"'
        else:
            search_regex = self.regex_match_change_recipe(input_text)
            if search_regex:
                return self.search_a_recipe(search_regex)
            return self.split_input_in_type_of_question(input_text)
