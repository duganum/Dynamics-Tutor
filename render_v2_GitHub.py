import matplotlib.pyplot as plt
import numpy as np
import os
import io

def render_problem_diagram(prob):
    """
    Generates procedural FBDs for Statics or loads external images for Dynamics.
    Supports nested paths: images/[HW Folder]/images/[ID].png
    Handles specific spacing and naming in HW 7 and HW 8 directory naming.
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

    # --- 1. Procedural Statics Diagrams (FBD, Trusses, Geometric Props, Equilibrium) ---
    
    # 1.1: Free Body Diagrams
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

    # 1.2: Trusses
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

    # 1.3: Geometric Properties (Centroids/Area)
    elif pid.startswith("S_1.3"):
        if pid == "S_1.3_1": # Rectangular Area
            rect = plt.Rectangle((0, 0), 4, 2, color='blue', alpha=0.3)
            ax.add_patch(rect)
            ax.plot(2, 1, 'rx', markersize=10, label='Centroid')
            ax.set_xlim(-1, 5); ax.set_ylim(-1, 3)
            found = True
        elif pid == "S_1.3_2": # Triangular Area
            tri = plt.Polygon([[0,0], [3,0], [0,3]], color='green', alpha=0.3)
            ax.add_patch(tri)
            ax.plot(1, 1, 'rx', markersize=10)
            ax.set_xlim(-1, 4); ax.set_ylim(-1, 4)
            found = True
        elif pid == "S_1.3_3": # Composite Shape (L-shape)
            pts = np.array([[0,0], [4,0], [4,1], [1,1], [1,4], [0,4], [0,0]])
            ax.fill(pts[:,0], pts[:,1], color='orange', alpha=0.3)
            ax.set_xlim(-1, 5); ax.set_ylim(-1, 5)
            found = True

    # 1.4: Equilibrium (Forces and Moments)
    elif pid.startswith("S_1.4"):
        if pid == "S_1.4_1": # Seesaw/Lever
            ax.plot([-3, 3], [0, 0], 'k-', lw=4)
            ax.plot(0, -0.5, 'k^', markersize=15) # Fulcrum
            ax.annotate('100 N', xy=(-2.5, -1), xytext=(-2.5, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.annotate('F', xy=(2.5, 0), xytext=(2.5, 1), arrowprops=dict(arrowstyle='->', color='blue'))
            ax.set_xlim(-4, 4); ax.set_ylim(-2, 2)
            found = True
        elif pid == "S_1.4_2": # Moment on a bolt/wrench
            ax.plot([0, 2], [0, 0], 'gray', lw=8)
            ax.plot(0, 0, 'ko', markersize=12)
            ax.annotate('', xy=(2, 1), xytext=(2, 0), arrowprops=dict(arrowstyle='->', color='red'))
            ax.text(2.1, 0.5, 'Force F')
            ax.set_xlim(-0.5, 3); ax.set_ylim(-1, 2)
            found = True

    # --- 2. HW Directory Image Loader (Nested Path Logic) ---
    if not found:
        hw_title = prob.get("hw_title")
        hw_subtitle = prob.get("hw_subtitle")
        category = str(prob.get("category", "")).lower()
        
        folder_name = None
        
        if "work" in category or "energy" in category or pid in ["141", "158", "161", "162"]:
            folder_name = "HW 8 (work and energy)"
            image_filename = f"{pid}.png"
        elif hw_title and hw_subtitle:
            if hw_title == "HW 7":
                folder_name = f"HW 7  ({hw_subtitle})" 
            else:
                folder_name = f"{hw_title} ({hw_subtitle})"
            image_filename = f"{pid.split('_')[-1]}.png"

        if folder_name:
            img_path = os.path.join('images', folder_name, 'images', image_filename)
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
            clean_name = pid.replace("_", "").replace(".", "").lower()
            img_path_alt = os.path.join('images', f'{clean_name}.png')
            if os.path.exists(img_path_alt):
                try:
                    img = plt.imread(img_path_alt)
                    ax.imshow(img)
                    h, w = img.shape[:2]
                    ax.set_xlim(0, w); ax.set_ylim(h, 0)
                    found = True
                except Exception:
                    pass

    # --- 3. Error Handling ---
    if not found:
        ax.text(0.5, 0.5, f"Diagram Not Found\nID: {pid}", color='red', ha='center', va='center')
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.axis('off')
    
    try:
        plt.tight_layout()
    except Exception:
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def render_lecture_visual(topic, params=None):
    """Visualizes derivation components with a strictly centered origin."""
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    if params is None: params = {}
    
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
        
        limit = max(np.abs(vA + vB)) + 5
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
        ax.set_title(r"Projectile Trajectory Analysis")

    elif topic == "Normal & Tangent":
        v, rho = params.get('v', 20), params.get('rho', 50)
        theta_arc = np.linspace(np.pi/4, 3*np.pi/4, 100)
        ax.plot(rho * np.cos(theta_arc), rho * np.sin(theta_arc) - rho, 'k--', alpha=0.5)
        ax.plot(0, 0, 'ko', markersize=8)
        ax.quiver(0, 0, v, 0, color='blue', angles='xy', scale_units='xy', scale=1, label=r'$v$ (Tangent)')
        ax.quiver(0, 0, 0, -(v**2/rho), color='red', angles='xy', scale_units='xy', scale=1, label=r'$a_n = v^2/\rho$')
        ax.set_xlim(-rho, rho); ax.set_ylim(-rho, rho/2)
        ax.set_title(r"Normal and Tangential Acceleration")
        ax.legend()

    elif topic == "Polar Coordinates":
        r, theta_deg = params.get('r', 20), params.get('theta', 45)
        theta = np.radians(theta_deg)
        x, y = r * np.cos(theta), r * np.sin(theta)
        ax.plot([0, x], [0, y], 'k-o', lw=2)
        ax.quiver(x, y, np.cos(theta)*5, np.sin(theta)*5, color='blue', angles='xy', scale_units='xy', scale=1, label=r'$e_r$')
        ax.quiver(x, y, -np.sin(theta)*5, np.cos(theta)*5, color='red', angles='xy', scale_units='xy', scale=1, label=r'$e_\theta$')
        ax.set_xlim(-r-10, r+10); ax.set_ylim(-r-10, r+10)
        ax.set_title(r"Polar Coordinates: Radial & Transverse")
        ax.legend()

    try:
        plt.tight_layout()
    except Exception:
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
