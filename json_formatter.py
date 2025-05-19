from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import MenuItem, Menu, Restaurant, MenuItemJSON, ServingUnit

class NutrientInfo(BaseModel):
    protein: float = 0.0
    fat: float = 0.0
    carbohydrates: float = 0.0
    calories: float = 0.0
    fiber: float = 0.0
    calcium: float = 0.0
    iron: float = 0.0
    magnesium: float = 0.0
    phosphorus: float = 0.0
    potassium: float = 0.0
    sodium: float = 0.0
    zinc: float = 0.0
    copper: float = 0.0
    flouride: float = 0.0
    manganese: float = 0.0
    selenium: float = 0.0
    vitamin_a: float = 0.0
    retinol: float = 0.0
    vitamin_a_rae: float = 0.0
    vitamin_d: float = 0.0
    vitamin_c: float = 0.0
    thiamin: float = 0.0
    riboflavin: float = 0.0
    niacin: float = 0.0
    pantothenic_acid: float = 0.0
    vitamin_b6: float = 0.0
    vitamin_b12: float = 0.0
    vitamin_k: float = 0.0
    folate_dfe: float = 0.0
    cholesterol: float = 0.0
    trans_fat: float = 0.0
    saturated_fat: float = 0.0
    omega3_ala: float = 0.0
    added_sugar: float = 0.0
    biotin: float = 0.0
    iodine: float = 0.0
    molybdenum: float = 0.0
    chloride: float = 0.0

class MenuItemJSON(BaseModel):
    name: str
    brand_name: str = ""
    product_type: str = "Restaurant Meal"
    image: str = ""
    category: str = "Restaurant Meal"
    tags: List[str] = []
    gtin_upc: List[str] = []
    language: str = "en"
    serving_unit: str = "g"
    grams_per_serving: float = 0.0
    milliliters_per_serving: float = 0.0
    serving_description: str = "1 serving"
    units: List[ServingUnit] = []
    default_unit: ServingUnit
    ingredients_description: str = ""
    exclude_from_groceries: bool = True
    nutrients_per_serving: NutrientInfo = NutrientInfo()

def convert_menu_item_to_json(menu_item: MenuItem, restaurant_name: str) -> MenuItemJSON:
    """Convert a MenuItem to the required JSON format."""
    default_unit = ServingUnit(
        description="serving",
        plural="servings",
        amount=1.0,
        grams=0.0,
        milliliters=0.0
    )
    
    return MenuItemJSON(
        name=menu_item.name,
        brand_name=restaurant_name,
        ingredients_description=", ".join(menu_item.ingredients),
        default_unit=default_unit,
        units=[default_unit]
    )

def convert_restaurant_to_json(restaurant: Restaurant) -> List[MenuItemJSON]:
    """Convert a Restaurant object to a list of MenuItemJSON objects."""
    return [
        convert_menu_item_to_json(item, restaurant.name)
        for item in restaurant.menu.items
    ]

def save_restaurant_to_json(restaurant: Restaurant, output_file: str):
    """Save restaurant menu items to a JSON file."""
    import json
    
    menu_items_json = convert_restaurant_to_json(restaurant)
    with open(output_file, 'w') as f:
        json.dump([item.dict() for item in menu_items_json], f, indent=4) 