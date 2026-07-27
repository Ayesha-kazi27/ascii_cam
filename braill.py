from PIL import Image

def image_to_colored_braille_html(image_path, output_html_path, new_width=100):
    # 1. Load image and ensure it's in RGB mode
    img = Image.open(image_path).convert('RGB')
    
    # Calculate height based on target width and aspect ratio
    # (0.5 multiplier balances the tall layout of Braille text)
    aspect_ratio = img.height / img.width
    new_height = int(new_width * aspect_ratio * 0.5)
    
    # Resize image so that each 2x4 block matches our structural grid
    img_resized = img.resize((new_width * 2, new_height * 4), Image.Resampling.LANCZOS)
    
    # Create a grayscale copy specifically for dot thresholding
    img_gray = img_resized.convert('L')
    pixels_gray = img_gray.load()
    pixels_rgb = img_resized.load()
    
    threshold = 127
    
    # Build the HTML document structure with CSS
    html_content = ["""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Colored Braille ASCII Art</title>
    <style>
        body {
            background-color: #0b0c10; /* Dark premium background */
            color: #ffffff;
            font-family: monospace;
            font-size: 13px;
            line-height: 1.1;
            letter-spacing: 0.5px;
            text-align: center;
            padding: 40px 10px;
            margin: 0;
        }
        .ascii-container {
            display: inline-block;
            background-color: #020204;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.8);
            border: 1px solid #1f2833;
            white-space: pre; /* Essential to preserve spacing and line breaks */
        }
    </style>
</head>
<body>
    <div class="ascii-container">"""]

    # 2. Step through the image in 2x4 pixel blocks
    for y in range(0, img_resized.height, 4):
        row_pieces = []
        for x in range(0, img_resized.width, 2):
            dots = [0] * 8
            
            # Map pixel luminance to the 8 Braille dot flags
            if pixels_gray[x, y] > threshold:     dots[0] = 1
            if pixels_gray[x, y+1] > threshold:   dots[1] = 1
            if pixels_gray[x, y+2] > threshold:   dots[2] = 1
            if pixels_gray[x, y+3] > threshold:   dots[6] = 1
            if pixels_gray[x+1, y] > threshold:   dots[3] = 1
            if pixels_gray[x+1, y+1] > threshold: dots[4] = 1
            if pixels_gray[x+1, y+2] > threshold: dots[5] = 1
            if pixels_gray[x+1, y+3] > threshold: dots[7] = 1
            
            # Compute Unicode point
            braille_code = 0x2800
            for i in range(8):
                if dots[i]:
                    braille_code += (1 << i)
            
            # 3. Sample the colors inside this 2x4 block to find the average RGB color
            r_total, g_total, b_total = 0, 0, 0
            for dy in range(4):
                for dx in range(2):
                    r, g, b = pixels_rgb[x+dx, y+dy]
                    r_total += r
                    g_total += g
                    b_total += b
            
            avg_r = r_total // 8
            avg_g = g_total // 8
            avg_b = b_total // 8
            
            char = chr(braille_code)
            
            # Optimization: Use standard spaces for completely empty blocks
            if braille_code == 0x2800:
                row_pieces.append(" ")
            else:
                # Wrap character in colored inline span
                row_pieces.append(f'<span style="color: rgb({avg_r},{avg_g},{avg_b});">{char}</span>')
                
        html_content.append("".join(row_pieces) + "\n")
        
    html_content.append("""</div>
</body>
</html>""")
    
    # Save code to HTML output
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write("".join(html_content))
    print(f"Successfully generated colored Braille art at: {output_html_path}")

# --- Execution ---
# Replace 'your_image.png' with your file path
image_to_colored_braille_html('D:/vs code data/me.jpeg', 'my_braille_art.html', new_width=120)