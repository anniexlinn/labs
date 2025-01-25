"""
6.101 Lab 5:
Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!

def atomic_ingredient_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    atomic = {}
    # find atomic foods and add them along with costs to dict
    for item in recipes:
        f_type, food, cost = item[0], item[1], item[2]
        if f_type == "atomic" and food not in atomic:
            atomic[food] = cost
    return atomic


def compound_ingredient_possibilities(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    compound = {}
    for item in recipes:
        f_type, food, ingredients_list = item[0], item[1], item[2]
        # if food type is compound add to dictionary
        if f_type == "compound":
            if food in compound:
                compound[food].append(ingredients_list)
            else:
                compound[food] = [ingredients_list]
    return compound


def lowest_cost(recipes, food_item, forbidden = None):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    # use recursive helper to find lowest cost recipe
    min_cost = recipe_helper(recipes, food_item, forbidden)
    if min_cost is None:
        return None
    if len(min_cost) == 0:
        return None
    return min_cost[0] # returns first elem in tuple: cost

def scaled_flat_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    scaled = {}
    # add values of scaled ingredient to scaled dictionary
    for ingredient in flat_recipe:
        scaled[ingredient] = flat_recipe[ingredient] * n
    return scaled

def add_flat_recipes(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        add_flat_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    result = {}
    
    if flat_recipes is not None:
        for ingredient_dict in flat_recipes:
            for ingredient in ingredient_dict:
            # add new key for ingredient if not in dict, otherwise increment
                if ingredient not in result:
                    result[ingredient] = ingredient_dict[ingredient]
                else:
                    result[ingredient] += ingredient_dict[ingredient]
    return result

def cheapest_flat_recipe(recipes, food_item, forbidden = None):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    # get cheapest recipe
    cheapest_recipe = recipe_helper(recipes, food_item, forbidden)
    if cheapest_recipe is None:
        return None
    if len(cheapest_recipe) == 0:
        return None
    return cheapest_recipe[1] # return dict representing cheapest recipe

def recipe_helper(recipes, food_item, forbidden = None):
    """
    Recursively finds the cheapest cost and flat list recipe for a food.
    Returns a tuple with (cheapest_cost, flat_recipe_list) or None if 
    no recipe is found.
    """
    atomic_cost = atomic_ingredient_costs(recipes)
    compound = compound_ingredient_possibilities(recipes)
    
    # if food missing, return None
    if food_item not in atomic_cost and food_item not in compound:
        return None
    # if food forbidden, return None
    elif forbidden and food_item in forbidden:
        return None
    # base case: atomic food mapped to its quantity
    elif food_item in atomic_cost:
        return atomic_cost.get(food_item), {food_item: 1}
    else:
        # iterate through ingredient lists for food item
        valid_recipes = []
        for ing_list in compound[food_item]:
            costs = 0
            scaled_recipe_list = []
            # tracker for whether recipe is valid
            can_make = True
            # iterate through each ingredient in list
            for ingredient, quantity in ing_list:
                # check if recipe can be made or not
                scaled_recipe = recipe_helper(recipes, ingredient, forbidden)
                if scaled_recipe is None:
                    can_make = False
                    break
                # calculate cost and scaled recipe for ingredient
                costs += scaled_recipe[0] * quantity
                scaled_recipe_list.append(scaled_flat_recipe(scaled_recipe[1], quantity))
                
            if can_make:
                valid_recipes.append((costs, add_flat_recipes(scaled_recipe_list)))

        # if no valid recipes in the list, return None
        if not valid_recipes:
            return None

        # find and return the cheapest recipe
        cheapest = valid_recipes[0]
        for cost, _ in valid_recipes[1:]:
            if cost < cheapest[0]:
                cheapest = (cost, _)
        return cheapest
    
def combined_flat_recipes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    # if list empty, return list with empty dict
    if not flat_recipes:
        return [{}]
    first_recipe = flat_recipes[0] 
    # list to store combinations
    combos = []
    # recursively compute combos for remaining recipe lists
    remaining_combos = combined_flat_recipes(flat_recipes[1:])
    for ingredient in first_recipe:
        for combo in remaining_combos:
            # combine current ingredient with each remaining combo
            combined_recipe = add_flat_recipes([combo, ingredient])
            combos.append(combined_recipe)
    return combos

def all_flat_recipes(recipes, food_item, forbidden = None):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic_cost = atomic_ingredient_costs(recipes)
    compound = compound_ingredient_possibilities(recipes)
    all_recipes = []
    # food not found, return empty list
    if food_item not in atomic_cost and food_item not in compound:
        return []
    # if food forbidden, return empty list
    elif forbidden and food_item in forbidden:
        return []
    # base case: atomic food mapped to its quantity
    elif food_item in atomic_cost:
        return [{food_item: 1}]
    else:
        # iterate through each ingredient list
        for ing_list in compound[food_item]:
            curr = []
            can_make = True
            # iterate through ingredients in each list
            for ingredient, quantity in ing_list:
                # skip current recipe if forbidden
                if forbidden and ingredient in forbidden:
                    can_make = False
                    break
                # if atomic, add to current recipe
                if ingredient in atomic_cost:
                    curr.append([{ingredient: quantity}])
                else: 
                    sub_recipes = all_flat_recipes(recipes, ingredient, forbidden)
                    # scale each sub-recipe by quantity and add to current recipe
                    scaled_recipes = [scaled_flat_recipe(sub, quantity) for sub in sub_recipes]
                    curr.append(scaled_recipes)
            # add all ingredient recipes to list of possible recipes
            if can_make:
                all_recipes += combined_flat_recipes(curr)
    return all_recipes

if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
