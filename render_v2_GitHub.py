import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob):
    """Generates precise FBDs or loads images from the HW directory structure."""
    # Ensure we handle both the full object and just the ID for backward compatibility
    if isinstance(prob, dict):
        pid = str(prob.get('id', '')).strip()
    else:
        pid = str(prob).strip()
        prob = {} # Create empty dict to avoid errors below

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_aspect('equal')
    found = False

    # --- Procedural Diagrams (Statics sections) ---
    if pid.startswith("S_1.1"):
        if pid == "S_1.1_1": # 50kg mass cables
            ax.plot(0, 0, 'ko', markersize=8)
            ax.annotate('', xy=(-1.5, 0), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='blue'))
            ax.annotate('', xy=(1.2, 1.2), xytext=(0, 0), arrowprops=dict(arrowstyle='<-', color='green'))
            ax.annotate('', xy=(0, -1.5), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.text(-1.4, 0.2, '$T_A$', color='blue'); ax.text(1.0, 1.3, '$T_B (45^\circ)$', color='green')
            ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.1_2": # Cylinder on Incline
            theta = np.radians(30)
            ax.plot([-2, 2], [2*np.tan(-theta), -2*np.tan(-theta)], 'k-', lw=2) 
            ax.add_patch(plt.Circle((0, 0.5), 0.5, color='gray', alpha=0.5)) 
            ax.annotate('', xy=(0.5*np.sin(theta), 0.5+0.5*np.cos(theta)), xytext=(0, 0.5), 
                        arrowprops=dict(arrowstyle='->', color='red')) 
            ax.set_xlim(-2, 2); ax.set_ylim(-1, 2)
            found = True
        elif pid == "S_1.1_3": # Beam with Pin and Cable
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

    # --- HW Directory Image Loader (NEW) ---
    if not found:
        hw_title = prob.get("hw_title")
        hw_subtitle = prob.get("hw_subtitle")
        
        if hw_title and hw_subtitle:
            # Path: images/HW 6 (kinetics of particles-rectilinear motion)/1.png
            folder_name = f"{hw_title} ({hw_subtitle})"
            # Extract number from ID (e.g., '1' from 'HW6_1')
            image_num = pid.split('_')[-1]
            img_path = os.path.join('images', folder_name, f"{image_num}.png")
        else:
            # Original Kinematics fallback loader
            clean_name = pid.replace("_", "").replace(".", "").lower()
            img_path = f'images/{clean_name}.png'

        try:
            if os.path.exists(img_path):
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
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    """Visualizes derivation components with a strictly centered origin."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    if params is None: params = {}
    
    # Grid and Origin Settings
    ax.axhline(0, color='black', lw=1.5, zorder=2)
    ax.axvline(0, color='black', lw=1.5, zorder=2)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')
    
    if topic == "Relative Motion":
        vA = params.get('vA', [15, 5])
        vB = params.get('vB', [10, -5])
        v_rel_x, v_rel_y = vA[0] - vB[0], vA[1] - vB[1]

        ax.quiver(0, 0, vA[0], vA[1], color='blue', angles='xy', scale_units='xy', scale=1, label=r'$\vec{v}_A$')
        ax.quiver(0, 0, vB[0], vB[1], color='red', angles='xy', scale_units='xy', scale=1, label=r'$\vec{v}_B$')
        ax.quiver(vB[0], vB[1], v_rel_x, v_rel_y, color='green', angles='xy', scale_units='xy', scale=1, label=r'$\vec{v}_{A/B}$')
        
        max_reach = max(np.abs([vA[0], vA[1], vB[0], vB[1], vA[0], vA[1]]))
        limit = max_reach + 5
        ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit)
        ax.set_title(r"Relative Motion: $\vec{v}_A = \vec{v}_B + \vec{v}_{A/B}$")
        ax.legend(loc='upper right')

    elif topic == "Projectile Motion":
        v0, angle = params.get('v0', 30), params.get('angle', 45)
        g, theta = 9.81, np.radians(angle)
        t_flight = 2 * v0 * np.sin(theta) / g
        t = np.linspace(0, t_flight, 100)
        x = v0 * np.cos(theta) * t
        y = v0 * np.sin(theta) * t - 0.5 * g * t**2
        ax.plot(x, y, 'g-', lw=2)
        ax.set_xlim(-5, max(x)+5); ax.set_ylim(-5, max(y)+5)
        ax.set_title(r"Projectile Trajectory")

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf