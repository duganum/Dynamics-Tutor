import matplotlib.pyplot as plt
import numpy as np
import os
import io
import re

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    FIXED: Robust number extraction to prevent 'HW7' from being read as '7.png'.
    """
    if isinstance(prob, dict):
        pid = str(prob.get('id', '')).strip()
    else:
        pid = str(prob).strip()
        prob = {}

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_aspect('equal')
    found = False

    # --- 1. Procedural Statics Diagrams ---
    if pid.startswith("S_1"):
        if pid == "S_1.1_1":
            ax.plot(0, 0, 'ko', markersize=8)
            ax.annotate('', xy=(-1.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
            ax.annotate('', xy=(1.2, 1.2), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
            ax.annotate('', xy=(0, -1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.2_1":
            pts = np.array([[0,0], [2,1], [4,0], [2,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2); ax.plot([2,2], [0,1], 'k-', lw=2)
            found = True

    # --- 2. Dynamics Image Loader ---
    if not found:
        category = str(prob.get("category", "")).lower()
        
        # FIXED: Extraction logic. 
        # If ID is "HW7_67", this looks for the number AFTER the underscore/dash.
        if "_" in pid:
            image_number = pid.split("_")[-1]
        elif "-" in pid:
            image_number = pid.split("-")[-1]
        else:
            # Fallback to standard regex if no separator found
            match = re.search(r'(\d+)$', pid)
            image_number = match.group(1) if match else pid
            
        image_filename = f"{image_number}.png"
        folder_name = None

        # Mapping to the exact folder names in your repository
        if "curvilinear" in category or "hw 7" in pid.lower() or "hw7" in pid.lower():
            folder_name = "HW 7 (kinetics of particles-curvilinear motion)"
        elif "rectilinear" in category or "hw 6" in pid.lower() or "hw6" in pid.lower():
            folder_name = "HW 6 (kinetics of particles-rectilinear motion)"
        elif "impact" in category or "hw 10" in pid.lower():
            folder_name = "HW 10 (Impact)"
        elif "momentum" in category or "impulse" in category or "hw 9" in pid.lower():
            folder_name = "HW 9 (Impuls and momentum)"
        elif "work" in category or "energy" in category or "hw 8" in pid.lower():
            folder_name = "HW 8 (work and energy)"
        elif "rotation" in category or "rigid" in category or "hw 11" in pid.lower():
            folder_name = "HW 11 (kinematics of rigid body-rotation)"
            # Manual overrides for HW 11
            if pid.endswith("_1"): image_filename = "71.png"
            elif pid.endswith("_2"): image_filename = "6.png"
            elif pid.endswith("_3"): image_filename = "16.png"

        # List of paths to try (Triple-nested /images/ structure)
        paths_to_try = []
        if folder_name:
            paths_to_try.append(os.path.join('images', folder_name, 'images', image_filename))
            paths_to_try.append(os.path.join('images', folder_name, image_filename))

        # Absolute fallbacks
        clean_pid = pid.replace("_", "").replace(".", "").replace("-", "").replace(" ", "").lower()
        paths_to_try.append(os.path.join('images', f"{clean_pid}.png"))
        paths_to_try.append(os.path.join('images', image_filename))

        for img_path in paths_to_try:
            if os.path.exists(img_path):
                try:
                    img = plt.imread(img_path)
                    ax.imshow(img)
                    h, w = img.shape[:2]
                    ax.set_xlim(0, w); ax.set_ylim(h, 0)
                    found = True
                    break
                except: continue

    if not found:
        ax.text(0.5, 0.5, f"Not Found: {image_filename}\nID: {pid}\nPath: images/{folder_name}/images/", color='red', ha='center', va='center', fontsize=8)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.axhline(0, color='black', lw=1.5); ax.axvline(0, color='black', lw=1.5)
    ax.grid(True, linestyle=':', alpha=0.6); ax.set_aspect('equal')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
