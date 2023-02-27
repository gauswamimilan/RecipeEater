import json
import re
from config import *
import pdb
from word2number import w2n


class RecipeFunctionHelper:
    question_type_to_function: dict = {}

    def __init__(self):
        self.question_type_to_function = {
            "how many": self.answer_how_many_question,
            "how much": self.answer_how_many_question,
            "what": self.answer_what_question,
            "how": self.answer_other_questions,
            "can": self.answer_other_questions,
        }

    def regex_match_recipe(self, input_text):
        print(f"inside regex_match_recipe")
        regex_recipe_list = [
            "(find|search|select|show) (me|for) (a|an) (?P<search_term>.*) recipe",
            "(find|search|select|show) (a|an|me|for) (?P<search_term>.*) recipe",
            "(find|search|select|show) (?P<search_term>.*) recipe",
            "(how to|lets) make (?P<search_term>.*) recipe",
            "(find|search|select|show) (me|for) (a|an) (?P<search_term>.*)",
            "(find|search|select|show) (a|an|me|for) (?P<search_term>.*)",
            "(find|search|select|show) (?P<search_term>.*)",
            "(how to|lets) make (?P<search_term>.*)",
        ]
        for single_regex_recipe in regex_recipe_list:
            result = re.search(single_regex_recipe, input_text, re.IGNORECASE)
            if not result:
                continue
            result = result.groupdict()
            if result.get("search_term"):
                return result.get("search_term")
        return False

    def regex_match_step_search(self, input_text):
        print(f"inside regex_match_step_search")
        regex_recipe_list = [
            " (step) (?P<search_indicator>[a-zA-Z]+) (?P<search_term>.+) (|in this |in )(recipe|this)",
            " (step) (?P<search_indicator>[a-zA-Z]+) (?P<search_term>.+)",
        ]
        for single_regex_recipe in regex_recipe_list:
            result = re.search(single_regex_recipe, input_text, re.IGNORECASE)
            if not result:
                continue
            result = result.groupdict()
            if result.get("search_term"):
                return [result.get("search_indicator"), result.get("search_term")]
        return False

    def regex_match_change_recipe(self, input_text):
        print(f"inside regex_match_change_recipe")
        regex_recipe_list = [
            "(change recipe to) (?P<search_term>.*)",
            "(change to) (?P<search_term>.*)",
        ]
        for single_regex_recipe in regex_recipe_list:
            result = re.search(single_regex_recipe, input_text, re.IGNORECASE)
            if not result:
                continue
            result = result.groupdict()
            if result.get("search_term"):
                return result.get("search_term")
        return False

    def split_input_in_type_of_question(self, input_text):
        type_of_question = list(self.question_type_to_function.keys())
        tmp_input_text = input_text.lower()

        print("splitting into input type")

        tmp_result = self.regex_match_nth_step(input_text)
        if tmp_result:
            return tmp_result

        tmp_result = self.get_recipe_step_search(input_text)
        if tmp_result:
            return tmp_result

        for single_type_of_question in type_of_question:
            if single_type_of_question in tmp_input_text:
                print(f"question type is {single_type_of_question}")
                return self.question_type_to_function[single_type_of_question](
                    input_text
                )
            if single_type_of_question.replace(" ", "") in tmp_input_text:
                print(f"question type is {single_type_of_question}")
                return self.question_type_to_function[single_type_of_question](
                    input_text
                )

        print(f"question type is other")
        return self.answer_other_questions(input_text)

    def answer_step_questions(self, input_text):
        print(f"inside answer_step_questions")
        print(input_text)
        match_result = find_matcher_output("next_step", input_text)
        print(match_result)
        if match_result:
            if "step" in match_result:
                result_match_dict = {
                    "next": [self.get_next_step, [input_text]],
                    "after": [self.get_next_step, [input_text]],
                    "previous": [self.get_previous_step, [input_text]],
                    "before": [self.get_previous_step, [input_text]],
                    "current": [self.get_current_step, []],
                    "repeat": [self.get_current_step, []],
                    "first": [self.get_nth_step, [1]],
                    "last": [self.get_nth_step, [self.total_steps]],
                    "no": [self.get_no_of_steps, []],
                    "number": [self.get_no_of_steps, []],
                }
                for key in result_match_dict.keys():
                    if key in match_result:
                        return result_match_dict[key][0](*result_match_dict[key][1])
        return False

    def answer_how_many_question(self, input_text):
        print("answer_how_many_question")

        matcher_result = find_matcher_output("nutrician_fact", input_text)
        if matcher_result:
            matcher_result = self.get_nutrician_fact(matcher_result[-1])
            if matcher_result:
                return matcher_result

        matcher_result = find_matcher_output("recipe_details", input_text)
        if matcher_result:
            matcher_result = self.get_recipe_details(matcher_result)
            if matcher_result:
                return matcher_result

        if "ingredient" in input_text:
            return self.show_ingredients()

        matcher_result = find_matcher_output("ingredient_search", input_text)
        if matcher_result:
            matcher_result = self.search_ingredient_details(matcher_result, input_text)
            if matcher_result:
                return matcher_result
        
        return handle_error_input(input_text=input_text)

    def regex_match_nth_step(self, input_text):
        print(f"inside regex_match_nth_step")
        regex_recipe_list = [
            "(go to|goto|jump to|show me) (?P<search_term>.*) step",
            "(go to|goto|jump to|show me) step(| no| number) (?P<search_term>[0-9A-Za-z]+)",
        ]
        for single_regex_recipe in regex_recipe_list:
            result = re.search(single_regex_recipe, input_text, re.IGNORECASE)
            if not result:
                continue
            result = result.groupdict().get("search_term")
            print("search result is ", result)

            tmp_result = self.answer_step_questions(
                " ".join(
                    [
                        result,
                        "step",
                    ]
                )
            )
            if tmp_result:
                return tmp_result

            if result:
                try:
                    if re.search("[0-9]+(th|nd|rd|st)", result):
                        result = re.sub("th|nd|rd|st", "", result)
                    result = w2n.word_to_num(result)
                    return self.get_nth_step(result)
                except Exception as e:
                    print(e)
                    return 'Invalid step number is given, try "go to step two" or try "show me step two"'
        return False

    def answer_other_questions(self, input_text):
        print(f"inside answer_other_questions")
        tmp_result = self.answer_step_questions(input_text)

        if tmp_result:
            return tmp_result

        if "ingredient" in input_text:
            return self.show_ingredients()
        
        return handle_error_input(input_text)

    def answer_what_question(self, input_text):
        print(f"inside answer_what_question")
        tmp_result = self.answer_step_questions(input_text)
        if tmp_result:
            return tmp_result

        matcher_result = find_matcher_output("nutrician_fact", input_text)
        if matcher_result:
            matcher_result = self.get_nutrician_fact(matcher_result[-1])
            if matcher_result:
                return matcher_result

        matcher_result = find_matcher_output("recipe_details", input_text)
        if matcher_result:
            matcher_result = self.get_recipe_details(matcher_result)
            if matcher_result:
                return matcher_result

        if "ingredient" in input_text:
            return self.show_ingredients()

        matcher_result = find_matcher_output("ingredient_search", input_text)
        if matcher_result:
            matcher_result = self.search_ingredient_details(matcher_result, input_text)
            if matcher_result:
                return matcher_result

        return handle_error_input(input_text=input_text)


class RecipeDetails:
    recipe_details: dict

    def select_recipe_details(self, recipe):
        self.recipe_details = recipe["details"]

    def get_recipe_details(self, key_list):
        print(f"inside get_recipe_details")
        keys = [" ".join(key_list), key_list[-1]]
        print(keys)
        recipe_key_dict_map = {
            "prep time": "prep time",
            "preparation time": "prep time",
            "cook time": "cook time",
            "total time": "total time",
            "serving": "servings",
            "yield": "yield",
        }
        for key in keys:
            if key in list(recipe_key_dict_map.keys()):
                tmp_result = self.recipe_details.get(recipe_key_dict_map[key])
                if tmp_result is None:
                    return f"For this recipe information about {recipe_key_dict_map[key]} does not exist"
                return f"For this recipe {recipe_key_dict_map[key]} is {tmp_result} "
        return False


class Recipeingredients:
    ingredients: dict

    def select_ingredients(self, recipe):
        recipe = json.dumps(recipe)
        # print(recipe)
        convert_to_number = [
            [r"([0-9]+) \\u2153", r"\1 and 1/3"],
            [r"([0-9]+) \\u00bc", r"\1 and 1/3"],
            [r"([0-9]+) \\u00bd", r"\1 and 1/2"],
            [r"([0-9]+) \\u00be", r"\1 and 3/4"],
            [r"\\u2153", r"1/3"],
            [r"\\u00bc", r"1/4"],
            [r"\\u00bd", r"1/2"],
            [r"\\u00be", r"3/4"],
        ]
        for single_regex in convert_to_number:
            recipe = re.sub(single_regex[0], single_regex[1], recipe)
        # print(recipe)
        recipe = json.loads(recipe)
        self.ingredients = recipe["ingredients"]

    def show_ingredients(self):
        print(f"inside show_ingredients")
        if self.ingredients["type"] == "list":
            result_str = "Ingredients are as follows:\n"
            for single_ingredient in self.ingredients["data"]:
                result_str = (
                    result_str
                    + single_ingredient["original"]
                    .encode(encoding="ascii", errors="ignore")
                    .decode()
                    + "\n"
                )
            return result_str.strip().replace("\n", "</br>")
        if self.ingredients["type"] == "iterative":
            ingredients_steps = list(self.ingredients["data"].keys())
            result_str = f"There are {len(ingredients_steps)} Steps for this recipe and ingredients for these steps are as follows \n"
            for i, single_ingredient_step in enumerate(self.ingredients["data"].keys()):
                result_str = result_str + f"\nStep {i+1}: {single_ingredient_step}\n"
                for single_ingredient in self.ingredients["data"][
                    single_ingredient_step
                ]:
                    result_str = (
                        result_str
                        + single_ingredient["original"]
                        .encode(encoding="ascii", errors="ignore")
                        .decode()
                        + "\n"
                    )
            return result_str.strip().replace("\n", "</br>")

    def search_ingredient_details(self, matcher, input_text):
        print("inside search_ingredient_details")
        if "much" in matcher: matcher.remove("much")
        if "many" in matcher: matcher.remove("many")
        print(matcher)
        matcher = " ".join(matcher)
        if self.ingredients["type"] == "list":
            for i, single_ingredient in enumerate(self.ingredients["data"]):
                if matcher in single_ingredient["original"]:
                    return f"You need {single_ingredient['original']} for this recipe"
        if self.ingredients["type"] == "iterative":
            for i, single_ingredient_step in enumerate(self.ingredients["data"].keys()):
                for single_ingredient in self.ingredients["data"][
                    single_ingredient_step
                ]:
                    if matcher in single_ingredient["original"]:
                        return f"You need {single_ingredient['original']} for this recipe"
        return False


class RecipeSteps:
    recipe_steps: list
    current_step = 0
    total_steps: int

    def select_recipe_steps(self, recipe):
        print(f"inside select_recipe_steps")
        self.recipe_steps = recipe["recipe_steps"]
        self.total_steps = len(self.recipe_steps)

    def get_next_step(self, input_text):
        print(f"inside get_next_step")
        matcher_result = find_matcher_output("step_search", input_text)
        if matcher_result:
            result_step = self.get_step_no_by_step(matcher_result)
            if result_step is not False:
                self.current_step = result_step

        if self.current_step + 1 >= self.total_steps:
            return 'You have completed recipe, You can say "Please Repeat current step" or "go to previous step"'
        self.current_step = self.current_step + 1
        return (
            f"Step: {self.current_step + 1} \n" + self.recipe_steps[self.current_step]
        )

    def get_current_step(self):
        print(f"inside get_current_step")
        return (
            f"Step: {self.current_step + 1} \n" + self.recipe_steps[self.current_step]
        )

    def get_no_of_steps(self):
        print(f"inside get_no_of_steps")
        return f"Total number of steps are {self.total_steps}"

    def get_nth_step(self, step_no):
        print(f"inside get_nth_step")
        step_no = step_no - 1
        if step_no >= self.total_steps:
            return f"recipe only have {self.total_steps} steps"
        if step_no <= 0:
            step_no = 0
        self.current_step = step_no
        return f"Step: {step_no + 1} \n" + self.recipe_steps[step_no]

    def get_previous_step(self, input_text):
        print(f"inside get_previous_step")
        matcher_result = find_matcher_output("step_search", input_text)
        if matcher_result:
            result_step = self.get_step_no_by_step(matcher_result)
            if result_step is not False:
                self.current_step = result_step

        if self.current_step - 1 < 0:
            return 'You are currently at first step, You can say "Please Repeat current step" or "go to previous step"'
        self.current_step = self.current_step - 1
        return (
            f"Step: {self.current_step + 1} \n" + self.recipe_steps[self.current_step]
        )

    def get_step_no_by_step(self, keywords: list):
        print(f"inside get_step_no_by_step")
        for step_no, step in enumerate(self.recipe_steps):
            count = 0
            for keyword in keywords:
                if keyword in step:
                    count = count + 1
            if count == len(keywords):
                return step_no
        return False

    def get_recipe_step_search(self, input_text):
        print("inside get_recipe_step_search")
        print(input_text)


        regex_result = self.regex_match_step_search(input_text)
        if regex_result:
            step_type = regex_result[0]
            search_term = str(regex_result[1]).lower()
            for i, single_step in enumerate(self.recipe_steps):
                if search_term in single_step.lower():
                    if step_type == "next" or step_type == "after":
                        return self.get_nth_step(i + 2)
                    if step_type == "previous" or step_type == "before":
                        return self.get_nth_step(i)
        return False


class RecipeReview:
    recipe_review: dict

    def select_recipe_review(self, recipe):
        self.recipe_review = recipe["recipe_review"]


class RecipeNutricianFacts:
    nutrician_facts: dict

    def select_recipe_facts(self, recipe):
        self.nutrician_facts = recipe["nutrician_facts"]

    def get_nutrician_fact(self, key):
        print(f"inside get_nutrician_fact")
        recipe_key_dict_map = {
            "calorie": "calories",
            "fat": "fat",
            "carb": "carbs",
            "protein": "protein",
        }
        if key in list(recipe_key_dict_map.keys()):
            nutrician_fact = self.nutrician_facts.get(recipe_key_dict_map[key])
            if nutrician_fact is None:
                return f"For this recipe information about {recipe_key_dict_map[key]} does not exist"
            return f"This recipe contains {nutrician_fact} {recipe_key_dict_map[key]}"
        return False
