import json

def parse_ingredients(raw_input):
    # accepts comma-separated or newline-separated ingredients
    # returns a clean list of ingredients

    # splitter; on commas or newlines
    ingredients = raw_input.replace('\n', ',').split(',')

    # normalize list: lowercase and strip whitespace
    cleaned = [ing.strip().lower() for ing in ingredients if ing.strip()]

    return cleaned

def load_recipes():
    # Load recipes from a JSON file
    with open('recipes.json', 'r') as file:
        data = json.load(file)
    return data['recipes']

def calculate_match(recipe_ingredients, user_ingredients):
    # calculates how well a recipe matches the user's ingredients
    # returns match percentage, matched ingredients and missing ingredients

    # normalize
    lower_rec_ings = [ing.lower() for ing in recipe_ingredients]

    # ingredient lists
    matched = []
    missing = []

    # check each recipe ingredient
    for recipe_ing in lower_rec_ings:
        if recipe_ing in user_ingredients:
            matched.append(recipe_ing)
        else:
            missing.append(recipe_ing)

    # calculate precentage
    total = len(lower_rec_ings)
    match_count = len(matched)
    percentage = (match_count/total*100) if total > 0 else 0

    return {
        'percentage': round(percentage, 1),
        'matched': matched,
        'missing': missing
    }

def search_recipes(user_ingredients, recipes):
    # searches through recipes and ranks them by match percentage
    results = []

    for recipe in recipes:
        match_data = calculate_match(recipe['ingredients'], user_ingredients)
        # only shows recipes with at least some match
        # match_data still has unmatched recipes for further use
        if match_data['percentage'] > 0:
            results.append({
                'id': recipe['id'],
                'name': recipe['name'],
                'match_percentage': match_data['percentage'],
                'matched_ingredients': match_data['matched'],
                'missing_ingredients': match_data['missing']
            })

    # sort by match percentage descending
    results.sort(key=lambda x: x['match_percentage'], reverse=True)

    return results

def display_results(results, ingred_input):
    #Displays search results
    print("\n" + "=" * 70)
    print(f"Your ingredients: {ingred_input}")
    print("=" * 70)

    # no recipes found; could be redirected to add more ingredients later
    if not results:
        print("\n❌ No matching recipes found.\n")
        return


    for i, recipe in enumerate(results, 1):
        #visual indicator
        bars = "[]" * int(recipe['match_percentage'] / 10)

        print(f"\n{i}. {recipe['name']}")
        print(f"   Match: {recipe['match_percentage']}% {bars}")
        print(f"   You have: {', '.join(recipe['matched_ingredients'])}")
        
        if recipe['missing_ingredients']:
            print(f"   Missing: {', '.join(recipe['missing_ingredients'])}")


def main():
    # main function to run the recipe search and display results
    print("\n" + "=" * 70)
    print("SmartFridge - Quick Recipe Search")
    print("=" * 70)

    print("Enter your available ingredients (comma-separated):")
    print("Ex: eggs, bread, cheese, butter\n")

    # get user input
    user_input = input("Your ingredients: ").strip()

    # guard against empty input
    if not user_input:
        print("\n No ingredients entered. Exiting.\n")
        return
    
    # parse ingredients and print
    user_ing = parse_ingredients(user_input)

    recipes = load_recipes()

    results = search_recipes(user_ing, recipes)

    display_results(results, user_input)


if __name__ == "__main__":
    main()