"""
Cooking Terms Glossary
Comprehensive list of common cooking terms with beginner-friendly definitions
"""

COOKING_TERMS = {
    # Cutting Techniques
    "dice": "Cut food into small, uniform cubes (usually 1/4 to 1/2 inch). Like cutting something into tiny squares.",
    "chop": "Cut food into pieces of roughly the same size. Doesn't need to be perfect - just reasonably uniform.",
    "mince": "Cut food into very tiny pieces, as small as you can get them. Often used for garlic or herbs.",
    "slice": "Cut food into thin, flat pieces. Think of cutting a loaf of bread.",
    "julienne": "Cut food into thin matchstick-shaped strips. Like cutting vegetables for stir-fry.",
    "cube": "Cut food into larger cubes than dicing, usually about 1 inch on each side.",
    "chiffonade": "Stack leaves, roll them up, and slice into thin ribbons. Great for herbs like basil.",
    
    # Cooking Methods
    "sauté": "Cook food quickly in a small amount of oil or butter over medium-high heat, stirring often. The pan should be hot!",
    "simmer": "Cook liquid just below boiling. You'll see small bubbles around the edges, but not a rolling boil.",
    "boil": "Heat liquid until large bubbles rapidly break the surface. Water boils at 212°F (100°C).",
    "steam": "Cook food using the vapor from boiling water. Food doesn't touch the water, just the steam.",
    "roast": "Cook food in the oven using dry heat. Usually at higher temperatures (375°F+) for browning.",
    "bake": "Cook food in the oven with dry heat, usually at moderate temperatures. Like making cookies or bread.",
    "broil": "Cook food using direct heat from above (usually the top heating element in your oven). Like an upside-down grill.",
    "grill": "Cook food over direct heat (usually from below). Can be on a BBQ or a stovetop grill pan.",
    "braise": "Brown meat in fat, then cook it slowly in a covered pot with liquid. Makes tough meat tender!",
    "sear": "Cook food (especially meat) at very high heat to create a brown, flavorful crust. Usually done quickly.",
    "poach": "Gently cook food in barely-simmering liquid (not boiling). Common for eggs and fish.",
    "blanch": "Briefly boil food, then immediately plunge it into ice water to stop cooking. Keeps vegetables bright green.",
    "fry": "Cook food in hot oil or fat. Can be shallow (a little oil) or deep (food completely submerged).",
    "stir-fry": "Cook small pieces of food quickly over very high heat while constantly stirring. Traditional Asian technique.",
    
    # Preparation Techniques
    "whisk": "Beat ingredients together rapidly using a whisk (the wire tool) to add air and blend thoroughly.",
    "beat": "Mix ingredients vigorously to combine them and add air. Makes things light and fluffy.",
    "fold": "Gently combine ingredients using a lifting and turning motion. Keeps things airy (like when adding egg whites).",
    "cream": "Beat fat (like butter) and sugar together until light and fluffy. Creates air bubbles for tender baked goods.",
    "knead": "Work dough by pressing, folding, and turning it. Develops gluten for bread-making.",
    "marinate": "Soak food in a seasoned liquid before cooking. Adds flavor and can tenderize meat.",
    "baste": "Spoon or brush liquid (like pan juices) over food while it cooks. Keeps it moist and adds flavor.",
    "season": "Add salt, pepper, herbs, or spices to food to enhance the flavor.",
    "deglaze": "Add liquid to a hot pan to loosen the brown bits stuck to the bottom. Creates delicious sauces!",
    "reduce": "Simmer liquid to evaporate some of it, making it thicker and more concentrated in flavor.",
    "zest": "Remove the colored outer peel of citrus fruit (not the white part!). Contains flavorful oils.",
    "strain": "Pour liquid through a sieve or strainer to remove solid pieces.",
    "drain": "Pour off liquid from food, usually using a colander or strainer.",
    "toss": "Gently mix ingredients by lifting and turning them. Like tossing a salad.",
    "coat": "Cover food completely with another ingredient, like flour or breadcrumbs.",
    "score": "Make shallow cuts in the surface of food (like cutting a crosshatch pattern). Helps it cook evenly or look fancy.",
    
    # Ingredient States
    "room temperature": "Not cold from the fridge, not warm. Usually means leaving something out for 30-60 minutes.",
    "soft peaks": "When you lift a whisk from whipped cream/egg whites, the peaks curl over gently. Not quite stiff.",
    "stiff peaks": "When you lift a whisk out, the peaks stand straight up. Fully whipped!",
    "golden brown": "Cooked until the surface is light brown in color, not dark. Looks delicious and appetizing.",
    "caramelized": "Cooked until natural sugars turn brown and sweet. Gives a rich, deep flavor.",
    "al dente": "Italian for 'to the tooth.' Pasta that's cooked but still slightly firm when you bite it. Not mushy!",
    
    # Measurements & Amounts
    "pinch": "The amount you can hold between your thumb and forefinger. Very small - less than 1/8 teaspoon.",
    "dash": "A small amount, usually 2-3 drops of liquid or a quick shake from a shaker.",
    "handful": "About 1/4 to 1/2 cup, or as much as you can grab in one hand. Not super precise!",
    
    # Equipment Terms
    "double boiler": "A pot of boiling water with a heat-proof bowl on top. Gently heats delicate ingredients without burning.",
    "preheat": "Turn on the oven ahead of time so it reaches the right temperature before you put food in.",
    "rest": "Let cooked meat sit for a few minutes before cutting. Helps juices redistribute - makes it juicier!",
    
    # Texture Terms
    "crisp": "Firm and crunchy texture. The opposite of soft or soggy.",
    "tender": "Soft and easy to chew or cut. Not tough or chewy.",
    "fluffy": "Light and airy texture, like clouds. Opposite of dense or heavy.",
    "smooth": "No lumps or chunks. Completely even texture throughout.",
    "creamy": "Smooth and rich, like cream. Thick but flows easily.",
    
    # Other Common Terms
    "peel": "Remove the outer skin or rind from fruits and vegetables.",
    "core": "Remove the tough center part (like from an apple or pineapple).",
    "pit": "Remove the hard seed from fruit like peaches, cherries, or avocados.",
    "garnish": "Add a decorative or flavorful finishing touch on top of a dish. Makes it look pretty!",
    "taste": "Actually eat a small amount to check if it needs more seasoning. Important step!",
    "adjust seasoning": "Taste the food and add more salt, pepper, or spices if needed.",
}

def get_term_definition(term):
    # get the definition of a cooking term
    term_lower = term.lower().strip()
    return COOKING_TERMS.get(term_lower)

def get_all_terms():
    # get list of all cooking terms
    return list(COOKING_TERMS.keys())

def search_terms(query):
    # search for terms matching a query
    query_lower = query.lower()
    return {
        term: definition 
        for term, definition in COOKING_TERMS.items() 
        if query_lower in term.lower() or query_lower in definition.lower()
    }

# For database population
def get_terms_for_database():
    # get terms formatted for database insertion
    return [
        {'name': term, 'description': definition}
        for term, definition in COOKING_TERMS.items()
    ]