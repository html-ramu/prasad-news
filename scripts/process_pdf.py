import os
import sys
import shutil
import subprocess
import glob
import re
from PIL import Image

# CONFIGURATION
UPLOADS_DIR = "uploads"
PAPERS_DIR = "papers"
ASSETS_DIR = "assets"
INDEX_HTML_FILE = "index.html"
DOMAIN_URL = "https://epaperprasadnews.in"

def main():
    # 1. Find the PDF
    pdfs = glob.glob(os.path.join(UPLOADS_DIR, "*.pdf"))
    if not pdfs:
        print("No PDF found in uploads/ folder.")
        return

    pdf_path = pdfs[0]
    filename = os.path.basename(pdf_path)
    date_str = filename.replace(".pdf", "")
    
    print(f"Processing Edition: {date_str}")

    # 2. Create Output Directory
    output_dir = os.path.join(PAPERS_DIR, date_str)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # 3. Convert PDF to Images
    subprocess.run([
        "pdftoppm", 
        "-png", 
        pdf_path, 
        os.path.join(output_dir, "")
    ], check=True)

    # 4. Rename images to 1.png, 2.png, etc.
    generated_images = sorted(glob.glob(os.path.join(output_dir, "*.png")))
    page_count = len(generated_images)
    
    final_images = []
    for i, img_path in enumerate(generated_images):
        new_name = f"{i+1}.png"
        new_path = os.path.join(output_dir, new_path_name:=new_name)
        os.rename(img_path, new_path)
        final_images.append(new_path)
    
    print(f"Generated {page_count} pages.")

    # 5. Create WhatsApp Preview (Smart Crop + Compression)
    if final_images:
        create_smart_preview(date_str, final_images[0])

    # 6. Move PDF to target folder
    target_pdf = os.path.join(output_dir, "full.pdf")
    shutil.move(pdf_path, target_pdf)

    print("Processing Complete! (JSON mapping will be handled by GitHub Actions)")

def create_smart_preview(date_str, source_image_path):
    target_cover = os.path.join(ASSETS_DIR, "latest-cover.jpg")
    
    # --- SMART CROP LOGIC ---
    with Image.open(source_image_path) as img:
        width, height = img.size
        crop_height = int(height * 0.45) 
        cropped_img = img.crop((0, 0, width, crop_height))
        
        cropped_img = cropped_img.convert("RGB")
        cropped_img.save(target_cover, "JPEG", optimize=True, quality=70)
        
        print(f"Created Smart Crop (Top 45%) for WhatsApp preview [Optimized JPG]")

    # Update index.html social tags
    with open(INDEX_HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    new_image_url = f"{DOMAIN_URL}/assets/latest-cover.jpg?v={date_str}"
    
    # Regex to replace the content inside og:image meta tag
    pattern_og = r'(<meta property="og:image" content=")(.*?)(")'
    
    if re.search(pattern_og, html_content):
        new_content = re.sub(pattern_og, r'\1' + new_image_url + r'\3', html_content)
        with open(INDEX_HTML_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated index.html og:image to {new_image_url}")
    else:
        print("Warning: Could not find og:image meta tag in index.html")

if __name__ == "__main__":
    main()