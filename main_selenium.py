"""
YC Cofounder Matcher Bot
Automatically finds and invites cofounders interested in biomedical/biotech/robotics/health tech
using Selenium and local Ollama for text analysis.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import ollama
import time
import re
from typing import Optional, Tuple


def check_ollama_connection(model_name: str, debug: bool = False) -> bool:
    """Check if Ollama is running and the model is available."""
    # Create Ollama client with explicit host
    client = ollama.Client(host='http://localhost:11434')
    response = client.list()

    # Handle different possible response structures
    available_models = []
    if hasattr(response, 'models'):
        # Response is an object with models attribute
        for model in response.models:
            if hasattr(model, 'model'):
                available_models.append(model.model)
            elif hasattr(model, 'name'):
                available_models.append(model.name)
            else:
                available_models.append(str(model))
    elif "models" in response:
        # Response is a dict
        for model in response["models"]:
            # Try different possible keys for the model name
            if "name" in model:
                available_models.append(model["name"])
            elif "model" in model:
                available_models.append(model["model"])
            else:
                # If neither key exists, add the whole model object for debugging
                available_models.append(str(model))

    if model_name not in available_models:
        print(
            f"Model {model_name} not found. Available models: {available_models}"
        )
        return False

    print(f"Connected to Ollama with model: {model_name}")
    return True


def analyze_text_for_interests(
    text: str, model_name: str, debug: bool = False
) -> Tuple[bool, str, str]:
    """
    Analyze text using Ollama to detect biomedical/biotech/robotics/health tech EXPERIENCE.

    Returns:
        Tuple of (has_experience, person_name, analysis_summary)
    """
    prompt = f"""
    CRITICAL INSTRUCTION: You MUST answer NO unless the person has CONCRETE, VERIFIABLE EXPERIENCE in ONE OF TWO CATEGORIES:

    CATEGORY 1 - ROBOTICS (ANY TYPE):
    - ANY robotics experience counts, even if NOT medical/healthcare related
    - Robotics engineering
    - Built robots (industrial, consumer, research, hobby, ANY type)
    - Robotics competitions (name/year of competition)
    - Robotics coursework or robotics degree
    - Worked in robotics
    - Specific robotics projects described
    - Mechatronics, control systems for robots, robot design
    
    CATEGORY 2 - MEDICAL/BIOTECH/HEALTHCARE (ANY TYPE):
    - Worked at healthcare/biotech/medical/pharma companies (job title, company name)
    - Built healthcare/medical products, apps, or services (specific product/project)
    - Clinical experience (doctors, nurses, healthcare providers, medical students)
    - Founded or worked at medtech, biotech, pharmaceutical startups
    - Medical device development (specific device or project)
    - Bioinformatics, computational biology work (specific projects/research)
    - Digital health, AI in healthcare projects (specific applications)
    - Laboratory experience with biological/medical research described
    - Degrees in biomedical engineering, biotechnology, biology, medicine, or related fields
    - Drug development, clinical trials, medical research

    SAYING "I'M INTERESTED IN" OR LISTING TOPICS AS "INTERESTS" DOES NOT COUNT AS EXPERIENCE.

    IMPORTANT CLARIFICATIONS:
    - ROBOTICS ALONE = YES (doesn't need to be medical)
    - MEDICAL/BIOTECH ALONE = YES (doesn't need to be robotics)
    - GENERAL ENGINEERING = NO (unless it's robotics engineering specifically)
    - Mechanical engineering, electrical engineering, software engineering = NO (unless applied to robotics or medical/biotech)

    AUTOMATICALLY ANSWER NO FOR:
    - General "Health/Wellness" interest without specific healthcare work
    - Listing "Biomedical/Biotech" or "Robotics" under interests WITHOUT describing actual work
    - "Interested in healthcare" or "want to work in biotech" aspirational statements
    - General engineering (mechanical, electrical, software) NOT applied to robotics or medical
    - General AI/software work without specific healthcare/robotics application
    - Wellness, fitness, meditation, nutrition apps
    - No concrete examples of work, projects, or education in these fields

    VERIFICATION TEST: If you cannot identify a SPECIFIC project, job, degree, or accomplishment in ROBOTICS (any type) OR MEDICAL/BIOTECH/HEALTHCARE from the text, the answer MUST be NO.

    Text to analyze:
    {text}
    
    Please respond in this exact format:
    NAME: [person's name or "Unknown" if not found]
    EXPERIENCE: [YES or NO]
    SUMMARY: [List the SPECIFIC experience found (job titles, company names, projects, degrees, etc.) OR state "No specific robotics or biotech/healthcare/medical experience found - only general interest mentioned"]
    """

    # Create Ollama client with explicit host
    client = ollama.Client(host='http://localhost:11434')
    response = client.generate(model=model_name, prompt=prompt, stream=False)

    analysis = response["response"]
    print(f"Ollama analysis:\n{analysis}\n")

    # Parse the response
    name_match = re.search(r"NAME:\s*(.+)", analysis)
    experience_match = re.search(
        r"EXPERIENCE:\s*(YES|NO)", analysis, re.IGNORECASE
    )
    summary_match = re.search(r"SUMMARY:\s*(.+)", analysis, re.DOTALL)

    person_name = name_match.group(1).strip() if name_match else "Unknown"
    has_experience = (
        experience_match and experience_match.group(1).upper() == "YES"
    )
    summary = (
        summary_match.group(1).strip()
        if summary_match
        else "No summary available"
    )

    print("\n🐛 DEBUG: Parsed results:")
    print(f"🐛 DEBUG: Name extracted: '{person_name}'")
    print(f"🐛 DEBUG: Has experience: {has_experience}")
    print(f"🐛 DEBUG: Summary: '{summary}'")

    return has_experience, person_name, summary


def get_page_text(driver, debug: bool = False) -> str:
    """Get profile text content from the specific XPath location."""
    print("📄 Extracting profile text from XPath...")
    
    # Wait for the profile content to load and extract text from specific XPath
    wait = WebDriverWait(driver, 10)
    profile_element = wait.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/div/div/div[1]/div[1]"))
    )
    
    text = profile_element.text
    
    if debug:
        print(f"� DEBUG: XPath element found and extracted")
        print(f"🐛 DEBUG: First 200 chars: {text[:200]}...")
    
    print(f"✅ Extracted {len(text)} characters from profile section")
    return text
        



def get_profile_url(driver, debug: bool = False) -> str:
    """Get the current profile URL from the browser."""
    print("🌐 Getting current profile URL...")


    url = driver.current_url
    print(f"✅ Current profile URL: {url}")
    return url



def click_skip_button(driver, debug: bool = False) -> bool:
    """Click the skip button to move to next profile."""
    print("⏭️ Looking for skip button...")


    # Wait for and find the skip button with text "skip for now"
    wait = WebDriverWait(driver, 10)
    skip_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'skip for now') or contains(text(), 'Skip for now')]"))
    )
    
    if debug:
        print("🐛 DEBUG: Found skip button, clicking...")
    
    skip_button.click()
    time.sleep(2)  # Wait for page to load
    
    print("✅ Moved to next profile")
    return True



def save_candidate_to_file(
    person_name: str,
    url: str,
    summary: str,
    filename: str = "recommended_candidates.txt",
):
    """Save recommended candidate information to a text file."""
    import os
    from datetime import datetime

    # Create entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"""
{'='*60}
Date: {timestamp}
Name: {person_name}
URL: {url}
Reason: {summary}
{'='*60}

"""

    # Append to file
    with open(filename, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"💾 Saved {person_name} to {filename}")

    # Show file info
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
            candidate_count = len(
                [line for line in lines if line.startswith("Name:")]
            )
        print(f"📊 Total candidates saved: {candidate_count}")


def main(model: str = "llama3.2", debug: bool = False):
    """Main execution function."""
    print("🤖 YC Cofounder Matcher Bot Starting...")
    print("📝 URL Collection Mode - Saving recommended candidates to file")
    print("🌐 Using Selenium WebDriver for browser automation")

    # Check Ollama connection
    if not check_ollama_connection(model, debug):
        print(
            "❌ Cannot connect to Ollama. Make sure it's running and the model is available."
        )
        return False

    # Initialize Selenium WebDriver
    print("\n🚀 Starting browser...")

    driver = webdriver.Chrome()  # You can change to Firefox() if preferred
    driver.maximize_window()

    try:
        # Navigate to YC Startup School
        print("🌐 Navigating to Y Combinator Startup School...")
        driver.get("https://www.startupschool.org/cofounder-matching")
        
        print("\n=== MANUAL LOGIN REQUIRED ===")
        print("Please complete the following steps manually:")
        print("1. Log in to your Y Combinator account")
        print("2. Navigate to the cofounder matching section")
        print("3. Go to the first profile you want to analyze")
        print("4. Make sure you're on a candidate profile page")
        
        input("\nPress Enter when you're logged in and on the first candidate profile...")

        profile_count = 0

        while True:
            profile_count += 1
            print(f"\n🔍 Analyzing profile #{profile_count}...")

            # Get page content automatically
            page_text = get_page_text(driver, debug)
            if not page_text:
                print("❌ Could not get page content. Skipping this profile.")
                if not click_skip_button(driver, debug):
                    print("❌ Could not skip profile. Manual intervention required.")
                    input("Please navigate to the next profile manually and press Enter...")
                continue

            print(
                f"📄 Analyzing profile content ({len(page_text)} characters)..."
            )

            # Analyze text for experience
            has_experience, person_name, summary = analyze_text_for_interests(
                page_text, model, debug
            )

            print("\n=== ANALYSIS RESULTS ===")
            print(f"Name: {person_name}")
            print(f"Has relevant experience: {'YES' if has_experience else 'NO'}")
            print(f"Summary: {summary}")

            if has_experience:
                print(
                    f"\n✅ {person_name} has relevant experience in biotech/health tech/robotics!"
                )

                # Get the profile URL
                profile_url = get_profile_url(driver, debug)

                # Save to file
                save_candidate_to_file(person_name, profile_url, summary)

                print(f"💾 Added {person_name} to recommendations list!")
            else:
                print(
                    f"❌ {person_name} does not have relevant experience in biotech/health tech/robotics."
                )
                print("Skipping this candidate.")

            # In debug mode, ask user for confirmation
            if debug:
                print(f"\n🔄 Ready to move to next profile...")
                response = input(
                    "Continue to next profile? (y/N/q to quit): "
                ).lower()

                if response == "q":
                    print("🛑 Stopping automation as requested.")
                    break
                elif response != "y":
                    print("❌ Automation cancelled by user.")
                    break
            else:
                print(f"\n🔄 Moving to next profile automatically...")
                time.sleep(1)  # Brief pause between profiles

            # Click skip button to move to next profile
            if not click_skip_button(driver, debug):
                print("❌ Could not find skip button. Manual intervention required.")
                input("Please click 'skip for now' manually and press Enter...")



        print(f"\n📊 Session Summary:")
        print(f"   Profiles analyzed: {profile_count}")
        print(f"   Check 'recommended_candidates.txt' for saved candidates")
        print("✅ Automation completed!")
        
    finally:
        # Clean up
        print("\n🧹 Closing browser...")
        driver.quit()
        
    return True


if __name__ == "__main__":
    # Default execution - you can change these defaults
    main(model="qwen2.5:32b", debug=False)
