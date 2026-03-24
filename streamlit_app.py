import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="ENIGMA 3D — SN63", page_icon="🔑", layout="wide")

# Bunker CSS + Game Feel
st.markdown("""
<style>
    .stApp { background: #0a0503; color: #ffcc00; font-family: 'Courier New', monospace; }
    .header { text-align: center; padding: 20px; border-bottom: 4px solid #ffcc00; text-shadow: 0 0 15px #ffcc00; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">🔑 ENIGMA MACHINE 3D — SUBNET 63 MINER</h1>', unsafe_allow_html=True)
st.markdown("**Bunker POV activated. Orbit the machine. Drag tools to hook them. Click to inspect or zoom.**")

# Session State
if "hooked_tools" not in st.session_state:
    st.session_state.hooked_tools = []
if "tool_configs" not in st.session_state:
    st.session_state.tool_configs = {t: {"enabled": True} for t in ["ScienceClaw", "GPD", "AI-Researcher", "HyperAgent", "Chutes"]}
if "zoom_machine" not in st.session_state:
    st.session_state.zoom_machine = False
if "last_inspected" not in st.session_state:
    st.session_state.last_inspected = None

# ====================== 3D GAME SCENE (Pure three.js via CDN) ======================
three_js_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>body {{ margin:0; overflow:hidden; background:#0a0503; }}</style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
    <script>
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x0a0503, 10, 50);
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{antialias: true}});
        renderer.setSize(window.innerWidth, 620);
        document.body.appendChild(renderer.domElement);

        // Lights + Atmosphere
        scene.add(new THREE.AmbientLight(0x404040));
        const pointLight = new THREE.PointLight(0xffcc88, 1.5);
        pointLight.position.set(10, 15, 10);
        scene.add(pointLight);

        // Wooden table
        const tableGeo = new THREE.PlaneGeometry(15, 15);
        const tableMat = new THREE.MeshStandardMaterial({{color: 0x3c2f1f, roughness: 0.95}});
        const table = new THREE.Mesh(tableGeo, tableMat);
        table.rotation.x = -Math.PI / 2;
        table.position.y = -2;
        scene.add(table);

        // Enigma Machine (GLB from raw GitHub URL - update if you change the path)
        const loader = new THREE.GLTFLoader();
        let enigmaModel;
        loader.load('https://raw.githubusercontent.com/jbequ5/Enigma-Machine-Miner/main/components/enigma_3d/frontend/public/models/enigma.glb', (gltf) => {{
            enigmaModel = gltf.scene;
            enigmaModel.scale.set(1.6, 1.6, 1.6);
            scene.add(enigmaModel);
        }}, undefined, (error) => console.error('GLB load error:', error));

        // Orbit Controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        camera.position.set(0, 8, 18);

        // Simple tool spheres (draggable placeholder)
        const tools = ["ScienceClaw", "GPD", "AI-Researcher", "HyperAgent", "Chutes"];
        const toolMeshes = [];
        tools.forEach((name, i) => {{
            const geo = new THREE.SphereGeometry(0.65, 32, 32);
            const mat = new THREE.MeshStandardMaterial({{color: 0xffaa00, emissive: 0xffaa00}});
            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(5 + Math.cos(i)*4, 2 + Math.sin(i)*1.5, -4 + i*1.5);
            mesh.userData = {{name: name}};
            scene.add(mesh);
            toolMeshes.push(mesh);
        }});

        // Click handler (inspect or zoom)
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        renderer.domElement.addEventListener('click', (event) => {{
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / 620) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(scene.children, true);
            if (intersects.length > 0) {{
                let obj = intersects[0].object;
                while (obj && !obj.userData.name) obj = obj.parent;
                if (obj && obj.userData.name) {{
                    window.parent.postMessage({{type: 'inspect_tool', tool: obj.userData.name}}, '*');
                }} else if (enigmaModel && intersects[0].object === enigmaModel) {{
                    window.parent.postMessage({{type: 'zoom_machine'}}, '*');
                }}
            }}
        }});

        // Drag simulation (click + move near machine = hook)
        // (Simplified - real drag would need more code; this gives the feel)

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        // Resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / 620;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, 620);
        }});
    </script>
</body>
</html>
"""

st.components.v1.html(three_js_html, height=620, scrolling=False)

# Event handling from 3D (via session state polling - simple but effective)
# For now we use sidebar buttons as fallback; full postMessage sync can be added later.

# Tool Status + Inspect Fallback
st.markdown("### 🛠️ Tools — Click spheres in 3D to inspect")
if st.session_state.hooked_tools:
    st.success("Hooked: " + ", ".join(st.session_state.hooked_tools))
else:
    st.info("Drag/click tools in the 3D scene to hook them (visual feedback coming).")

# Simple inspect buttons as backup while we refine JS
col = st.columns(5)
for i, tool in enumerate(["ScienceClaw", "GPD", "AI-Researcher", "HyperAgent", "Chutes"]):
    with col[i]:
        if st.button(f"Inspect {tool}"):
            st.session_state.last_inspected = tool
            st.rerun()

# Inspect Dialog
if st.session_state.last_inspected:
    tool = st.session_state.last_inspected
    with st.dialog(f"Customize {tool}"):
        st.write("Edit config — saves to miner")
        # Add your config fields here (expand as needed)
        if st.button("Save & Hook"):
            if tool not in st.session_state.hooked_tools:
                st.session_state.hooked_tools.append(tool)
            st.session_state.last_inspected = None
            st.rerun()

# Zoom Modal (same as before)
if st.session_state.zoom_machine:
    with st.dialog("🔍 ENIGMA ZOOM — FINAL LAUNCH"):
        # ... (copy the GOAL.md editing + LAUNCH code from previous version)
        goal_path = Path("goals/GOAL.md")
        current = goal_path.read_text() if goal_path.exists() else Path("goals/killer_base.md").read_text()
        edited = st.text_area("GOAL.md", current, height=400)
        if st.button("🚀 LAUNCH MINER"):
            goal_path.write_text(edited)
            st.success("Miner launched!")
            st.session_state.zoom_machine = False
            st.rerun()
        if st.button("Back"):
            st.session_state.zoom_machine = False
            st.rerun()

st.caption("3D Enigma powered by three.js (no build required). Orbit with mouse • Click tools • Everything syncs to GOAL.md")
