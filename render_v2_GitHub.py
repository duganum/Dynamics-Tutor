import matplotlib.pyplot as plt
import numpy as np
import os
import io
import re

def render_problem_diagram(prob):
    """
    Generates UNIQUE procedural FBDs for Statics S_1 series 
    and loads external images for Dynamics.
    """
    if isinstance(prob, dict):
        pid = str(prob.get('id', '')).strip()
    else:
        pid = str(prob).strip()
        prob = {}

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_aspect('equal')
    found = False

    # --- 1. UNIQUE Procedural Statics Diagrams ---
    if pid.startswith("S_1"):
        # Section S_1.1: Particle Equilibrium / Force Vectors
        if "S_1.1" in pid:
            ax.plot(0, 0, 'ko', markersize=10) 
            if pid == "S_1.1_1":
                ax.annotate('', xy=(-1.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
                ax.annotate('', xy=(1.2, 1.2), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
                ax.annotate('', xy=(0, -1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            elif pid == "S_1.1_2":
                ax.annotate('', xy=(1, 1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
                ax.annotate('', xy=(-1, 1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
                ax.annotate('', xy=(0, -1.8), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            elif pid == "S_1.1_3":
                ax.annotate('', xy=(1.8, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
                ax.annotate('', xy=(-0.8, 1.4), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
                ax.annotate('', xy=(-0.8, -1.4), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
            found = True
        
        # Section S_1.2: Simple Trusses
        elif "S_1.2" in pid:
            if pid == "S_1.2_1":
                pts = np.array([[0,0], [2,1], [4,0], [2,0], [0,0]])
                ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2); ax.plot([2,2], [0,1], 'k-', lw=2)
            elif pid == "S_1.2_2":
                pts = np.array([[0,0], [1,1.5], [2,1.5], [3,0], [0,0]])
                ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2); ax.plot([1,2], [1.5,0], 'k-', lw=2)
            elif pid == "S_1.2_3":
                pts = np.array([[0,0], [0,2], [2,0], [0,0]])
                ax.plot(pts[:,0], pts[:,1], 'k-o', lw=2); ax.plot([0,1], [1,0], 'k-', lw=2)
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 2.5)
            found = True

        # Section S_1.3: Geometric Properties (FIXED: Draws Shapes, not Beams)
        elif "S_1.3" in pid:
            if pid == "S_1.3_1": # Rectangle Centroid
                rect = plt.Rectangle((0, 0), 4, 6, color='gray', alpha=0.3)
                ax.add_patch(rect); ax.set_xlim(-1, 5); ax.set_ylim(-1, 7)
                ax.plot(2, 3, 'rx', markersize=10)
            elif pid == "S_1.3_2": # Triangle Centroid
                tri = plt.Polygon([[0,0], [4,0], [0,6]], color='gray', alpha=0.3)
                ax.add_patch(tri); ax.set_xlim(-1, 5); ax.set_ylim(-1, 7)
                ax.plot(1.33, 2, 'rx', markersize=10)
            elif pid == "S_1.3_3": # Semicircle Centroid
                theta = np.linspace(0, np.pi, 100)
                ax.fill(3*np.cos(theta), 3*np.sin(theta), color='gray', alpha=0.3)
                ax.set_xlim(-4, 4); ax.set_ylim(-1, 4)
                ax.plot(0, 1.27, 'rx', markersize=10)
            found = True

        # Section S_1.4: Equilibrium (FIXED: Draws Log and Cantilever)
        elif "S_1.4" in pid:
            if pid == "S_1.4_1": # Person A/B carrying log
                ax.plot([0, 6], [0.5, 0.5], 'brown', lw=10) 
                ax.annotate('$F_A$', xy=(0, 0.5), xytext=(0, 1.5), arrowprops=dict(arrowstyle='<-', color='blue'))
                ax.annotate('$F_B$', xy=(4, 0.5), xytext=(4, 1.5), arrowprops=dict(arrowstyle='<-', color='green'))
                ax.annotate('W', xy=(3, 0.5), xytext=(3, -0.5), arrowprops=dict(arrowstyle='->', color='red'))
                ax.set_xlim(-1, 7); ax.set_ylim(-1, 2.5)
            elif pid == "S_1.4_2": # Cantilever Beam Moment
                ax.plot([0, 3], [0, 0], 'k-', lw=6) 
                ax.plot([0, 0], [-0.5, 0.5], 'k-', lw=4) 
                ax.annotate('100 N', xy=(3, 0), xytext=(3, -1), arrowprops=dict(arrowstyle='->', color='red'))
                ax.set_xlim(-0.5, 4); ax.set_ylim(-1.5, 1.5)
            elif pid == "S_1.4_3": # Friction block on incline
                ax.plot([0, 4], [0, 2], 'k-', lw=2)
                rect = plt.Rectangle((1, 0.5), 1.5, 0.8, angle=26, color='gray', alpha=0.4)
                ax.add_patch(rect)
                ax.set_xlim(-0.5, 5); ax.set_ylim(-0.5, 3)
            found = True

    # --- 2. Dynamics Image Loader ---
    if not found:
        category = str(prob.get("category", "")).lower()
        if "_" in pid: image_number = pid.split("_")[-1]
        elif "-" in pid: image_number = pid.split("-")[-1]
        else:
            match = re.search(r'(\d+)$', pid)
            image_number = match.group(1) if match else pid
            
        image_filename = f"{image_number}.png"
        target_hw = None
        
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
        if target_hw and os.path.exists('images'):
            all_folders = [f for f in os.listdir('images') if os.path.isdir(os.path.join('images', f))]
            for folder in all_folders:
                if folder.startswith(target_hw):
                    paths_to_try.append(os.path.join('images', folder, 'images', image_filename))
                    paths_to_try.append(os.path.join('images', folder, image_filename))

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
        ax.text(0.5, 0.5, f"Not Found: {image_filename}\nID: {pid}", color='red', ha='center', va='center', fontsize=7)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    if params is None: params = {}
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    topic_clean = topic.lower().strip()

    if "projectile" in topic_clean:
        v0 = params.get("v0", 50.0); angle = np.radians(params.get("angle", 0)); g = params.get("g", 10.0)
        t_total = (2 * v0 * np.sin(angle)) / g if g > 0 and angle > 0 else 2.0
        t = np.linspace(0, t_total, 100); x = v0 * np.cos(angle) * t; y = v0 * np.sin(angle) * t - 0.5 * g * t**2
        ax.plot(x, y, 'b-', lw=2)
        ax.set_xlim(min(0, np.min(x)), max(10, np.max(x))*1.1 if len(x)>1 else 10)
        ax.set_ylim(min(-5, np.min(y)), max(10, np.max(y))*1.2 if len(y)>1 else 10)
    elif "normal" in topic_clean or "tangent" in topic_clean:
        v, rho, at = params.get("v", 50.0), params.get("rho", 255.0), params.get("at", 0.0)
        an = (v**2) / rho if rho > 0 else 0
        theta_path = np.linspace(0, np.pi/2, 100); ax.plot(rho * np.cos(theta_path), rho * np.sin(theta_path), 'k--', alpha=0.3)
        px, py = rho * np.cos(np.pi/4), rho * np.sin(np.pi/4); ax.plot(px, py, 'bo', markersize=10)
        ax.quiver(px, py, -an*np.cos(np.pi/4), -an*np.sin(np.pi/4), color='red', angles='xy', scale_units='xy', scale=1, label="$a_n$")
        ax.quiver(px, py, -at*np.sin(np.pi/4), at*np.cos(np.pi/4), color='green', angles='xy', scale_units='xy', scale=1, label="$a_t$")
    elif "polar" in topic_clean:
        r_val, rdot, tdot = params.get("r", 5.0), params.get("rdot", 0.0), params.get("theta_dot", 0.0)
        theta_val = np.radians(45); px, py = r_val * np.cos(theta_val), r_val * np.sin(theta_val)
        ax.quiver(px, py, rdot*np.cos(theta_val), rdot*np.sin(theta_val), color='red', angles='xy', scale_units='xy', scale=1, label="$\dot{r}e_r$")
        v_theta = r_val * tdot; ax.quiver(px, py, -v_theta*np.sin(theta_val), v_theta*np.cos(theta_val), color='green', angles='xy', scale_units='xy', scale=1, label="$r\dot{\\theta}e_\\theta$")
        ax.plot([0, px], [0, py], 'k--', alpha=0.5); ax.plot(px, py, 'ro', markersize=10); ax.set_xlim(-15, 15); ax.set_ylim(-15, 15)

    ax.axhline(0, color='black', lw=1); ax.axvline(0, color='black', lw=1); ax.grid(True, linestyle=':', alpha=0.6)
    buf = io.BytesIO(); fig.savefig(buf, format='png', bbox_inches='tight'); plt.close(fig); buf.seek(0)
    return buf
