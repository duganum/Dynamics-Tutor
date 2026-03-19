import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    FIXED: Full procedural logic for Statics Truss (S_1.2_1, S_1.2_2, S_1.2_3).
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
    # Section: Free Body Diagrams
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

    # Section: Truss Problems (S_1.2)
    elif pid.startswith("S_1.2"):
        if pid == "S_1.2_1":  # Simple Bridge Truss
            pts = np.array([[0,0], [2,1], [4,0], [2,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2)
            ax.plot([2,2], [0,1], 'k-', lw=2) # Central vertical
            ax.annotate('', xy=(2, -1), xytext=(2, 0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.text(2.1, -0.8, '10 kN', color='red')
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-1.5, 2)
            found = True
        elif pid == "S_1.2_2":  # Triangle Truss (60 deg)
            pts = np.array([[0,0], [1, 1.73], [2,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2)
            ax.annotate('', xy=(1, 0.73), xytext=(1, 1.73), arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.text(1.1, 1.0, '5 kN', color='red')
            ax.set_xlim(-0.5, 2.5); ax.set_ylim(-0.5, 2.5)
            found = True
        elif pid == "S_1.2_3":  # Pratt Truss
            ax.plot([0,1,2,3], [0,1,1,0], 'k-o', lw=2) # Top
            ax.plot([0,1,2,3], [0,0,0,0], 'k-o', lw=2) # Bottom
            ax.plot([1,1], [0,1], 'k-'); ax.plot([2,2], [0,1], 'k-') # Verticals
            ax.plot([0,1], [0,1], 'k-'); ax.plot([3,2], [0,1], 'k-') # Diagonals
            ax.set_xlim(-0.5, 3.5); ax.set_ylim(-0.5, 2)
            found = True

    # Section: Geometric Properties (S_1.3)
    elif pid.startswith("S_1.3"):
        if pid == "S_1.3_1":
            pts = np.array([[0,0], [4,0], [4,2], [0,2], [0,0]])
            ax.fill(pts[:,0], pts[:,1], color='green', alpha=0.3)
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 2.5)
            found = True
        # ... (Add other S_1.3 shapes if needed)

    # Section: Equilibrium (S_1.4)
    elif pid.startswith("S_1.4"):
        if pid == "S_1.4_1":
            ax.plot([-3, 3], [0, 0], 'k-', lw=4); ax.plot(0, -0.2, 'k^', markersize=15)
            ax.set_xlim(-4, 4); ax.set_ylim(-2, 2)
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

        paths_to_try = []
        if folder_name:
            paths_to_try.append(os.path.join('images', folder_name, 'images', image_filename))
            paths_to_try.append(os.path.join('images', folder_name, image_filename))
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
