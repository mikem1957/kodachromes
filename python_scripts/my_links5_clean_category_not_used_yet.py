import dropbox
import json
import os
import re # Import the regular expression module
from dropbox.exceptions import ApiError, AuthError
from dropbox.sharing import SharedLinkSettings, RequestedVisibility

# --- Configuration ---
# ACCESS_TOKEN = 'abc'  # Replace with your actual Dropbox access token
ACCESS_TOKEN = 'sl.u.AFvATks9gagMIjdGkZZzrrXJF75FT0KS_OFWZ6HDYmaJjnKX4xTNR04143yF1Oxf5yj8MWjgLkWoWJSHWXrwKXNaNOrIYoUatBbaRwUy8aGi0Jx06cRKer8zXH5dWdxjeN1P0sV3ZuhokBLjNaUmM3n0gLWNTZeMcGJBRr2mqF5RYFHeDu6yasDK1UVGIEpumB7O2SgC14cL4psMuLKJo5iAeFzlesm_NW7abHGMEVyncKn50oY4AhhT0UHNgVb-ZmxgmaOqtpnb_1wOvjUDIMGhbwoZbXHjstBfaczb3YlF4owmgv4dSKiwTWwxbUV_FUycv0Y6IbQ53g_bUMLt6VvPkeIZOHj-dJ0ZABE6HSdN58BXjSZy_-BL5wEXBrp7xNS2lTeS59oWgKtAu-e0R-1c8Teo1sGJJCfpyBhexuQ66eABtfZ0Uc3klCVth4H5L0f7kFw39TASTR6ZDfIsXhG0B9u5yd8ZbxvhWMd3snRrmSZDg-mEmjCsWq5hYO2E0_WNdGlERV3jksUY2_dp8b76QA_Npp1ZGLKwtjVbhoOf-crJNGtyfQiwmDZ0AaB8pAuwupqa-iQdtbUn7voLpdt7OJCUdZ9FtKWTUNJICpsq7kHJ8bAUju5SvFfc1ozqH-ZrOrFsyejGsI0m9dIA4VaDiWgGVCqE_UJtg_Jy0toeZq2b9aLAxPftZElAWN5m3tZeX8h8-UbZSh65S-lRLCTWirpxS8ICh68KtlSBlIg1-yWR1wSHo1yNrNluSYD0KZsv3b3ikfH1K_sD3PAlF6punY6mA9_E8mteSSKlQNbW5U6CznNlDlBZuZlGPV62W19Iq41DFjDAVoOKyO3t8Q5dmb0-zOuYc52wImYQjDOQL3NQyk4UnLsruUdrX4oi2uroaThcOX74Q6IJPIEGDkaABDZPZyEq3xDYjv2FpbCe1n6McXrR3pvIGvysGGkm6IhSreU46DB3yffo7-xb8RSSaJ08uBgV-eFoqbNePqkK876l8UwIQVBUTVAFCwQQhWZF8An0GdLC_KTsHvcKwfZT_t5QiiGqk4R8FBHywCoFqqlm7XAaXPa7-0Cv_ZqYss3uYd8AMY26qrfPVn2rg7qS2Mqvl4rQ8JI0BRQeLBBe-wdw_Spf1lVkaNs1HpGmIvybdH1u2hmCQD2SatcDzj5ryb_ixBex87-FYjmHEQc9W-InyfnZkg54aYQnGFeXp0RPeIH479QNWvVw5WtZJI9-xu6QL0dqXQI02g2Z8RYZ1y27j2XkD_uzgg1GRlhs-TPLXNa_t-GKqhygeTvsbjpi'
BASE_DROPBOX_PATH = "/kodachromes/RAJ"  # The main folder containing subfolders of images
OUTPUT_JSON = "all_images_data.json"  # Name of the output JSON file

# --- Helper Function to Clean Text ---
def clean_category_name(name):
    """
    Cleans a string by removing numbers, special characters, and extra spaces.
    Converts to lowercase.
    """
    # 1. Remove numbers
    cleaned_name = re.sub(r'\d+', '', name)
    # 2. Remove special characters (keep letters, spaces, and hyphens if desired)
    #    Here, we keep letters, spaces, and hyphens. You can adjust this regex
    #    to include/exclude other characters based on what you consider "meaningful".
    cleaned_name = re.sub(r'[^\w\s-]', '', cleaned_name) # Keep word chars, spaces, hyphens
    # 3. Replace multiple spaces with a single space
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    # 4. Strip leading/trailing whitespace
    cleaned_name = cleaned_name.strip()
    # 5. Optionally, convert to lowercase for consistency
    cleaned_name = cleaned_name.lower()
    return cleaned_name

# --- Helper Function to Create Shared Links ---
def create_shared_link(dbx, path):
    """
    Creates or retrieves a public shared link for a given Dropbox path.
    """
    try:
        # Try to create a public shared link
        settings = SharedLinkSettings(requested_visibility=RequestedVisibility.public)
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(path=path, settings=settings)
        return shared_link_metadata.url
    except ApiError as err:
        # If a shared link already exists, retrieve it
        if err.error.is_shared_link_already_exists():
            links = dbx.sharing_list_shared_links(path=path, direct_only=True)
            if links.links:
                return links.links[0].url
        print(f"Failed to create or retrieve shared link for {path}: {err}")
        return None

# --- Main Logic to List Files and Create JSON ---
def process_dropbox_folders():
    """
    Connects to Dropbox, iterates through subfolders, and generates
    a JSON file with image data and public links.
    """
    all_image_data = []

    try:
        dbx = dropbox.Dropbox(ACCESS_TOKEN)
        print("Connected to Dropbox.")

        # List contents of the base Dropbox path
        print(f"Listing subfolders in: {BASE_DROPBOX_PATH}")
        base_folder_response = dbx.files_list_folder(BASE_DROPBOX_PATH)

        subfolders_to_process = []
        for entry in base_folder_response.entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                subfolders_to_process.append(entry)

        if not subfolders_to_process:
            print(f"No subfolders found in {BASE_DROPBOX_PATH}. Exiting.")
            return

        for subfolder in subfolders_to_process:
            original_category_name = subfolder.name

            # Clean the category name for use in the 'name' field
            cleaned_category_name = clean_category_name(original_category_name)

            subfolder_path = subfolder.path_lower
            print(f"\nProcessing category: '{original_category_name}' (Cleaned: '{cleaned_category_name}') from folder: {subfolder_path}")

            response = dbx.files_list_folder(subfolder_path)

            while True:
                for entry in response.entries:
                    if isinstance(entry, dropbox.files.FileMetadata):
                        base_name, ext = os.path.splitext(entry.name)

                        # Skip files that are already thumbnails (e.g., "image_thumb.jpg")
                        if "_thumb" in base_name.lower():
                            continue

                        print(f"  Processing image: {entry.name}")

                        # Create shared link for the original file
                        original_url = create_shared_link(dbx, entry.path_lower)
                        if not original_url:
                            print(f"    Skipping {entry.name} due to shared link creation failure.")
                            continue

                        # Convert to direct download link
                        direct_url = original_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "raw=1")

                        # Attempt to locate the thumbnail version
                        thumb_filename = f"{base_name}_thumb{ext}"
                        thumb_path = f"{subfolder_path}/{thumb_filename}"
                        thumb_url = create_shared_link(dbx, thumb_path)

                        direct_thumb_url = None
                        if thumb_url:
                            direct_thumb_url = thumb_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "raw=1")
                        else:
                            print(f"    Warning: Thumbnail not found for {entry.name} at expected path: {thumb_path}")

                        # Construct the new 'name' field using the cleaned category name
                        # We might also want to clean the base_name if it also contains undesirable characters.
                        # For simplicity, we'll just use the original base_name here,
                        # but you could apply a similar clean_category_name function to base_name as well.
                        new_name_field = f"{cleaned_category_name}_{base_name}"

                        all_image_data.append({
                            "name": new_name_field,
                            "category": original_category_name, # Keep original for 'category'
                            "thumb": direct_thumb_url,
                            "url": direct_url
                        })

                if response.has_more:
                    response = dbx.files_list_folder_continue(response.cursor)
                else:
                    break

        # Save all collected data to JSON
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(all_image_data, f, indent=2)
        print(f"\n✅ Successfully processed all folders. JSON data saved to {OUTPUT_JSON}")

    except AuthError as e:
        print(f"[AuthError] Please check your Dropbox access token and app permissions: {e}")
    except ApiError as err:
        print(f"[ApiError] A Dropbox API error occurred: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Run the Script ---
if __name__ == "__main__":
    process_dropbox_folders()
    