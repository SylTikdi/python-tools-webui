import os
from comtypes import client

def export_ppt_to_jpg(ppt_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    powerpoint = client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    ppt = powerpoint.Presentations.Open(ppt_path, WithWindow=False)
    ppt.SaveAs(output_folder, 17)  # 17 = Export as JPG
    ppt.Close()

    powerpoint.Quit()
    print(f"✅ Exported slides to {output_folder}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python export_ppt_to_jpg.py <path_to_pptx> <output_folder>")
        sys.exit(1)

    pptx_path = sys.argv[1]
    output_folder = sys.argv[2]

    export_ppt_to_jpg(pptx_path, output_folder)
