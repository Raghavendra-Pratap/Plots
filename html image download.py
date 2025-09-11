import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import filedialog

def download_images_from_url_html(html_url, output_directory="downloaded_images"):
    """
    Fetches an HTML file from a URL, parses it, extracts image URLs, and downloads them.

    Args:
        html_url (str): The URL of the HTML file.
        output_directory (str): Directory to save the downloaded images.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    try:
        print(f"Fetching HTML from: {html_url}")
        html_response = requests.get(html_url)
        html_response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        html_content = html_response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML from {html_url}: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')

    if not img_tags:
        print(f"No <img> tags found in {html_url}.")
        return

    for img_tag in img_tags:
        img_url = img_tag.get('src')
        if img_url:
            # Construct absolute URL, important for relative paths within HTML
            absolute_img_url = urljoin(html_url, img_url)

            try:
                print(f"Attempting to download image: {absolute_img_url}")
                image_response = requests.get(absolute_img_url, stream=True)
                image_response.raise_for_status() # Raise an exception for bad status codes

                # Get filename from URL or Content-Disposition header
                parsed_url = urlparse(absolute_img_url)
                filename = os.path.basename(parsed_url.path)
                
                # Fallback if filename is empty or not useful
                if not filename or '.' not in filename: # Check for extension
                    content_disposition = image_response.headers.get('content-disposition')
                    if content_disposition:
                        import re
                        fname_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                        if fname_match:
                            filename = fname_match.group(1)
                
                # Final fallback: generate a unique name
                if not filename or '.' not in filename:
                    # Try to guess extension from content-type
                    content_type = image_response.headers.get('content-type', '').split(';')[0]
                    ext = content_type.split('/')[-1] if '/' in content_type else 'jpg' # Default to jpg
                    filename = f"image_{os.urandom(4).hex()}.{ext}"

                save_path = os.path.join(output_directory, filename)

                with open(save_path, 'wb') as out_file:
                    for chunk in image_response.iter_content(chunk_size=8192):
                        out_file.write(chunk)
                print(f"Downloaded: {filename} to {save_path}")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {absolute_img_url}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred for image {absolute_img_url}: {e}")

def pick_local_html_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select HTML file",
        filetypes=[("HTML files", "*.html;*.htm"), ("All files", "*.*")]
    )
    return file_path

# Usage:
local_html_path = pick_local_html_file()
if local_html_path:
    # Now read the HTML file and pass its content to your image downloader
    with open(local_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    # You'd need to slightly modify your function to accept HTML content directly
    # For now, you can parse and download images from this content
else:
    print("No file selected.")

# --- How to use it with your example ---
# The HTML link you provided
your_html_link = "https://traxus.s3.amazonaws.com/heinekentw/scene-images/3274743/Stitched_Scene3274743_2025052916025202S_tiles.html"

# Call the function to download images from this HTML link
download_images_from_url_html(your_html_link, output_directory="heineken_images")

print("\nProcess completed for the provided HTML link.")