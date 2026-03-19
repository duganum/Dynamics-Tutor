import matplotlib.pyplot as plt
import numpy as np
import os
import io
import re

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    FIXED: Added handlers for Statics S_1.x.x and improved Dynamics folder discovery.
    """
    if isinstance(prob, dict):
        pid = str(prob.get('id', '')).strip()
    else:
        pid = str(prob).strip()
        prob = {}

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_aspect('equal')
    found = False

    # --- 1. Procedural Statics Diagrams (Handles S_1.1.x, S_1.2.x, etc.) ---
    if pid.startswith("S_1"):
        # Procedural drawing for specific Statics problems
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
        else:
            # General placeholder for other S_1 series to prevent blank screens
            ax.plot([-1, 1], [0, 0], 'k-', lw=3)  # Beam
            ax.plot(0, 0, 'r^', markersize=10)    # Support
            ax.set_xlim(-2, 2); ax.set_ylim(-1, 2)
            ax.set_title(f"Statics Schematic: {pid}", fontsize=8)
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

        # DYNAMIC FOLDER DISCOVERY (Handles spaces/parentheses in GitHub folder names)
        if target_hw and os.path.exists('images'):
            all_folders = [f for f in os.listdir('images') if os.path.isdir(os.path.join('images', f))]
            for folder in all_folders:
                if folder.startswith(target_hw):
                    # Check the /images/folder/images/ nested structure and the single nested structure
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
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    """
    Generates dynamic physics plots for the Interactive Lectures.
    Calculates trajectories and vectors based on user-provided slider params.
    FIXED: Using 'angles=xy, scale_units=xy, scale=1' so arrows grow with values.
    """
    if params is None: params = {}
    
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    topic_clean = topic.lower().strip()

    # --- 1. Projectile Motion ---
    if "projectile" in topic_clean:
        v0 = params.get("v0", 50.0)
        angle = np.radians(params.get("angle", 0))
        g = params.get("g", 10.0)
        
        t_total = (2 * v0 * np.sin(angle)) / g if g > 0 and angle > 0 else 2.0
        t = np.linspace(0, t_total, 100)
        x = v0 * np.cos(angle) * t
        y = v0 * np.sin(angle) * t - 0.5 * g * t**2
        
        ax.plot(x, y, 'b-', lw=2)
        ax.set_title("Projectile Trajectory")
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        ax.set_xlim(min(0, np.min(x)), max(10, np.max(x))*1.1 if len(x)>1 else 10)
        ax.set_ylim(min(-5, np.min(y)), max(10, np.max(y))*1.2 if len(y)>1 else 10)

    # --- 2. Normal & Tangent ---
    elif "normal" in topic_clean or "tangent" in topic_clean:
        v, rho, at = params.get("v", 50.0), params.get("rho", 255.0), params.get("at", 0.0)
        an = (v**2) / rho if rho > 0 else 0
        
        theta_path = np.linspace(0, np.pi/2, 100)
        ax.plot(rho * np.cos(theta_path), rho * np.sin(theta_path), 'k--', alpha=0.3)
        
        px, py = rho * np.cos(np.pi/4), rho * np.sin(np.pi/4)
        ax.plot(px, py, 'bo', markersize=10)
        
        # a_n points toward center (-cos, -sin)
        ax.quiver(px, py, -an*np.cos(np.pi/4), -an*np.sin(np.pi/4), 
                  color='red', angles='xy', scale_units='xy', scale=1, label="$a_n$")
        
        # a_t points along tangent (-sin, cos)
        ax.quiver(px, py, -at*np.sin(np.pi/4), at*np.cos(np.pi/4), 
                  color='green', angles='xy', scale_units='xy', scale=1, label="$a_t$")
        
        ax.set_title(f"Acceleration Vectors ($a_n = {an:.1f}$)")
        ax.set_xlim(0, rho*1.2); ax.set_ylim(0, rho*1.2)
        ax.legend()

    # --- 3. Polar Coordinates ---
    elif "polar" in topic_clean:
        r_val = params.get("r", 5.0)
        rdot = params.get("rdot", 0.0)
        tdot = params.get("theta_dot", 0.0)
        
        theta_val = np.radians(45)
        px, py = r_val * np.cos(theta_val), r_val * np.sin(theta_val)
        
        # Radial velocity vector
        ax.quiver(px, py, rdot*np.cos(theta_val), rdot*np.sin(theta_val), 
                  color='red', angles='xy', scale_units='xy', scale=1, label="$\dot{r}e_r$")
        
        # Transverse velocity vector (r * theta_dot)
        v_theta = r_val * tdot
        ax.quiver(px, py, -v_theta*np.sin(theta_val), v_theta*np.cos(theta_val), 
                  color='green', angles='xy', scale_units='xy', scale=1, label="$r\dot{\\theta}e_\\theta$")
        
        ax.plot([0, px], [0, py], 'k--', alpha=0.5)
        ax.plot(px, py, 'ro', markersize=10)
        ax.set_xlim(-15, 15); ax.set_ylim(-15, 15)
        ax.set_title("Velocity Components (Polar)")
        ax.legend()

    ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1)
    ax.grid(True, linestyle=':', alpha=0.6)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
