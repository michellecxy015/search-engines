from itertools import product

entity= {
    "game" : ["Roblox", "Minecraft", "Among Us", "Clash Royale", "Pokémon Go"],
    "cartoon" : ["Gravity Falls", "The Owl House", "Dexter's Laboratory", "SpongeBob SquarePants", "Powerpuff Girls"],
    "disney": ["Inside Out", "Elemental", "The Little Mermaid", "Turning Red", "Pirates of the Caribbean"],
    "toy":["Barbie", "Pokemon card", "Lego", "Hot Wheels", "Rubik’s Cube"]
}

harmful = {
    "violence" : ["torture", "murder", "violence", "Bullying", "fights", "weapons", "gunshot", "assault"],
    "sexual content" : ["sex", "nude", "fuck", "porn", "vulgar", "dick", "nsfw", "explicit"],
    "shock and disgusting" : ["horror", "horrible", "creepy","creepiness","dark", "bloody", "decapitation", "dismemberment"]
}

    # Combine terms
combined_terms = []
for entity_category, entity_terms in entity.items():
    for harmful_category, harmful_terms in harmful.items():
        for x, y in product(entity_terms, harmful_terms):
            combined_terms.append({
                    "entity_type": entity_category,
                    "entity": x,
                    "harmful_type": harmful_category,
                    "harmful_term": y,
                    "combined_term": f"{x} {y}"
                })
