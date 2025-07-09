import os
from comtypes import client

def export_ppt_to_jpg(ppt_path, output_dir):
    # Convert both paths to absolute paths
    ppt_path = os.path.abspath(ppt_path)
    output_dir = os.path.abspath(output_dir)

    # Print the paths (for debugging)
    print("Opening:", ppt_path)
    print("Saving to:", output_dir)

    if not os.path.exists(ppt_path):
        raise FileNotFoundError(f"PPTX file not found: {ppt_path}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Launch PowerPoint COM interface
    powerpoint = client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    # Open the file and export
    presentation = powerpoint.Presentations.Open(ppt_path, WithWindow=False)
    presentation.SaveAs(output_dir, 17)  # 17 = ppSaveAsJPG
    presentation.Close()
    powerpoint.Quit()

    return sorted(os.listdir(output_dir))
