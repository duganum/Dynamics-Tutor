import matplotlib.pyplot as plt
import numpy as np
import os
import io
import re  # FIXED: Added missing import

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    FIXED: Added 're' import and improved HW 7/11 numeric matching.
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
    if pid.startswith("S_1.1"):
        if pid == "S_1.1_1":
            ax.plot(0, 0, 'ko', markersize=8)
            ax.annotate('', xy=(-1.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
            ax.annotate('', xy=(1.2, 1.2), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
            ax.annotate('', xy=(0, -1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.1_2":
            theta = np.radians(30)
            ax.plot([-2, 2], [2*np.tan(-theta), -2*np.tan(-theta)], 'k-', lw=2) 
            ax.add_patch(plt.Circle((0, 0.5), 0.5, color='gray', alpha=0.5)) 
            ax.set_xlim(-2, 2); ax.set_ylim(-1, 2)
            found = True
        elif pid == "S_1.1_3":
            ax.plot([0, 3], [0, 0], 'brown', lw=6); ax.plot(0, 0, 'k^', markersize=10) 
            ax.set_xlim(-0.5, 4); ax.set_ylim(-1, 3)
            found = True

    elif pid.startswith("S_1.2"):
        if pid == "S_1.2_1":
            pts = np.array([[0,0], [2,1], [4,0], [2,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2); ax.plot([2,2], [0,1], 'k-', lw=2)
            ax.annotate('', xy=(2, -1), xytext=(2, 0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-1.5, 2)
            found = True
        elif pid == "S_1.2_2":
            pts = np.array([[0,0], [1, 1.73], [2,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2)
            ax.annotate('', xy=(1, 0.73), xytext=(1, 1.73), arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.set_xlim(-0.5, 2.5); ax.set_ylim(-0.5, 2.5)
            found = True

    elif pid.startswith("S_1.4"):
        if pid == "S_1.4_1":
            ax.plot([0, 3], [0, 0], color='gray', lw=8)
            ax.plot([0, 0], [-1, 1], color='black', lw=4)
            ax.annotate('', xy=(3, -1), xytext=(3, 0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.set_xlim(-0.5, 4); ax.set_ylim(-1.5, 1.5)
            found = True
        elif pid == "S_1.4_2":
            ax.plot([0, 6], [0, 0], color='brown', lw=10)
            ax.plot(0, -0.2, 'k^', markersize=15)
            ax.plot(4, -0.2, 'k^', markersize=15)
            ax.annotate('', xy=(3, -1.5), xytext=(3, 0), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            ax.set_xlim(-1, 7); ax.set_ylim(-2, 1)
            found = True

    # --- 2. Dynamics Image Loader (HW Folders & Root) ---
    if not found:
        category = str(prob.get("category", "")).lower()
        clean_pid = pid.replace("_", "").replace(".", "").lower()
        image_filename = f"{clean_pid}.png"
        folder_name = None

        if "rotation" in category or "rigid" in category or pid.startswith("K_2.6"):
            folder_name = "HW 11 (kinematics of rigid body-rotation)"
            if pid.endswith("_1"): image_filename = "71.png"
            elif pid.endswith("_2"): image_filename = "6.png"
            elif pid.endswith("_3"): image_filename = "16.png"
        elif "curvilinear" in category or "hw7" in clean_pid:
            folder_name = "HW 7 (kinetics of particles-curvilinear motion)"
            match = re.search(r'(\d+)$', pid)
            if match: image_filename = f"{match.group(1)}.png"
        elif "rectilinear" in category or "hw6" in clean_pid:
            folder_name = "HW 6 (kinetics of particles-rectilinear motion)"
            match = re.search(r'(\d+)$', pid)
            if match: image_filename = f"{match.group(1)}.png"
        elif "impact" in category:
            folder_name = "HW 10 (Impact)"
        elif "momentum" in category or "impulse" in category:
            folder_name = "HW 9 (Impuls and momentum)"
        elif "work" in category or "energy" in category:
            folder_name = "HW 8 (work and energy)"

        paths_to_try = []
        if folder_name:
            paths_to_try.append(os.path.join('images', folder_name, 'images', image_filename))
            paths_to_try.append(os.path.join('images', folder_name, image_filename))
        
        # Universal fallback for root images (k221.png etc.)
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
        ax.text(0.5, 0.5, f"Diagram Not Found\nID: {pid}", color='red', ha='center', va='center', fontsize=8)
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
