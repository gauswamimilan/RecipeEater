import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_md")

stop_list = ["much", "what", "many"]

matcher = Matcher(nlp.vocab)
next_step = [{"DEP": "advmod", "OP": "?"}, {"DEP": "amod"}, {"POS": "NOUN"}]
next_step_2 = [
    {"POS": "PRON"},
    {"DEP": "prep", "OP": "?"},
    {"POS": "NOUN", "DEP": "pobj"},
]
next_step_3 = [
    {"POS": "NOUN"},
    {"DEP": "prep", "OP": "?"},
    {"POS": "NOUN", "DEP": "pobj"},
]
next_step_4 = [
    {"POS": "NOUN"},
    {"POS": "ADP", "DEP": "prep"},
]
next_step_5 = [{"POS": "VERB"}, {"POS": "DET"}, {"POS": "NUM", "DEP": "npadvmod"}]
matcher.add(
    "next_step", [next_step, next_step_2, next_step_3, next_step_4, next_step_5]
)


nutrician_fact_1 = [{"DEP": "advmod", "OP": "?"}, {"DEP": "amod"}, {"POS": "NOUN"}]
nutrician_fact_3 = [{"DEP": "advmod", "OP": "?"}, {"DEP": "amod"}, {"DEP": "ROOT"}]
nutrician_fact_2 = [{"DEP": "advmod"}, {"DEP": "advmod"}, {"POS": "NOUN"}]
nutrician_fact_4 = [{"POS": "NOUN"}, {"DEP": "prep", "OP": "?"}, {"POS": "NOUN"}]
# What is serve quantity
nutrician_fact_5 = [
    {"POS": "PRON"},
    {"POS": "AUX"},
    {"POS": "DET", "OP": "?"},
    {"POS": "NOUN"},
]
matcher.add(
    "nutrician_fact",
    [
        nutrician_fact_1,
        nutrician_fact_2,
        nutrician_fact_3,
        nutrician_fact_4,
        nutrician_fact_5,
    ],
)


# What is serve quantity
recipe_details_4 = [
    {"POS": "PRON"},
    {"POS": "AUX"},
    {"POS": "DET", "OP": "?"},
    {"POS": "NOUN"},
]
recipe_details_5 = [{"POS": "NOUN"}, {"DEP": "prep", "OP": "?"}, {"POS": "NOUN"}]
# how much is no of servings
recipe_details_1 = [{"POS": "PRON"}, {"DEP": "prep"}, {"POS": "NOUN", "DEP": "pobj"}]
# what is total time
recipe_details_3 = [{"DEP": "amod"}, {"POS": "NOUN"}]
# what is prepartion time
recipe_details_2 = [{"DEP": "compound"}, {"POS": "NOUN"}]
matcher.add(
    "recipe_details",
    [
        recipe_details_5,
        recipe_details_4,
        recipe_details_1,
        recipe_details_2,
        recipe_details_3,
    ],
)


# What is the previous step of Make pumpkin layer
step_search_ingredient = [{"DEP": "compound"}, {"POS": "NOUN"}]
matcher.add("step_search", [step_search_ingredient])


# Can it be cooked without an oven?


# What is the quantity of schezwan sauce
# how much schezwan sauce do i need
# how much white sugar do i need
ingredient_search_1 = [{"DEP": "pobj", "POS": "NOUN"}]
ingredient_search_2 = [{"DEP": "dobj", "POS": "NOUN"}]
ingredient_search_3 = [{"DEP": "compound", "OP": "?"}, {"DEP": "pobj", "POS": "NOUN"}]
ingredient_search_4 = [{"DEP": "compound", "OP": "?"}, {"DEP": "dobj", "POS": "NOUN"}]
ingredient_search_5 = [{"DEP": "amod", "POS": "ADJ"}, {"DEP": "pobj", "POS": "NOUN"}]
ingredient_search_6 = [{"DEP": "amod", "POS": "ADJ"}, {"DEP": "dobj", "POS": "NOUN"}]
matcher.add(
    "ingredient_search",
    [
        ingredient_search_1,
        ingredient_search_2,
        ingredient_search_3,
        ingredient_search_4,
        ingredient_search_5,
        ingredient_search_6,
    ],
)


def find_matcher_output(match_rule, input_text):
    doc = nlp(input_text)
    result_text = []
    matches = matcher(doc)
    matches = [
        single_match
        for single_match in matches
        if nlp.vocab.strings[single_match[0]] == match_rule
    ]
    match_results = []
    for match_id, start, end in matches:
        result_text = [i.lemma_ for i in doc[start:end]]
        stop_list = ["much", "what", "many"]
        if len(list(set(stop_list) & set(result_text))) > 0:
            continue
        if len(match_results) < len(result_text):
            match_results = result_text
    if len(match_results) > 0:
        return match_results
    return False


input_sentence = ["what is step after boiling point"]
error_reply = [
    "I am unable to understand this, if you want to know the serve quantity number ask 'What is the number of serving' ",
    "I am unable to understand this, if you want to go to the next step then say 'what is the next step' ",
    "I am unable to understand this, if you want to go back to previous step, say 'what the previous step?' ",
    "I am unable to understand this, if you want to know the ingredients ask 'what are the ingredients'",
    "I am unable to understand this, if you want to know the cook time ask what is the cook time?",
    "I am unable to understand this, if you want to know the prep time ask 'what is the prep time?'",
]
pre_tagged = [nlp(i) for i in error_reply]


def handle_error_input(input_text):
    print("inside handle_error_input")
    reply_message = ""
    max_simmiliarity = 0
    for single_message in pre_tagged:
        simmiliarity = nlp(input_text).similarity(single_message)
        if simmiliarity > max_simmiliarity:
            max_simmiliarity = simmiliarity
            reply_message = single_message
    return str(reply_message)


"""
sample questions 
Please forward this mail to the class.

Let us consider the recipe described in 
1.
https://recipes.timesofindia.com/recipes/fiery-drumsticks/rs95140230.cms

Sample questions:
 Q: What is the quantity of schezwan sauce?
A: 3 tablespoon
Q: What is the next step after preheating the oven?
A:  Mix it all
Next , take a large bowl and mix all the ingredinets and sauces, whisk it well and add chopped corinader leaves.
Q: Can it be cooked without an oven?
A: No

2.
https://www.allrecipes.com/recipe/13804/pumpkin-crumb-cake/

Q: What are the ingredients for pumpkin layer?
A: 1 (15 ounce) can pumpkin puree
½ cup white sugar
¼ cup packed brown sugar
3 large eggs, beaten
1 ½ teaspoons ground cinnamon
Q: What is the previous step of Make pumpkin layer?
A: Make crust: Measure 1 cup cake mix into a medium bowl; set aside for topping. Combine remaining cake mix, melted butter, and egg in a large bowl; mix until well combined. Pat mixture into the bottom of the prepared pan.

"""
