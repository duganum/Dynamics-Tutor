import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    Supports nested paths: images/[HW Folder]/images/[ID].png
    """
    # Ensure we handle both the full object and just the ID for backward compatibility
    if isinstance(prob, dict):
        pid = str(prob.get('id', '')).strip()
    else:
        pid = str(prob).strip()
        prob = {}

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_aspect('equal')
    found = False

    # --- 1. Procedural Statics Diagrams ---
    if pid.startswith("S_1.1"):
        if pid == "S_1.1_1":
            ax.plot(0, 0, 'ko', markersize=8)
            ax.annotate('', xy=(-1.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
            ax.annotate('', xy=(1.2, 1.2), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
            ax.annotate('', xy=(0, -1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.text(-1.4, 0.2, '$T_A$', color='blue'); ax.text(1.0, 1.3, '$T_B (45^\circ)$', color='green')
            ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.1_2":
            theta = np.radians(30)
            ax.plot([-2, 2], [2*np.tan(-theta), -2*np.tan(-theta)], 'k-', lw=2)
            ax.add_patch(plt.Circle((0, 0.5), 0.5, color='gray', alpha=0.5))
            ax.set_xlim(-2, 2); ax.set_ylim(-1, 2)
            found = True

    # --- 2. HW Directory Image Loader ---
    if not found:
        hw_title = prob.get("hw_title")
        hw_subtitle = prob.get("hw_subtitle")
        category = str(prob.get("category", "")).lower()
        
        folder_name = None
        
        # Mapping for HW 10 (Impact) based on your true directory
        if "impact" in category or pid in ["239", "243", "249", "252"]:
            folder_name = "HW 10 (Impact)"
            image_filename = f"{pid}.png"
        # Mapping for HW 9 (Impuls and momentum)
        elif any(x in category for x in ["momentum", "impulse"]) or pid in ["176", "198", "209"]:
            folder_name = "HW 9 (Impuls and momentum)"
            image_filename = f"{pid}.png"
        # Mapping for HW 8 (work and energy)
        elif any(x in category for x in ["work", "energy"]) or pid in ["141", "158", "161", "162"]:
            folder_name = "HW 8 (work and energy)"
            image_filename = f"{pid}.png"
        elif hw_title and hw_subtitle:
            folder_name = f"{hw_title} ({hw_subtitle})"
            image_filename = f"{pid.split('_')[-1]}.png"

        if folder_name:
            img_path = os.path.join('images', folder_name, 'images', image_filename)
            if os.path.exists(img_path):
                try:
                    img = plt.imread(img_path)
                    ax.imshow(img)
                    h, w = img.shape[:2]
                    ax.set_xlim(0, w); ax.set_ylim(h, 0)
                    found = True
                except Exception:
                    pass

    if not found:
        ax.text(0.5, 0.5, f"Diagram Not Found\nID: {pid}", color='red', ha='center', va='center')
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)
    ax.set_title(f"Visualizing: {topic}")
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
