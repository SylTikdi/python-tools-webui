import os
from comtypes import client

# === SET THESE VALUES ===
pptx_path = r"C:\Users\YourName\Documents\presentation.pptx"   # Input PPTX file
output_folder = r"C:\Users\YourName\Documents\SlidesAsJPG"     # Output folder
# =========================

def export_ppt_to_jpg(ppt_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    powerpoint = client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    ppt = powerpoint.Presentations.Open(ppt_path, WithWindow=False)
    ppt.SaveAs(output_dir, 17)  # 17 = ppSaveAsJPG
    ppt.Close()

    powerpoint.Quit()
    print(f"✅ Exported all slides as JPG to: {output_dir}")

if __name__ == "__main__":
    export_ppt_to_jpg(pptx_path, output_folder)
