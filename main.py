from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from dotenv import load_dotenv
import asyncio
import os
import tiktoken
from models import Restaurant
from json_formatter import save_restaurant_to_json

# Read GOOGLE_API_KEY into env
load_dotenv()

controller = Controller(output_model=Restaurant)

# Configure the browser to connect to your Chrome instance
browser = Browser(
    config=BrowserConfig(
        # Let Playwright manage the browser instance
        chrome_instance_path=None,  # Remove custom Chrome path
        headless=False,  # Set to True if you want to run Chrome in headless mode
        user_data_dir=None,  # Use a separate user profile
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-popup-blocking',
            '--start-maximized',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--disable-features=TranslateUI,BlinkGenPropertyTrees',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--enable-features=NetworkService,NetworkServiceInProcess',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--mute-audio'
        ],
        launch_options={
            'devtools': True,  # Open DevTools
            'slowMo': 50,  # Slow down operations by 50ms
            'timeout': 60000,  # Increase timeout to 60 seconds
            'handleSIGINT': False,  # Don't handle SIGINT
            'handleSIGTERM': False,  # Don't handle SIGTERM
            'handleSIGHUP': False,  # Don't handle SIGHUP
            'ignoreDefaultArgs': ['--enable-automation']  # Ignore automation flag
        }
    )
)

# Token estimation utility
def estimate_tokens(text, model="gemini-2.5-flash-preview-04-17"):
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
llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-preview-04-17', google_api_key=api_key)

# Set environment variable to skip LLM verification
os.environ["SKIP_LLM_API_KEY_VERIFICATION"] = "true"

# Add this before creating the agent
print(f"Using API key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
print(f"Model: gemini-2.5-flash-preview-04-17")
print(f"Skip verification: {os.environ.get('SKIP_LLM_API_KEY_VERIFICATION')}")

# Add this before the main function
RESTAURANT_URLS = [
    # "http://adalbertosmexicanrestaurant.com/",
    # "http://cheveybarbacha.com/",
    # "http://duffsdoggz.com/",
    # "http://heirloom-pizzeria.com/",
    # "http://luckygreekburgers.com/",
    # "https://www.zovs.com/",
    # "http://facebook.com/RoseGardenRedding",
    # "http://jugjugsportsbar.com/",
    # "http://194eatery.com/",
    # "http://cafe-delicias.com/",
    # "http://eurekarestaurantgroup.com/blog/locations/hawthorne-airport/",
    # "http://gayroxpress.square.site/"
    # "http://greenolivela.com/our-menu.html",
    # "http://perkos.com/"    
    # "http://troygreek.com/",
    # "https://locations.chipotle.com/ca/alameda/2314-s-shore-ctr?utm_source=google&utm_medium=yext&utm_campaign=yext_listings"
    # "https://www.thephocadaogrill.com/",
    # "http://hanasushi.menu11.com/",
    # "http://bigalspizzeria.com/".
    # "http://dragonhousemoval.com/"
    # "https://laprimaveramex.com/",
    "https://www.wanaaha.com/dining/tukanovie-restaurant/"
    # "https://locations.pizzahut.com/ca/banning/1860-w-ramsey-st?utm_medium=organic&utm_source=local&utm_campaign=googlelistings&utm_content=website&utm_term=298254",
    # "http://nasaspacebar.com/",
    # "http://www.lazysusanchinese.com/"
]

# Initialize global token counters,
total_input_tokens = 0
total_output_tokens = 0

async def enhance_menu_items_with_ingredients(restaurant: Restaurant, llm: ChatGoogleGenerativeAI) -> Restaurant:
    """Enhance menu items with inferred ingredients if not present."""
    for item in restaurant.menu.items:
        if not item.ingredients:
            # Create a prompt for ingredient inference
            inference_prompt = f"""
            Based on the following menu item, infer the most likely ingredients:
            Name: {item.name}
            Description: {item.description}
            
            Please list the main ingredients that would typically be used in this dish.
            Return only a comma-separated list of ingredients, nothing else.
            """
            
            try:
                # Get ingredient inference from LLM
                response = await llm.ainvoke(inference_prompt)
                inferred_ingredients = [ing.strip() for ing in response.content.split(',')]
                item.ingredients = inferred_ingredients
            except Exception as e:
                print(f"Error inferring ingredients for {item.name}: {e}")
                item.ingredients = ["Ingredients not available"]
    
    return restaurant

async def process_restaurant(website_url: str, llm: ChatGoogleGenerativeAI, browser: Browser, controller: Controller) -> bool:
    """Process a single restaurant URL and return success status."""
    try:
        print(f"\nProcessing restaurant: {website_url}")
        
        task_prompt = f"""
        Visit {website_url} and extract menu information:
        1. Look for food items in:
           - Menu section if available
           - Images containing food items
           - PDF files containing menus
           - Any section describing food offerings
        2. For each food item found, collect:
           - Name of the item
           - Price
           - Description
           - Ingredients (if available in the menu or description)
        3. Important instructions:
           - If you find a PDF menu, download and analyze its contents
           - For multi-page PDFs:
             * Set a 30-second timeout for PDF processing
             * If PDF takes too long to load or process, skip it and try other methods
             * Navigate through pages quickly, don't wait for full rendering
             * If PDF is too large or complex, note this and move on
             * Use page navigation controls to move through pages
             * Extract content from each page
             * Look for page numbers or navigation indicators
             * Check for table of contents if available
           - For images containing menus, use OCR to extract text
           - If a menu is in an image format, describe what you see
           - Look for "Menu", "Food", "Dining" sections
           - Check for downloadable menu PDFs
        4. Important restrictions:
           - Stay within the main website
           - Only download PDFs from the main website domain
           - If a PDF is causing issues, skip it and try alternative methods
        5. For ingredients:
           - If ingredients are explicitly listed in the menu, use those
           - If ingredients are mentioned in the description, extract them
           - If no ingredients are found, leave the ingredients list empty (we'll infer them later)
        6. Special handling:
           - If you find a PDF menu, note its location and content
           - For multi-page PDFs:
             * Document which page each item was found on
             * Note any section headers or categories
             * Track page numbers for reference
             * If PDF processing is slow, switch to alternative methods
           - For image-based menus, describe the items you can see
           - If menu is in a gallery format, check all images
        7. Last resort strategy:
           - If no menu items are found through normal navigation
           - Click on "Order Now" or "Order Online" section
           - Extract menu items from the ordering interface
           - This is ONLY to be used if no menu items are found through other methods
        8. Error handling:
           - If any method (PDF, image, etc.) takes too long, skip it
           - Document which methods were attempted and why they failed
           - Always have a fallback method ready
           - Don't get stuck on any single method for more than 30 seconds
        """
        
        # Estimate input tokens (task prompt)
        input_tokens = estimate_tokens(task_prompt)
        print(f"Input tokens: {input_tokens}")
        
        # Update total input tokens
        global total_input_tokens
        total_input_tokens += input_tokens
        
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
        
        # Update total output tokens
        global total_output_tokens
        total_output_tokens += output_tokens
        
        print("\nFinal Result:")
        print(final_result)

        # Parse the JSON string into a Restaurant object if it's a string
        if isinstance(final_result, str):
            import json
            try:
                restaurant_data = json.loads(final_result)
                final_result = Restaurant(**restaurant_data)
            except json.JSONDecodeError as e:
                print(f"\nError parsing JSON: {e}")
                print("Raw result:", final_result)
                return False

        # Enhance menu items with inferred ingredients
        if isinstance(final_result, Restaurant):
            print("\nEnhancing menu items with inferred ingredients...")
            final_result = await enhance_menu_items_with_ingredients(final_result, llm)
            
            # Save results to JSON file
            output_file = f"output/menu_json/{final_result.name.lower().replace(' ', '_')}_menu.json"
            save_restaurant_to_json(final_result, output_file)
            print(f"\nResults saved to {output_file}")
            return True
        else:
            print("\nWarning: Result is not in the expected Restaurant format")
            print("Raw result:", final_result)
            return False

    except Exception as e:
        print(f"Error processing {website_url}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    try:
        # Create a list to track successful and failed URLs
        successful_urls = []
        failed_urls = []
        
        for i, website_url in enumerate(RESTAURANT_URLS):
            print(f"\nProcessing restaurant {i+1} of {len(RESTAURANT_URLS)}")
            
            # Process the restaurant
            success = await process_restaurant(website_url, llm, browser, controller)
            
            if success:
                successful_urls.append(website_url)
            else:
                failed_urls.append(website_url)
            
            # Add delay between requests (60 seconds)
            if i < len(RESTAURANT_URLS) - 1:  # Don't delay after the last URL
                print("\nWaiting 60 seconds before processing next restaurant...")
                await asyncio.sleep(60)
        
        # Print summary
        print("\nProcessing Summary:")
        print(f"Total restaurants processed: {len(RESTAURANT_URLS)}")
        print(f"Successful: {len(successful_urls)}")
        print(f"Failed: {len(failed_urls)}")
        print(f"Total input tokens used: {total_input_tokens}")
        print(f"Total output tokens used: {total_output_tokens}")
        print(f"Total tokens used: {total_input_tokens + total_output_tokens}")
        
        # Calculate and print averages
        if len(successful_urls) > 0:
            avg_input_tokens = total_input_tokens / len(successful_urls)
            avg_output_tokens = total_output_tokens / len(successful_urls)
            avg_total_tokens = (total_input_tokens + total_output_tokens) / len(successful_urls)
            print(f"\nAverage tokens per successful restaurant:")
            print(f"Average input tokens: {avg_input_tokens:.2f}")
            print(f"Average output tokens: {avg_output_tokens:.2f}")
            print(f"Average total tokens: {avg_total_tokens:.2f}")
        
        if failed_urls:
            print("\nFailed URLs:")
            for url in failed_urls:
                print(f"- {url}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Make sure to close the browser
        try:
            await browser.close()
        except:
            pass

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

