import os
import subprocess

def convert_svg_to_png():
    icons_dir = 'media/icons'
    svg_files = [f for f in os.listdir(icons_dir) if f.endswith('.svg')]
    
    for svg_file in svg_files:
        svg_path = os.path.join(icons_dir, svg_file)
        png_path = os.path.join(icons_dir, svg_file.replace('.svg', '.png'))
        
        try:
            # Convert SVG to PNG using rsvg-convert
            subprocess.run([
                'rsvg-convert',
                '-w', '32',  # width
                '-h', '32',  # height
                '-o', png_path,  # output file
                svg_path  # input file
            ], check=True)
            print(f"Converted {svg_file} to PNG")
        except Exception as e:
            print(f"Error converting {svg_file}: {e}")

if __name__ == "__main__":
    convert_svg_to_png() 