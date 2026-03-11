import json
import ollama  # Import the Ollama module

from collections import defaultdict

products_file = 'FoodMenu.json'
categories_file = 'categories.json'

delimiter = "####"

step_2_system_message_content = f"""
You are a JSON extraction engine.
You do NOT ask questions.
You do NOT explain anything.

The most recent user query will be delimited with {delimiter} characters.

### OUTPUT (STRICT):
Return ONLY a valid JSON array.
No text before or after.
No markdown.
No explanations.

Each object must contain ONLY ONE key:
- "category"
OR
- "products"

Use DOUBLE QUOTES only.

### RULES:
1. Extract ONLY items explicitly mentioned.
2. Match products ONLY from the allowed list.
3. Do NOT repeat items.
4. If nothing is found, return [].
5. If unsure, return [].

### CATEGORIES:
Starters, Main Course, Biryani, Pizza, Burgers, Desserts, Beverages

### ALLOWED PRODUCTS:
Starters:
- Veg Spring Rolls
- Chicken Wings
- Paneer Tikka
- Garlic Bread
- Crispy Corn

Main Course:
- Paneer Butter Masala
- Chicken Curry
- Dal Tadka
- Veg Fried Rice
- Butter Naan

Biryani:
- Chicken Biryani
- Mutton Biryani
- Veg Biryani
- Egg Biryani
- Hyderabadi Dum Biryani

Pizza:
- Margherita Pizza
- Farmhouse Pizza
- Pepperoni Pizza
- BBQ Chicken Pizza
- Veg Supreme Pizza

Burgers:
- Veg Burger
- Chicken Burger
- Cheese Burger
- Paneer Burger
- Double Patty Burger

Desserts:
- Chocolate Brownie
- Gulab Jamun
- Ice Cream Sundae
- Cheesecake
- Fruit Salad

Beverages:
- Coke
- Fresh Lime Soda
- Cold Coffee
- Mango Shake
- Mineral Water
"""

step_2_system_message = {'role': 'system', 'content': step_2_system_message_content}

step_4_system_message_content = f"""
You are a customer service assistant for a Online Food Restaurant.  
Respond in a **friendly and professional** tone.  

### **Response Guidelines:**
- **Be concise but informative** (avoid overly short or vague answers).  
- **Directly address the user’s question** before moving to follow-ups.  
- **Ask relevant follow-up questions** to ensure the best assistance.  
- **If relevant, provide product recommendations based on available details.**  

IMPORTANT RULES:
- Use ONLY the products provided in "Menu details".
- DO NOT invent new dishes.
- DO NOT rename products.
- DO NOT add sides or combos unless explicitly present.
- If multiple products are provided, recommend ONLY from them.

Respond politely and ask at most ONE follow-up question.

Keep responses clear and helpful without unnecessary details.
"""

step_4_system_message = {'role': 'system', 'content': step_4_system_message_content}

step_6_system_message_content = f"""
You are an assistant that evaluates whether the customer service agent's response:

1. **Does the response correctly answer the question?**  
2. **Is the response factually correct based on the given product details?**  
3. **Does the response contain any MAJOR errors that significantly affect correctness?**  

The conversation history, product details, user query, and response will be delimited with `{delimiter}`.

### **Response Format:**
- Respond with only **a single uppercase character** (`Y` or `N`).  
- **No punctuation, spaces, or explanations unless `"N"` is returned.**  
- **"N" should be used ONLY for major mistakes that mislead the user.**  
- **Minor errors or missing details do NOT justify an "N".**  

#### **Examples:**
✅ `"Y"` → (Response is correct, even if slightly incomplete)  
❌ `"N (Incorrect product details)"` → (If a product is completely misrepresented)  
❌ `"N (Major missing information)"` → (If key details affecting user decision are missing)  

**IMPORTANT:** Only return `"Y"` or `"N"` with an optional reason in parentheses.
"""

step_6_system_message = {'role': 'system', 'content': step_6_system_message_content}

def get_completion_from_messages(
    messages,
    model="qwen2.5:7b-instruct",
    temperature=0.7,
    max_tokens=250
):
    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            "num_predict": max_tokens,
            "temperature": temperature,
            "num_ctx": 2048
        }
    )
    return response["message"]["content"].strip()

PRICE_KEYWORDS = [
    "price", "cost", "how much", "rate", "amount"
]
def get_price_answer(user_input, food_menu):
    user_input_lower = user_input.lower()

    # 1️⃣ Check if price is being asked
    if not any(keyword in user_input_lower for keyword in PRICE_KEYWORDS):
        return None

    # 2️⃣ Check which item price is requested
    for item, details in food_menu.items():
        if item.lower() in user_input_lower:
            return f"The price of {item} is ₹{details['price']}."

    return None

def create_categories():
    categories_dict = {
        'Orders': [
            'Place an order',
            'Modify an order',
            'Cancel an order',
            'Order status',
            'Missing or incorrect items'
        ],
        'Payments': [
            'Payment failed',
            'Refund request',
            'Charge explanation',
            'Promo code issue'
        ],
        'Delivery': [
            'Delivery delay',
            'Change delivery address',
            'Contact delivery partner',
            'Pickup issues'
        ],
        'Account Management': [
            'Login issues',
            'Update personal information',
            'Loyalty program',
            'Account security'
        ],
        'General Inquiry': [
            'Menu information',
            'Allergen or dietary questions',
            'Restaurant hours',
            'Feedback',
            'Speak to a human'
        ]
    }

    with open(categories_file, 'w') as file:
        json.dump(categories_dict, file, indent=4)

    return categories_dict

def get_categories():
    with open(categories_file, 'r') as file:
        categories = json.load(file)
    return categories

def get_product_by_name(name):
    products = get_products()
    return products.get(name, None)

def get_products_by_category(category):
    products = get_products()
    return [product for product in products.values() if product.get("category") == category]
    
def get_product_list():
    """
    Used in L4 to get a flat list of products
    """
    products = get_products() 
    return list(products.keys())

def get_products():
    with open(products_file, 'r') as file:
        products = json.load(file)
    return products

def find_category_and_product(user_input, products_and_category):
    delimiter = "####"
    system_message = f"""
    You will be provided with restaurant customer queries. \
    The customer query will be delimited with {delimiter} characters.
    
    Output a python list of JSON objects, where each object has the following format:
        "category": <one of Starters, Main Course, Biryani, Pizza, Burgers, Desserts, Beverages>,
    OR
        "products": <a list of food items that must be found in the allowed products below>

    The categories and products must be explicitly mentioned in the customer query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.

    The allowed products are provided in JSON format.
    The keys of each item represent the food category.
    The values of each item are a list of food items within that category.

    Allowed products: {products_and_category}
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ]

    return get_completion_from_messages(messages)


def get_products_from_query(user_msg):
    """
    Adapted for online restaurant queries
    """
    products_and_category = get_products_and_category()
    delimiter = "####"
    system_message = f"""
    You will be provided with restaurant customer queries. \
    The customer query will be delimited with {delimiter} characters.
    
    Output a python list of JSON objects, where each object has the following format:
        "category": <one of Starters, Main Course, Biryani, Pizza, Burgers, Desserts, Beverages>,
    OR
        "products": <a list of food items that must be found in the allowed products below>

    The categories and products must be found in the customer query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.

    The allowed products are provided in JSON format.
    The keys of each item represent the food category.
    The values of each item are a list of food items within that category.

    Allowed products: {products_and_category}
    """
    
    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_msg}{delimiter}"}
    ] 
    
    category_and_product_response = get_completion_from_messages(messages)
    
    return category_and_product_response

def get_mentioned_product_info(data_list):
    """
    Used in L5 and L6
    """
    product_info_l = []

    if not data_list:
        return product_info_l

    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product:
                        product_info_l.append(product)
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_products = get_products_by_category(data["category"])
                product_info_l.extend(category_products)
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return product_info_l

def generate_output_string(data_list):
    output_string = ""

    if not data_list:
        return output_string

    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product:
                        output_string += json.dumps(product, indent=4) + "\n"
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_products = get_products_by_category(data["category"])
                for product in category_products:
                    output_string += json.dumps(product, indent=4) + "\n"
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return output_string

# Example usage:
# product_information_for_user_message_1 = generate_output_string(category_and_product_list)
# print(product_information_for_user_message_1)

def answer_user_msg(user_msg,product_info):
    """
    Code from L5, used in L6
    """
    delimiter = "####"
    system_message = f"""
    You are a customer service assistant for a Online Food Restaurant. \
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow up questions.
    """
    # user_msg = f"""
    # tell me about the smartx pro phone and the fotosnap camera, the dslr one. Also what tell me about your tvs"""
    messages =  [  
    {'role':'system', 'content': system_message},   
    {'role':'user', 'content': f"{delimiter}{user_msg}{delimiter}"},  
    {'role':'assistant', 'content': f"Relevant product information:\n{product_info}"},   
    ] 
    response = get_completion_from_messages(messages)
    return response

from collections import defaultdict
import json

def create_food_menu():
    """
    Create food menu dictionary and save it to FoodMenu.json
    """

    food_menu = {
        "Margherita Pizza": {
            "name": "Margherita Pizza",
            "category": "Pizza",
            "type": "Vegetarian",
            "price": 8.99,
            "rating": 4.6,
            "ingredients": ["Cheese", "Tomato Sauce", "Basil"],
            "description": "Classic pizza topped with fresh cheese and basil.",
            "availability": "Available"
        },

        "Pepperoni Pizza": {
            "name": "Pepperoni Pizza",
            "category": "Pizza",
            "type": "Non-Vegetarian",
            "price": 10.99,
            "rating": 4.7,
            "ingredients": ["Pepperoni", "Cheese", "Tomato Sauce"],
            "description": "Spicy pepperoni pizza with melted cheese.",
            "availability": "Available"
        },

        "Veg Supreme Pizza": {
            "name": "Veg Supreme Pizza",
            "category": "Pizza",
            "type": "Vegetarian",
            "price": 11.49,
            "rating": 4.5,
            "ingredients": ["Onion", "Capsicum", "Olives", "Cheese"],
            "description": "Loaded vegetable pizza with rich flavors.",
            "availability": "Available"
        },

        "Chicken Burger": {
            "name": "Chicken Burger",
            "category": "Burgers",
            "type": "Non-Vegetarian",
            "price": 7.99,
            "rating": 4.6,
            "ingredients": ["Chicken Patty", "Lettuce", "Mayo"],
            "description": "Juicy chicken burger with fresh toppings.",
            "availability": "Available"
        },

        "Veg Burger": {
            "name": "Veg Burger",
            "category": "Burgers",
            "type": "Vegetarian",
            "price": 6.99,
            "rating": 4.4,
            "ingredients": ["Veg Patty", "Lettuce", "Cheese"],
            "description": "Healthy vegetarian burger.",
            "availability": "Available"
        },

        "French Fries": {
            "name": "French Fries",
            "category": "Sides",
            "type": "Vegetarian",
            "price": 3.99,
            "rating": 4.3,
            "ingredients": ["Potatoes", "Salt"],
            "description": "Crispy golden french fries.",
            "availability": "Available"
        },

        "Chicken Wings": {
            "name": "Chicken Wings",
            "category": "Starters",
            "type": "Non-Vegetarian",
            "price": 9.49,
            "rating": 4.7,
            "ingredients": ["Chicken", "Spices"],
            "description": "Spicy and crispy chicken wings.",
            "availability": "Available"
        },

        "Paneer Tikka": {
            "name": "Paneer Tikka",
            "category": "Starters",
            "type": "Vegetarian",
            "price": 8.49,
            "rating": 4.6,
            "ingredients": ["Paneer", "Spices", "Yogurt"],
            "description": "Grilled paneer cubes with Indian spices.",
            "availability": "Available"
        },

        "Chicken Biryani": {
            "name": "Chicken Biryani",
            "category": "Main Course",
            "type": "Non-Vegetarian",
            "price": 12.99,
            "rating": 4.8,
            "ingredients": ["Rice", "Chicken", "Spices"],
            "description": "Aromatic rice dish cooked with chicken and spices.",
            "availability": "Available"
        },

        "Veg Biryani": {
            "name": "Veg Biryani",
            "category": "Main Course",
            "type": "Vegetarian",
            "price": 10.99,
            "rating": 4.5,
            "ingredients": ["Rice", "Vegetables", "Spices"],
            "description": "Flavorful biryani with mixed vegetables.",
            "availability": "Available"
        },

        "Butter Chicken": {
            "name": "Butter Chicken",
            "category": "Main Course",
            "type": "Non-Vegetarian",
            "price": 13.49,
            "rating": 4.8,
            "ingredients": ["Chicken", "Butter", "Cream"],
            "description": "Creamy and rich butter chicken curry.",
            "availability": "Available"
        },

        "Paneer Butter Masala": {
            "name": "Paneer Butter Masala",
            "category": "Main Course",
            "type": "Vegetarian",
            "price": 11.99,
            "rating": 4.7,
            "ingredients": ["Paneer", "Butter", "Tomato Gravy"],
            "description": "Soft paneer in rich butter gravy.",
            "availability": "Available"
        },

        "Veg Fried Rice": {
            "name": "Veg Fried Rice",
            "category": "Main Course",
            "type": "Vegetarian",
            "price": 8.99,
            "rating": 4.4,
            "ingredients": ["Rice", "Vegetables", "Soy Sauce"],
            "description": "Stir-fried rice with fresh vegetables.",
            "availability": "Available"
        },

        "Chicken Fried Rice": {
            "name": "Chicken Fried Rice",
            "category": "Main Course",
            "type": "Non-Vegetarian",
            "price": 9.99,
            "rating": 4.6,
            "ingredients": ["Rice", "Chicken", "Soy Sauce"],
            "description": "Flavorful fried rice cooked with chicken.",
            "availability": "Available"
        },

        "Hakka Noodles": {
            "name": "Hakka Noodles",
            "category": "Main Course",
            "type": "Vegetarian",
            "price": 8.49,
            "rating": 4.5,
            "ingredients": ["Noodles", "Vegetables", "Sauces"],
            "description": "Classic Indo-Chinese noodles.",
            "availability": "Available"
        },

        "Chicken Hakka Noodles": {
            "name": "Chicken Hakka Noodles",
            "category": "Main Course",
            "type": "Non-Vegetarian",
            "price": 9.49,
            "rating": 4.6,
            "ingredients": ["Noodles", "Chicken", "Sauces"],
            "description": "Spicy noodles tossed with chicken.",
            "availability": "Available"
        },

        "Tomato Soup": {
            "name": "Tomato Soup",
            "category": "Soups",
            "type": "Vegetarian",
            "price": 4.49,
            "rating": 4.2,
            "ingredients": ["Tomatoes", "Cream", "Spices"],
            "description": "Warm and comforting tomato soup.",
            "availability": "Available"
        },

        "Sweet Corn Soup": {
            "name": "Sweet Corn Soup",
            "category": "Soups",
            "type": "Vegetarian",
            "price": 4.99,
            "rating": 4.3,
            "ingredients": ["Sweet Corn", "Vegetables", "Spices"],
            "description": "Healthy soup made with sweet corn.",
            "availability": "Available"
        },

        "Masala Dosa": {
            "name": "Masala Dosa",
            "category": "South Indian",
            "type": "Vegetarian",
            "price": 7.99,
            "rating": 4.7,
            "ingredients": ["Rice Batter", "Potato Masala"],
            "description": "Crispy dosa filled with spiced potato.",
            "availability": "Available"
        },

        "Idli Sambar": {
            "name": "Idli Sambar",
            "category": "South Indian",
            "type": "Vegetarian",
            "price": 6.99,
            "rating": 4.6,
            "ingredients": ["Idli", "Sambar"],
            "description": "Soft idlis served with hot sambar.",
            "availability": "Available"
        },

        "Chocolate Brownie": {
            "name": "Chocolate Brownie",
            "category": "Desserts",
            "type": "Vegetarian",
            "price": 4.99,
            "rating": 4.7,
            "ingredients": ["Chocolate", "Flour", "Sugar"],
            "description": "Rich chocolate brownie.",
            "availability": "Available"
        },

        "Ice Cream Sundae": {
            "name": "Ice Cream Sundae",
            "category": "Desserts",
            "type": "Vegetarian",
            "price": 5.49,
            "rating": 4.6,
            "ingredients": ["Ice Cream", "Chocolate Syrup"],
            "description": "Cold and creamy dessert.",
            "availability": "Available"
        },

        "Cold Coffee": {
            "name": "Cold Coffee",
            "category": "Beverages",
            "type": "Vegetarian",
            "price": 3.99,
            "rating": 4.4,
            "ingredients": ["Coffee", "Milk"],
            "description": "Chilled coffee drink.",
            "availability": "Available"
        },

        "Fresh Lime Soda": {
            "name": "Fresh Lime Soda",
            "category": "Beverages",
            "type": "Vegetarian",
            "price": 2.99,
            "rating": 4.3,
            "ingredients": ["Lime", "Soda"],
            "description": "Refreshing lime soda.",
            "availability": "Available"
        },

        "Mango Milkshake": {
            "name": "Mango Milkshake",
            "category": "Beverages",
            "type": "Vegetarian",
            "price": 4.49,
            "rating": 4.5,
            "ingredients": ["Mango", "Milk", "Sugar"],
            "description": "Refreshing mango milkshake.",
            "availability": "Available"
        },

        "Strawberry Milkshake": {
            "name": "Strawberry Milkshake",
            "category": "Beverages",
            "type": "Vegetarian",
            "price": 4.49,
            "rating": 4.4,
            "ingredients": ["Strawberry", "Milk", "Sugar"],
            "description": "Sweet and creamy strawberry milkshake.",
            "availability": "Available"
        }
    }

    with open("FoodMenu.json", "w") as file:
        json.dump(food_menu, file, indent=4)

    return food_menu
    
def load_food_menu():
    with open("FoodMenu.json", "r") as file:
        return json.load(file)

def get_products_and_category():
    """
    Retrieves restaurant menu items and categorizes them properly.
    Ensures all menu categories exist even if they have no products.
    """
    predefined_categories = [
        "Starters",
        "Main Course",
        "Biryani",
        "Pizza",
        "Burgers",
        "Desserts",
        "Beverages"
    ]

    try:
        products = get_products()  # Must return dict: {product_name: {category: "..."}}
        if not isinstance(products, dict):
            raise ValueError("get_products() did not return a valid dictionary.")

        products_by_category = defaultdict(list)

        # Add products to their respective categories
        for product_name, product_info in products.items():
            category = product_info.get('category')
            if category in predefined_categories:
                products_by_category[category].append(product_name)

        # Ensure all predefined categories exist
        for category in predefined_categories:
            products_by_category.setdefault(category, [])

        return dict(products_by_category)

    except Exception as e:
        print(f"Error in get_products_and_category: {e}")
        return {category: [] for category in predefined_categories}

def find_category_and_product_only(user_input, products_and_category):
    """
    Uses LLM to extract restaurant categories and menu items.
    Ensures STRICT JSON output.
    """
    delimiter = "####"
    system_message = f"""
    You will be provided with a restaurant customer query enclosed in {delimiter}.

    **Task:** Extract relevant food categories and menu items from the predefined list.

    **Output Format:**  
    Return a **valid JSON list** of objects where each object contains:  
    - "category": (one of the predefined menu categories)  
    - "products": (a list of matching menu items)  

    **Rules:**  
    1️⃣ If only a category is mentioned (no specific items), include **all products** from that category.  
    2️⃣ If a product is mentioned, ensure it belongs to the correct category.  
    3️⃣ If no valid category or product is found, return an empty list `[]`.  
    4️⃣ Recognize common synonyms  
        (e.g., "soft drinks" → "Beverages", "pizza" → "Pizza").  
    5️⃣ **STRICT JSON LIST ONLY** — no text, no explanation, no markdown.

    **Allowed Categories & Products:**  
    {json.dumps(products_and_category, indent=4)}
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ]

    raw_response = get_completion_from_messages(messages)
    print("Raw Response:", raw_response)  # Debugging

    return raw_response

import json
import re

def read_string_to_list(input_data):
    """
    Converts a JSON string to a Python list safely.
    Handles markdown, explanations, and invalid outputs.
    """

    # If already a list, return directly
    if isinstance(input_data, list):
        return input_data

    # Empty or explicit empty list
    if not input_data or input_data.strip() == "[]":
        return []

    # Convert to string safely
    text = str(input_data).strip()

    # 🔹 Remove markdown code fences completely
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()

    # 🔹 HARD GUARD: must start with [ or {
    if not text.startswith("["):
        print("Invalid JSON response: Output does not start with '['")
        return []

    try:
        parsed = json.loads(text)

        # 🔹 Ensure it's a list
        if isinstance(parsed, list):
            return parsed
        else:
            return []

    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
        return []
