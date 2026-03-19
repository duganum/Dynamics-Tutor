import matplotlib.pyplot as plt
import numpy as np
import os
import io
import re

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    FIXED: Restored correct HW 11 filename mapping (6, 16, 71).
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
        
        # Determine Numeric Filename
        if "_" in pid: image_number = pid.split("_")[-1]
        elif "-" in pid: image_number = pid.split("-")[-1]
        else:
            match = re.search(r'(\d+)$', pid)
            image_number = match.group(1) if match else pid
            
        image_filename = f"{image_number}.png"
        target_hw = None
        
        # Mapping Logic & HW 11 Overrides
        if "rotation" in category or "rigid" in category or "hw11" in pid.lower().replace(" ", "") or pid.startswith("K_2.6"):
            target_hw = "HW 11"
            if pid.endswith("_1"): image_filename = "71.png"
            elif pid.endswith("_2"): image_filename = "6.png"
            elif pid.endswith("_3"): image_filename = "16.png"
        elif "curvilinear" in category or "hw7" in pid.lower().replace(" ", ""): target_hw = "HW 7"
        elif "rectilinear" in category or "hw6" in pid.lower().replace(" ", ""): target_hw = "HW 6"
        elif "impact" in category or "hw10" in pid.lower().replace(" ", ""): target_hw = "HW 10"
        elif "momentum" in category or "impulse" in category or "hw9" in pid.lower().replace(" ", ""): target_hw = "HW 9"
        elif "work" in category or "energy" in category or "hw8" in pid.lower().replace(" ", ""): target_hw = "HW 8"

        paths_to_try = []

        # DYNAMIC FOLDER DISCOVERY
        if target_hw and os.path.exists('images'):
            all_folders = [f for f in os.listdir('images') if os.path.isdir(os.path.join('images', f))]
            for folder in all_folders:
                if folder.startswith(target_hw):
                    paths_to_try.append(os.path.join('images', folder, 'images', image_filename))
                    paths_to_try.append(os.path.join('images', folder, image_filename))

        # Absolute Fallbacks
        clean_pid = pid.replace("_", "").replace(".", "").replace("-", "").replace(" ", "").lower()
        paths_to_try.append(os.path.join('images', f"{clean_pid}.png"))
        paths_to_try.append(os.path.join('images', image_filename))

        # Execute Search
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
        ax.text(0.5, 0.5, f"Not Found: {image_filename}\nID: {pid}", color='red', ha='center', va='center', fontsize=7)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    """
    Generates dynamic physics plots for the Interactive Lectures.
    Calculates trajectories and vectors based on user-provided slider params.
    """
    if params is None: params = {}
    
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    topic_clean = topic.lower().strip()

    # --- 1. Projectile Motion ---
    if "projectile" in topic_clean:
        v0 = params.get("v0", 20.0)
        angle = np.radians(params.get("angle", 45))
        g = params.get("g", 9.81)
        t_total = (2 * v0 * np.sin(angle)) / g if g > 0 else 0
        t = np.linspace(0, t_total, 100) if t_total > 0 else [0]
        x = v0 * np.cos(angle) * t
        y = v0 * np.sin(angle) * t - 0.5 * g * t**2
        ax.plot(x, y, 'b-', lw=2)
        ax.set_title("Projectile Trajectory")
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        if len(x) > 1:
            ax.set_xlim(0, max(x)*1.1); ax.set_ylim(0, max(y)*1.2)

    # --- 2. Polar Coordinates ---
    elif "polar" in topic_clean:
        r_val = params.get("r", 5.0)
        theta_val = np.radians(30)
        px, py = r_val * np.cos(theta_val), r_val * np.sin(theta_val)
        ax.quiver(px, py, np.cos(theta_val), np.sin(theta_val), color='red', scale=5, label="$e_r$")
        ax.quiver(px, py, -np.sin(theta_val), np.cos(theta_val), color='green', scale=5, label="$e_\\theta$")
        ax.plot([0, px], [0, py], 'k--', alpha=0.5)
        ax.plot(px, py, 'ro', markersize=10)
        ax.set_xlim(-2, 12); ax.set_ylim(-2, 12)
        ax.set_title("Polar Vectors")
        ax.legend()

    # --- 3. Normal & Tangent ---
    elif "normal" in topic_clean or "tangent" in topic_clean:
        v, rho, at = params.get("v", 50.0), params.get("rho", 100.0), params.get("at", 2.0)
        an = (v**2) / rho if rho > 0 else 0
        arc = np.linspace(0, np.pi/2, 100)
        ax.plot(rho * np.cos(arc), rho * np.sin(arc), 'k--', alpha=0.3)
        px, py = rho * np.cos(np.pi/4), rho * np.sin(np.pi/4)
        ax.quiver(px, py, -np.cos(np.pi/4), -np.sin(np.pi/4), color='red', scale=an*0.5, label="$a_n$")
        ax.quiver(px, py, -np.sin(np.pi/4), np.cos(np.pi/4), color='green', scale=at*5, label="$a_t$")
        ax.plot(px, py, 'bo', markersize=10)
        ax.set_title("Normal/Tangential Acceleration")
        ax.legend()

    ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)
    ax.grid(True, linestyle=':', alpha=0.6)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
