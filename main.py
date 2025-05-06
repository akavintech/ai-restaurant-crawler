from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from dotenv import load_dotenv
import asyncio
from pydantic import BaseModel
import os
import tiktoken

# Read GOOGLE_API_KEY into env
load_dotenv()


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

controller = Controller(output_model=Restaurant)


# Configure the browser to connect to your Chrome instance
browser = Browser(
    config=BrowserConfig(
        # Specify the path to your Chrome executable
        chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
        # For Windows, typically: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        # For Linux, typically: '/usr/bin/google-chrome'
    )
)


# Token estimation utility
def estimate_tokens(text, model="gemini-2.0-flash-exp"):
    """
    Estimate the number of tokens in a text using tiktoken.
    
    Args:
        text (str): The text to estimate tokens for
        model (str): The model name to use for tokenization
        
    Returns:
        int: Estimated token count
    """
    # For Gemini models, we can use the cl100k_base encoding which is similar
    # to what Gemini uses (based on GPT-4 tokenizer)
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


# Make sure the API key is available
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Set the API key in the environment directly
os.environ["GEMINI_API_KEY"] = api_key

# Initialize the model with explicit API key
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', google_api_key=api_key)

# Set environment variable to skip LLM verification
os.environ["SKIP_LLM_API_KEY_VERIFICATION"] = "true"

# Add this before creating the agent
print(f"Using API key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
print(f"Model: gemini-2.0-flash-exp")
print(f"Skip verification: {os.environ.get('SKIP_LLM_API_KEY_VERIFICATION')}")

# Add this before the main function
RESTAURANT_URLS = [
    "http://troygreek.com/",
    "http://arrowoodgolf.com/",
    "https://laprimaveramex.com/",
    "http://104.196.101.45/sushiHana/",
    "http://asianrestaurantnorthhollywood.com/",
    "https://copperskillet.com/",
    "https://awrestaurants.com/locations/california/sacramento/3820-florin-road/"
]

async def main():
    try:
        website_url = RESTAURANT_URLS[0]  # You can change the index or make it a parameter
        
        task_prompt = f"""
        Visit {website_url} and extract menu information:
        1. Look for food items in:
           - Menu section if available
           - Images containing food items
           - Any section describing food offerings
        2. For each food item found, collect:
           - Name of the item
           - Price
           - Description
           - Ingredients (if available)
        3. Important restrictions:
           - DO NOT click on any "Order Online" buttons or links
           - Stay within the main website
        4. Search all relevant pages but avoid external ordering systems
        """
        
        # Estimate input tokens (task prompt)
        input_tokens = estimate_tokens(task_prompt)
        print(f"Input tokens: {input_tokens}")
        
        agent = Agent(
            task=task_prompt,
            llm=llm,
            browser=browser,
            controller=controller
        )

        # Run the agent
        result = await agent.run()
        final_result = result.final_result()
        
        # Estimate output tokens (result)
        output_tokens = estimate_tokens(str(final_result))
        print(f"Output tokens: {output_tokens}")
        
        print("\nFinal Result:")
        print(final_result)

        # Close the browser
        await browser.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())


# https://laprimaveramex.com/
# http://troygreek.com/
# http://104.196.101.45/sushiHana/
# http://arrowoodgolf.com/
# http://asianrestaurantnorthhollywood.com/
# https://copperskillet.com/
# https://awrestaurants.com/locations/california/sacramento/3820-florin-road/

