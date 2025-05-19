from pydantic import BaseModel
from typing import List

class MenuItem(BaseModel):
    name: str
    price: float
    description: str
    ingredients: list[str]

class Menu(BaseModel):      
    items: list[MenuItem]

class Restaurant(BaseModel):
    name: str
    menu: Menu

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

class ServingUnit(BaseModel):
    description: str
    plural: str
    amount: float
    grams: float
    milliliters: float

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