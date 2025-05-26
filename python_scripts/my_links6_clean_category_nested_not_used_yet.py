import dropbox
import json
import os
import re
from dropbox.exceptions import ApiError, AuthError
from dropbox.sharing import SharedLinkSettings, RequestedVisibility

# --- Configuration ---
# ACCESS_TOKEN = 'YOUR_DROPBOX_ACCESS_TOKEN'  # <<< IMPORTANT: Replace with your actual Dropbox access token
ACCESS_TOKEN = 'sl.u.AFvATks9gagMIjdGkZZzrrXJF75FT0KS_OFWZ6HDYmaJjnKX4xTNR04143yF1Oxf5yj8MWjgLkWoWJSHWXrwKXNaNOrIYoUatBbaRwUy8aGi0Jx06cRKer8zXH5dWdxjeN1P0sV3ZuhokBLjNaUmM3n0gLWNTZeMcGJBRr2mqF5RYFHeDu6yasDK1UVGIEpumB7O2SgC14cL4psMuLKJo5iAeFzlesm_NW7abHGMEVyncKn50oY4AhhT0UHNgVb-ZmxgmaOqtpnb_1wOvjUDIMGhbwoZbXHjstBfaczb3YlF4owmgv4dSKiwTWwxbUV_FUycv0Y6IbQ53g_bUMLt6VvPkeIZOHj-dJ0ZABE6HSdN58BXjSZy_-BL5wEXBrp7xNS2lTeS59oWgKtAu-e0R-1c8Teo1sGJJCfpyBhexuQ66eABtfZ0Uc3klCVth4H5L0f7kFw39TASTR6ZDfIsXhG0B9u5yd8ZbxvhWMd3snRrmSZDg-mEmjCsWq5hYO2E0_WNdGlERV3jksUY2_dp8b76QA_Npp1ZGLKwtjVbhoOf-crJNGtyfQiwmDZ0AaB8pAuwupqa-iQdtbUn7voLpdt7OJCUdZ9FtKWTUNJICpsq7kHJ8bAUju5SvFfc1ozqH-ZrOrFsyejGsI0m9dIA4VaDiWgGVCqE_UJtg_Jy0toeZq2b9aLAxPftZElAWN5m3tZeX8h8-UbZSh65S-lRLCTWirpxS8ICh68KtlSBlIg1-yWR1wSHo1yNrNluSYD0KZsv3b3ikfH1K_sD3PAlF6punY6mA9_E8mteSSKlQNbW5U6CznNlDlBZuZlGPV62W19Iq41DFjDAVoOKyO3t8Q5dmb0-zOuYc52wImYQjDOQL3NQyk4UnLsruUdrX4oi2uroaThcOX74Q6IJPIEGDkaABDZPZyEq3xDYjv2FpbCe1n6McXrR3pvIGvysGGkm6IhSreU46DB3yffo7-xb8RSSaJ08uBgV-eFoqbNePqkK876l8UwIQVBUTVAFCwQQhWZF8An0GdLC_KTsHvcKwfZT_t5QiiGqk4R8FBHywCoFqqlm7XAaXPa7-0Cv_ZqYss3uYd8AMY26qrfPVn2rg7qS2Mqvl4rQ8JI0BRQeLBBe-wdw_Spf1lVkaNs1HpGmIvybdH1u2hmCQD2SatcDzj5ryb_ixBex87-FYjmHEQc9W-InyfnZkg54aYQnGFeXp0RPeIH479QNWvVw5WtZJI9-xu6QL0dqXQI02g2Z8RYZ1y27j2XkD_uzgg1GRlhs-TPLXNa_t-GKqhygeTvsbjpi'
BASE_DROPBOX_PATH = "/kodachromes/RAJ"      # The main folder containing all nested subfolders and images
OUTPUT_JSON = "all_images_data_recursive.json" # Name of the output JSON file

# --- Helper Function to Clean Text ---
def clean_text(text):
    """
    Cleans a string by removing numbers, specific special characters, and extra spaces.
    Converts to lowercase for consistency.
    """
    # 1. Remove numbers
    text = re.sub(r'\d+', '', text)
    # 2. Remove characters that are not letters, spaces, or hyphens (allowing for some natural names)
    # Adjust this regex based on what special characters you want to retain or remove from category names.
    text = re.sub(r'[^a-zA-Z\s-]', '', text)
    # 3. Replace multiple spaces/hyphens with a single space, then strip leading/trailing spaces
    text = re.sub(r'[\s-]+', ' ', text).strip()
    # 4. Convert to lowercase
    text = text.lower()
    return text

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
        # Ignore "path not found" errors for thumbnails if they genuinely don't exist
        elif err.error.is_path_not_found():
            return None # Indicate that the path (e.g., thumbnail) was not found
        print(f"Failed to create or retrieve shared link for {path}: {err}")
        return None

# --- Recursive Folder Processing Function ---
def process_folder_recursively(dbx, current_dropbox_path, all_image_data):
    """
    Recursively processes a Dropbox folder, its subfolders, and files.
    Collects image data and shared links.
    """
    try:
        print(f"Entering folder: {current_dropbox_path}")
        response = dbx.files_list_folder(current_dropbox_path)

        while True:
            for entry in response.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    # It's a file, process it
                    base_name, ext = os.path.splitext(entry.name)

                    # Skip files that are already thumbnails
                    if "_thumb" in base_name.lower():
                        continue

                    # Get the immediate parent folder name to use as category
                    # os.path.basename returns the last component of the path
                    original_category_name = os.path.basename(current_dropbox_path)
                    # cleaned_category_name = clean_text(original_category_name)
                    cleaned_category_name = original_category_name # do not clean yet

                    print(f"  Processing image: {entry.name} in category: '{original_category_name}'")

                    # Create shared link for the original file
                    original_url = create_shared_link(dbx, entry.path_lower)
                    if not original_url:
                        print(f"    Skipping {entry.name} due to shared link creation failure or missing file.")
                        continue

                    # Convert to direct download link
                    direct_url = original_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "raw=1")

                    # Attempt to locate the thumbnail version
                    thumb_filename = f"{base_name}_thumb{ext}"
                    thumb_path = f"{current_dropbox_path}/{thumb_filename}" # Construct thumb path relative to current folder
                    thumb_url = create_shared_link(dbx, thumb_path)

                    direct_thumb_url = None
                    if thumb_url:
                        direct_thumb_url = thumb_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "raw=1")
                    else:
                        print(f"    Warning: Thumbnail not found for {entry.name} at expected path: {thumb_path}")

                    # Construct the 'name' field as cleaned_sub-directory_basename
                    new_name_field = f"{cleaned_category_name}_{base_name}"

                    all_image_data.append({
                        "name": new_name_field,
                        "category": original_category_name, # Keep original category name for the 'category' field
                        "thumb": direct_thumb_url,
                        "url": direct_url
                    })

                elif isinstance(entry, dropbox.files.FolderMetadata):
                    # It's a subfolder, recurse into it
                    process_folder_recursively(dbx, entry.path_lower, all_image_data)

            if response.has_more:
                response = dbx.files_list_folder_continue(response.cursor)
            else:
                break

    except ApiError as err:
        print(f"[ApiError] Error listing contents of {current_dropbox_path}: {err}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {current_dropbox_path}: {e}")


# --- Main Execution Function ---
def main():
    """
    Initializes Dropbox connection and starts the recursive folder processing.
    """
    all_image_data = [] # This list will be populated by the recursive calls

    try:
        dbx = dropbox.Dropbox(ACCESS_TOKEN)
        print("Connected to Dropbox.")

        # Start the recursive process from the base path
        process_folder_recursively(dbx, BASE_DROPBOX_PATH, all_image_data)

        # Save all collected data to JSON
        if all_image_data:
            with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                json.dump(all_image_data, f, indent=2)
            print(f"\n✅ Successfully processed all accessible folders. JSON data saved to {OUTPUT_JSON}")
        else:
            print(f"\n🤷 No image data found in {BASE_DROPBOX_PATH} or its subfolders. No JSON file generated.")


    except AuthError as e:
        print(f"[AuthError] Please check your Dropbox access token and app permissions: {e}")
    except ApiError as err:
        print(f"[ApiError] A Dropbox API error occurred during initial connection or root folder listing: {err}")
    except Exception as e:
        print(f"An unexpected error occurred during script execution: {e}")

# --- Run the Script ---
if __name__ == "__main__":
    main()
