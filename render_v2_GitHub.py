import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    Supports nested paths: images/[HW Folder]/images/[ID].png
    """
    if isinstance(prob, dict):
        pid = str(prob.get('id', '')).strip()
    else:
        pid = str(prob).strip()
        prob = {}

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_aspect('equal')
    found = False

    # --- 1. Procedural Statics Diagrams (S_1.1 to S_1.4) ---
    # [Keep your existing procedural logic here]

    # --- 2. HW Directory Image Loader (FIXED FOR HW 9 DIRECTORY) ---
    if not found:
        hw_title = prob.get("hw_title")
        hw_subtitle = prob.get("hw_subtitle")
        category = str(prob.get("category", "")).lower()
        
        folder_name = None
        
        # Check for Momentum/Impulse IDs (176, 198, 209) and map to HW 9 folder
        if any(x in category for x in ["momentum", "impulse"]) or pid in ["176", "198", "209"]:
            # Corrected to match your GitHub: "HW 9 (Impuls and momentum)"
            folder_name = "HW 9 (Impuls and momentum)"
            image_filename = f"{pid}.png"
        elif "work" in category or "energy" in category or pid in ["141", "158", "161", "162"]:
            folder_name = "HW 8 (work and energy)"
            image_filename = f"{pid}.png"
        elif hw_title and hw_subtitle:
            if hw_title == "HW 7":
                folder_name = f"HW 7  ({hw_subtitle})" 
            else:
                folder_name = f"{hw_title} ({hw_subtitle})"
            image_filename = f"{pid.split('_')[-1]}.png"

        if folder_name:
            # Construct path: images/HW 9 (Impuls and momentum)/images/176.png
            img_path = os.path.join('images', folder_name, 'images', image_filename)
            try:
                if os.path.exists(img_path):
                    img = plt.imread(img_path)
                    ax.imshow(img)
                    h, w = img.shape[:2]
                    ax.set_xlim(0, w); ax.set_ylim(h, 0)
                    found = True
            except Exception:
                pass
        
        # Fallback to root images folder
        if not found:
            clean_name = pid.replace("_", "").replace(".", "").lower()
            img_path_alt = os.path.join('images', f'{clean_name}.png')
            if os.path.exists(img_path_alt):
                try:
                    img = plt.imread(img_path_alt)
                    ax.imshow(img)
                    h, w = img.shape[:2]
                    ax.set_xlim(0, w); ax.set_ylim(h, 0)
                    found = True
                except Exception:
                    pass

    # --- 3. Error Handling ---
    if not found:
        ax.text(0.5, 0.5, f"Diagram Not Found\nID: {pid}", color='red', ha='center', va='center')
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axis('off')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
