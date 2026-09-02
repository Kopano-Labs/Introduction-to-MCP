import React, { useEffect, useRef, useState, useCallback } from "react";
import * as THREE from "three";

export type MascotMood = "idle" | "listening" | "thinking" | "celebrating";

interface KCMascot3DProps {
  mood?: MascotMood;
  size?: number;
  interactive?: boolean;
  className?: string;
  onMascotClick?: () => void;
}

export const KCMascot3D: React.FC<KCMascot3DProps> = ({
  mood = "idle",
  size = 320,
  interactive = true,
  className = "",
  onMascotClick,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hasWebGL, setHasWebGL] = useState(true);
  const mousePosRef = useRef({ x: 0, y: 0, targetX: 0, targetY: 0 });
  const shockwaveTriggerRef = useRef(0);

  const handleClick = useCallback(() => {
    shockwaveTriggerRef.current = 1.0;
    if (onMascotClick) onMascotClick();
  }, [onMascotClick]);

  useEffect(() => {
    // 1. Check WebGL Capability
    const canvasTest = document.createElement("canvas");
    const gl = canvasTest.getContext("webgl2") || canvasTest.getContext("webgl") || canvasTest.getContext("experimental-webgl");
    if (!gl) {
      setHasWebGL(false);
      return;
    }

    const currentMount = mountRef.current;
    if (!currentMount) return;

    // 2. Scene, Camera, Renderer setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 1000);
    camera.position.set(0, 0, 5.5);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(size, size);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    currentMount.appendChild(renderer.domElement);

    // 3. Dynamic Cinematic Lighting Matrix
    const ambientLight = new THREE.AmbientLight(0x0a0f1d, 2.5);
    scene.add(ambientLight);

    // Cyan Key Light (Top-Right Front)
    const cyanKeyLight = new THREE.PointLight(0x00f0ff, 6, 20);
    cyanKeyLight.position.set(3, 4, 4);
    scene.add(cyanKeyLight);

    // Copper Gold Rim Light (Bottom-Left Back)
    const goldRimLight = new THREE.PointLight(0xd97706, 5, 20);
    goldRimLight.position.set(-3, -3, 2);
    scene.add(goldRimLight);

    // Obsidian Fill Light (Bottom Front)
    const fillLight = new THREE.DirectionalLight(0x1e293b, 1.5);
    fillLight.position.set(0, -4, 3);
    scene.add(fillLight);

    // 4. Root KC Hierarchy Group
    const kcRoot = new THREE.Group();
    scene.add(kcRoot);

    // ==========================================
    // A. CENTRAL OBSIDIAN QUANTUM CORE (ICHOR MESH)
    // ==========================================
    const coreGeo = new THREE.IcosahedronGeometry(1.0, 4);
    const coreMat = new THREE.MeshPhysicalMaterial({
      color: 0x05070c,
      emissive: 0x001724,
      emissiveIntensity: 0.25,
      metalness: 0.95,
      roughness: 0.12,
      clearcoat: 1.0,
      clearcoatRoughness: 0.08,
      reflectivity: 1.0,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    kcRoot.add(coreMesh);

    // Lattice Cage (Sub-surface Geometry Wire)
    const cageGeo = new THREE.IcosahedronGeometry(1.04, 2);
    const cageMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.18,
    });
    const cageMesh = new THREE.Mesh(cageGeo, cageMat);
    kcRoot.add(cageMesh);

    // ==========================================
    // B. LUMINESCENT QUANTUM EYE / SENSOR APERTURE
    // ==========================================
    const eyeGroup = new THREE.Group();
    eyeGroup.position.set(0, 0, 0.92);
    kcRoot.add(eyeGroup);

    // Outer Eye Bezel
    const bezelGeo = new THREE.TorusGeometry(0.38, 0.04, 16, 48);
    const bezelMat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      metalness: 0.9,
      roughness: 0.2,
      emissive: 0xd97706,
      emissiveIntensity: 0.4,
    });
    const bezelMesh = new THREE.Mesh(bezelGeo, bezelMat);
    eyeGroup.add(bezelMesh);

    // Inner Radiant Iris
    const irisGeo = new THREE.CircleGeometry(0.32, 32);
    const irisMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.95,
    });
    const irisMesh = new THREE.Mesh(irisGeo, irisMat);
    eyeGroup.add(irisMesh);

    // Pupil Lens Point
    const pupilGeo = new THREE.CircleGeometry(0.12, 32);
    const pupilMat = new THREE.MeshBasicMaterial({
      color: 0x030712,
    });
    const pupilMesh = new THREE.Mesh(pupilGeo, pupilMat);
    pupilMesh.position.z = 0.01;
    eyeGroup.add(pupilMesh);

    // Eye Halo Glow PointLight
    const eyeLight = new THREE.PointLight(0x00f0ff, 2.5, 3);
    eyeLight.position.set(0, 0, 0.1);
    eyeGroup.add(eyeLight);

    // ==========================================
    // C. GYROSCOPIC GIMBAL BLADES (COPPER-GOLD & CYAN)
    // ==========================================
    // Ring 1 (Inner Gold Segmented Ring)
    const ring1Geo = new THREE.TorusGeometry(1.4, 0.032, 16, 64);
    const ring1Mat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      emissive: 0xd97706,
      emissiveIntensity: 0.9,
      metalness: 0.85,
      roughness: 0.25,
    });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    kcRoot.add(ring1);

    // Ring 2 (Middle Cyan Orbital Gyro)
    const ring2Geo = new THREE.TorusGeometry(1.7, 0.024, 16, 64);
    const ring2Mat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x00f0ff,
      emissiveIntensity: 1.1,
      metalness: 0.9,
      roughness: 0.15,
    });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = Math.PI / 3;
    ring2.rotation.y = Math.PI / 6;
    kcRoot.add(ring2);

    // Ring 3 (Outer Kinetic Energy Halo)
    const ring3Geo = new THREE.TorusGeometry(2.05, 0.018, 16, 64);
    const ring3Mat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 0.6,
      transparent: true,
      opacity: 0.7,
    });
    const ring3 = new THREE.Mesh(ring3Geo, ring3Mat);
    ring3.rotation.x = -Math.PI / 4;
    kcRoot.add(ring3);

    // Satellite Satchels (3 Magnetic Nodes floating on Ring 2)
    const satelliteGroup = new THREE.Group();
    kcRoot.add(satelliteGroup);
    const satGeo = new THREE.BoxGeometry(0.12, 0.12, 0.12);
    const satMat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      emissive: 0xf59e0b,
      emissiveIntensity: 1.2,
      metalness: 0.9,
    });

    const satellites: THREE.Mesh[] = [];
    for (let i = 0; i < 3; i++) {
      const sat = new THREE.Mesh(satGeo, satMat);
      satelliteGroup.add(sat);
      satellites.push(sat);
    }

    // ==========================================
    // D. DYNAMIC QUANTUM PARTICLE NEBULA (120 NODES)
    // ==========================================
    const particleCount = 120;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleScales = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      const angle = (i / particleCount) * Math.PI * 2;
      const radius = 2.2 + (Math.random() - 0.5) * 1.2;
      particlePositions[i * 3] = Math.cos(angle) * radius;
      particlePositions[i * 3 + 1] = Math.sin(angle) * radius * 0.7 + (Math.random() - 0.5) * 0.8;
      particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 1.5;
      particleScales[i] = Math.random() * 0.05 + 0.02;
    }

    particleGeo.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x00f0ff,
      size: 0.045,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    kcRoot.add(particles);

    // ==========================================
    // E. SHOCKWAVE EXPANSION RING (CLICK BURST)
    // ==========================================
    const shockwaveGeo = new THREE.RingGeometry(0.1, 0.15, 48);
    const shockwaveMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.0,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
    });
    const shockwaveMesh = new THREE.Mesh(shockwaveGeo, shockwaveMat);
    shockwaveMesh.position.z = 0.1;
    kcRoot.add(shockwaveMesh);

    // ==========================================
    // 5. INTERACTION & POINTER TRACKING (SPRING-DAMPER)
    // ==========================================
    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive) return;
      const rect = currentMount.getBoundingClientRect();
      const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      mousePosRef.current.targetX = THREE.MathUtils.clamp(nx, -1.2, 1.2);
      mousePosRef.current.targetY = THREE.MathUtils.clamp(ny, -1.2, 1.2);
    };

    window.addEventListener("mousemove", handleMouseMove);

    // ==========================================
    // 6. 60FPS CINEMATIC KINEMATICS ANIMATION LOOP
    // ==========================================
    let animationFrameId: number;
    const clock = new THREE.Clock();
    let shockwaveScale = 0.1;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      // Smooth Inertia Spring-Damper Interpolation
      const mouse = mousePosRef.current;
      mouse.x += (mouse.targetX - mouse.x) * (0.08 + delta * 2.0);
      mouse.y += (mouse.targetY - mouse.y) * (0.08 + delta * 2.0);

      // A. Organic Breathing Hover Dynamics
      const hoverSpeed = mood === "thinking" ? 3.0 : (mood === "listening" ? 1.6 : 1.1);
      const hoverAmp = mood === "celebrating" ? 0.28 : 0.14;
      kcRoot.position.y = Math.sin(time * hoverSpeed) * hoverAmp;
      kcRoot.position.x = Math.cos(time * hoverSpeed * 0.7) * 0.05;

      // B. 3D Head-Tilt Gaze Orientation
      const targetPitch = mouse.y * 0.45;
      const targetYaw = mouse.x * 0.55;
      kcRoot.rotation.x += (targetPitch - kcRoot.rotation.x) * 0.09;
      kcRoot.rotation.y += (targetYaw - kcRoot.rotation.y) * 0.09;
      kcRoot.rotation.z = -mouse.x * 0.12;

      // Eye pupil reactive gaze micro-adjustment
      pupilMesh.position.x = mouse.x * 0.08;
      pupilMesh.position.y = mouse.y * 0.08;

      // C. Gyroscopic Gimbal Spin Velocities by Mood
      const spinSpeed = mood === "thinking" ? 4.5 : (mood === "celebrating" ? 6.0 : (mood === "listening" ? 1.8 : 1.0));
      ring1.rotation.z = time * 0.6 * spinSpeed;
      ring1.rotation.x = Math.sin(time * 0.5) * 0.4;

      ring2.rotation.y = time * 0.85 * spinSpeed;
      ring2.rotation.z = Math.cos(time * 0.4) * 0.5;

      ring3.rotation.x = -time * 0.4 * spinSpeed;
      ring3.rotation.z = Math.sin(time * 0.6) * 0.35;

      cageMesh.rotation.y = -time * 0.25;
      cageMesh.rotation.x = time * 0.15;

      // D. Orbital Satellites Motion
      satellites.forEach((sat, idx) => {
        const satAngle = time * 1.2 * spinSpeed + (idx * Math.PI * 2) / 3;
        const satRadius = 1.7;
        sat.position.set(
          Math.cos(satAngle) * satRadius,
          Math.sin(satAngle) * satRadius * 0.6,
          Math.sin(satAngle * 2) * 0.3
        );
        sat.rotation.x = time * 2.0;
        sat.rotation.y = time * 3.0;
      });

      // E. Particle Swirl Dynamics
      particles.rotation.y = time * 0.12 * spinSpeed;
      particles.rotation.z = -time * 0.08 * spinSpeed;

      // F. Eye Luminescence & Pulse Wave
      const irisPulseSpeed = mood === "celebrating" ? 10.0 : (mood === "thinking" ? 6.0 : 2.5);
      irisMat.opacity = 0.8 + Math.sin(time * irisPulseSpeed) * 0.2;
      eyeLight.intensity = 2.0 + Math.sin(time * irisPulseSpeed) * 1.2;

      // G. Interactive Shockwave Burst Pulse
      if (shockwaveTriggerRef.current > 0.0) {
        shockwaveScale += delta * 7.5;
        shockwaveMesh.scale.set(shockwaveScale, shockwaveScale, 1);
        shockwaveMat.opacity = THREE.MathUtils.clamp(1.0 - shockwaveScale / 3.0, 0, 1);

        if (shockwaveScale > 3.0) {
          shockwaveTriggerRef.current = 0.0;
          shockwaveScale = 0.1;
          shockwaveMat.opacity = 0.0;
        }
      }

      renderer.render(scene, camera);
    };

    animate();

    // 7. Unmount & WebGL Resource Cleanup
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animationFrameId);
      if (currentMount && renderer.domElement && currentMount.contains(renderer.domElement)) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      cageGeo.dispose();
      cageMat.dispose();
      bezelGeo.dispose();
      bezelMat.dispose();
      irisGeo.dispose();
      irisMat.dispose();
      pupilGeo.dispose();
      pupilMat.dispose();
      ring1Geo.dispose();
      ring1Mat.dispose();
      ring2Geo.dispose();
      ring2Mat.dispose();
      ring3Geo.dispose();
      ring3Mat.dispose();
      satGeo.dispose();
      satMat.dispose();
      particleGeo.dispose();
      particleMat.dispose();
      shockwaveGeo.dispose();
      shockwaveMat.dispose();
    };
  }, [mood, size, interactive, handleClick]);

  if (!hasWebGL) {
    // 2D Vector Silhouette Fallback
    return (
      <div
        className={`kc-mascot-2d-fallback relative flex items-center justify-center cursor-pointer ${className}`}
        style={{ width: size, height: size }}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-label="KC Mascot — KC My Boy"
      >
        <svg viewBox="0 0 200 200" className="w-full h-full drop-shadow-2xl">
          <defs>
            <radialGradient id="kcCoreGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#0F172A" />
              <stop offset="100%" stopColor="#05070C" />
            </radialGradient>
            <linearGradient id="kcGoldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#D97706" />
              <stop offset="100%" stopColor="#F59E0B" />
            </linearGradient>
          </defs>
          <circle cx="100" cy="100" r="68" fill="url(#kcCoreGrad)" stroke="#00F0FF" strokeWidth="2.5" />
          <circle cx="100" cy="100" r="86" fill="none" stroke="url(#kcGoldGrad)" strokeWidth="2" strokeDasharray="10 6" className="animate-spin origin-center" />
          <circle cx="100" cy="95" r="24" fill="#00F0FF" className="animate-pulse" />
          <circle cx="100" cy="95" r="14" fill="#05070C" />
        </svg>
      </div>
    );
  }

  return (
    <div
      ref={mountRef}
      className={`kc-mascot-3d-canvas relative flex items-center justify-center cursor-pointer transition-transform duration-300 hover:scale-105 active:scale-95 ${className}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-label="Living 3D KC Mascot — KC My Boy"
      style={{ width: size, height: size }}
    />
  );
};

export default KCMascot3D;
