import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    FIXED: Strips ID formatting to match root filenames (e.g., K_2.5_1 -> k251.png).
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
        # ... (Other Statics procedural code remains here)

    # --- 2. Dynamics Image Loader (HW Folders & Root) ---
    if not found:
        category = str(prob.get("category", "")).lower()
        
        # CLEAN FILENAMES: Turn "K_2.5_1" into "k251.png" to match your root files
        clean_pid = pid.replace("_", "").replace(".", "").lower()
        image_filename = f"{clean_pid}.png"
        
        # FOLDER MAPPING:
        folder_name = None
        if "rotation" in category or "rigid" in category or pid.startswith("K_2.6"):
            folder_name = "HW 11 (kinematics of rigid body-rotation)"
            if pid.endswith("_1"): image_filename = "71.png"
            elif pid.endswith("_2"): image_filename = "6.png"
            elif pid.endswith("_3"): image_filename = "16.png"
        elif "curvilinear" in category or "hw7" in clean_pid:
            folder_name = "HW 7 (kinetics of particles-curvilinear motion)"
            if "_" in pid: image_filename = f"{pid.split('_')[-1]}.png"
        elif "rectilinear" in category or "hw6" in clean_pid:
            folder_name = "HW 6 (kinetics of particles-rectilinear motion)"
            if "_" in pid: image_filename = f"{pid.split('_')[-1]}.png"
        elif "impact" in category:
            folder_name = "HW 10 (Impact)"
        elif "momentum" in category or "impulse" in category:
            folder_name = "HW 9 (Impuls and momentum)"
        elif "work" in category or "energy" in category:
            folder_name = "HW 8 (work and energy)"

        # SEARCH PATHS
        paths_to_try = []
        if folder_name:
            paths_to_try.append(os.path.join('images', folder_name, 'images', image_filename))
            paths_to_try.append(os.path.join('images', folder_name, image_filename))
        
        # ALWAYS try the root images folder (This fixes K_2.1, K_2.2, K_2.3, K_2.4, K_2.5)
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
        ax.text(0.5, 0.5, f"Diagram Not Found\nID: {pid}\nSearch: {image_filename}", color='red', ha='center', va='center', fontsize=8)
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
