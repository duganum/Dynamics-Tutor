import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    Maps HW 11 specific IDs (K_2.6_x) to correct filenames (71, 6, 16).
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
            ax.text(-1.4, 0.2, '$T_A$', color='blue'); ax.text(1.0, 1.3, '$T_B (45^\circ)$', color='green')
            ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.1_2":
            theta = np.radians(30)
            ax.plot([-2, 2], [2*np.tan(-theta), -2*np.tan(-theta)], 'k-', lw=2) 
            ax.add_patch(plt.Circle((0, 0.5), 0.5, color='gray', alpha=0.5)) 
            ax.annotate('', xy=(0.5*np.sin(theta), 0.5+0.5*np.cos(theta)), xytext=(0, 0.5), arrowprops=dict(arrowstyle='->', color='red')) 
            ax.set_xlim(-2, 2); ax.set_ylim(-1, 2)
            found = True
        elif pid == "S_1.1_3":
            ax.plot([0, 3], [0, 0], 'brown', lw=6) 
            ax.plot(0, 0, 'k^', markersize=10) 
            ax.annotate('', xy=(3, 2), xytext=(3, 0), arrowprops=dict(arrowstyle='-', ls='--')) 
            ax.set_xlim(-0.5, 4); ax.set_ylim(-1, 3)
            found = True
    elif pid.startswith("S_1.2"):
        if pid == "S_1.2_1":
            pts = np.array([[0,0], [2,2], [4,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o')
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-1, 3)
            found = True
        elif pid == "S_1.2_2":
            pts = np.array([[0,0], [1, 1.73], [2,0], [0,0]])
            ax.plot(pts[:,0], pts[:,1], 'k-o')
            ax.set_xlim(-0.5, 2.5); ax.set_ylim(-0.5, 2.5)
            found = True
        elif pid == "S_1.2_3":
            ax.plot([0,1,2,3], [0,1,1,0], 'k-o'); ax.plot([0,3], [0,0], 'k-o')
            ax.set_xlim(-0.5, 3.5); ax.set_ylim(-0.5, 2)
            found = True
    elif pid.startswith("S_1.3"):
        if pid == "S_1.3_1":
            pts = np.array([[0,0], [4,0], [4,2], [0,2], [0,0]])
            ax.fill(pts[:,0], pts[:,1], color='green', alpha=0.3)
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 2.5)
            found = True
        elif pid == "S_1.3_2":
            pts = np.array([[0,0], [2,0], [2,2], [0,2], [0,0]])
            ax.fill(pts[:,0], pts[:,1], color='green', alpha=0.3)
            ax.set_xlim(-0.5, 2.5); ax.set_ylim(-0.5, 2.5)
            found = True
        elif pid == "S_1.3_3":
            pts = np.array([[0,0], [4,0], [4,1], [1,1], [1,4], [0,4], [0,0]])
            ax.fill(pts[:,0], pts[:,1], color='orange', alpha=0.3)
            ax.set_xlim(-1, 5); ax.set_ylim(-1, 5)
            found = True
    elif pid.startswith("S_1.4"):
        if pid == "S_1.4_1":
            ax.plot([-3, 3], [0, 0], 'k-', lw=4)
            ax.plot(0, -0.2, 'k^', markersize=15)
            ax.set_xlim(-4, 4); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.4_2":
            ax.plot([0, 3], [0, 0], color='gray', lw=8)
            ax.annotate('', xy=(3, -1), xytext=(3, 0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.set_xlim(-0.5, 4); ax.set_ylim(-1.5, 1.5)
            found = True
        elif pid == "S_1.4_3":
            ax.plot([0, 6], [0, 0], color='brown', lw=10)
            ax.set_xlim(-1, 7); ax.set_ylim(-2, 3)
            found = True

    # --- 2. HW Directory Image Loader ---
    if not found:
        category = str(prob.get("category", "")).lower()
        hw_title = prob.get("hw_title")
        hw_subtitle = prob.get("hw_subtitle")
        image_filename = f"{pid}.png"
        folder_name = None

        # ROUTING LOGIC: Specific HW Folders
        # Fixed mapping for Rigid Body Kinematics (Rotation)
        if "rotation" in category or "rigid" in category or pid.startswith("K_2.6"):
            folder_name = "HW 11 (kinematics of rigid body-rotation)"
            if "_1" in pid: image_filename = "71.png"
            elif "_2" in pid: image_filename = "6.png"
            elif "_3" in pid: image_filename = "16.png"
        elif "impact" in category or pid in ["239", "249", "252"]:
            folder_name = "HW 10 (Impact)"
        elif "momentum" in category or "impulse" in category or pid in ["176", "198", "209"]:
            folder_name = "HW 9 (Impuls and momentum)"
        elif "work" in category or "energy" in category or pid in ["158", "161", "162"]:
            folder_name = "HW 8 (work and energy)"
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
                except: pass

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
    """Visualizes derivation components."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.axhline(0, color='black', lw=1.5); ax.axvline(0, color='black', lw=1.5)
    ax.grid(True, linestyle=':', alpha=0.6); ax.set_aspect('equal')
    
    if topic == "Relative Motion" and params:
        vA, vB = params.get('vA', [15, 5]), params.get('vB', [10, -5])
        ax.quiver(0, 0, vA[0], vA[1], color='blue', angles='xy', scale_units='xy', scale=1, label='vA')
        ax.quiver(0, 0, vB[0], vB[1], color='red', angles='xy', scale_units='xy', scale=1, label='vB')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
