import React, { useEffect, useRef, useState } from "react";
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
  size = 280,
  interactive = true,
  className = "",
  onMascotClick,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hasWebGL, setHasWebGL] = useState(true);
  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  useEffect(() => {
    // Check WebGL availability
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (!gl) {
      setHasWebGL(false);
      return;
    }

    const currentMount = mountRef.current;
    if (!currentMount) return;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(size, size);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    currentMount.appendChild(renderer.domElement);

    // 2. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x00f0ff, 3, 50);
    pointLight.position.set(2, 3, 4);
    scene.add(pointLight);

    const goldLight = new THREE.PointLight(0xd97706, 2, 50);
    goldLight.position.set(-2, -2, 3);
    scene.add(goldLight);

    // 3. KC Core Geometry Group
    const mascotGroup = new THREE.Group();
    scene.add(mascotGroup);

    // A. Central Obsidian Orb
    const coreGeo = new THREE.SphereGeometry(1.0, 32, 32);
    const coreMat = new THREE.MeshPhysicalMaterial({
      color: 0x0a0d14,
      metalness: 0.8,
      roughness: 0.15,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      reflectivity: 0.9,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    mascotGroup.add(coreMesh);

    // B. Eye / Lens (Electric Cyan Glow)
    const eyeGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.15, 32);
    const eyeMat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x00f0ff,
      emissiveIntensity: 1.8,
      roughness: 0.2,
    });
    const eyeMesh = new THREE.Mesh(eyeGeo, eyeMat);
    eyeMesh.rotation.x = Math.PI / 2;
    eyeMesh.position.z = 0.95;
    mascotGroup.add(eyeMesh);

    // C. Inner Gold Energy Ring
    const innerRingGeo = new THREE.TorusGeometry(1.35, 0.035, 16, 100);
    const innerRingMat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      emissive: 0xd97706,
      emissiveIntensity: 0.8,
      roughness: 0.3,
    });
    const innerRing = new THREE.Mesh(innerRingGeo, innerRingMat);
    mascotGroup.add(innerRing);

    // D. Outer Cyan Orbital Ring
    const outerRingGeo = new THREE.TorusGeometry(1.65, 0.025, 16, 100);
    const outerRingMat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x00f0ff,
      emissiveIntensity: 1.0,
      roughness: 0.2,
    });
    const outerRing = new THREE.Mesh(outerRingGeo, outerRingMat);
    outerRing.rotation.x = Math.PI / 3;
    mascotGroup.add(outerRing);

    // E. Floating Halo Particles
    const particleCount = 40;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      const angle = (i / (particleCount * 3)) * Math.PI * 2;
      const radius = 1.8 + Math.random() * 0.4;
      positions[i] = Math.cos(angle) * radius;
      positions[i + 1] = Math.sin(angle) * radius;
      positions[i + 2] = (Math.random() - 0.5) * 0.6;
    }
    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const particleMat = new THREE.PointsMaterial({
      color: 0x00f0ff,
      size: 0.04,
      transparent: true,
      opacity: 0.8,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    mascotGroup.add(particles);

    // 4. Mouse Move Listener
    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive) return;
      const rect = currentMount.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      setMousePos({ x, y });
    };

    window.addEventListener("mousemove", handleMouseMove);

    // 5. Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const time = clock.getElapsedTime();

      // Idle vertical hover
      const hoverSpeed = mood === "thinking" ? 2.5 : 1.2;
      const hoverAmp = mood === "celebrating" ? 0.25 : 0.12;
      mascotGroup.position.y = Math.sin(time * hoverSpeed) * hoverAmp;

      // Smooth cursor tracking rotation
      const targetRotX = mousePos.y * 0.35;
      const targetRotY = mousePos.x * 0.45;
      mascotGroup.rotation.x += (targetRotX - mascotGroup.rotation.x) * 0.08;
      mascotGroup.rotation.y += (targetRotY - mascotGroup.rotation.y) * 0.08;

      // Ring rotations by mood
      const spinMultiplier = mood === "thinking" ? 3.0 : (mood === "celebrating" ? 4.0 : 1.0);
      innerRing.rotation.z = time * 0.5 * spinMultiplier;
      innerRing.rotation.x = Math.sin(time * 0.4) * 0.3;
      outerRing.rotation.y = time * 0.7 * spinMultiplier;
      outerRing.rotation.z = Math.cos(time * 0.5) * 0.4;
      particles.rotation.z = -time * 0.2 * spinMultiplier;

      // Eye emission pulsing
      const pulseSpeed = mood === "celebrating" ? 8 : (mood === "thinking" ? 4 : 2);
      eyeMat.emissiveIntensity = 1.4 + Math.sin(time * pulseSpeed) * 0.6;

      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animationFrameId);
      if (currentMount && renderer.domElement) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
      coreGeo.dispose();
      eyeGeo.dispose();
      innerRingGeo.dispose();
      outerRingGeo.dispose();
      particleGeo.dispose();
    };
  }, [mood, size, interactive, mousePos]);

  if (!hasWebGL) {
    // Elegant 2D Fallback for Low-End / Non-WebGL Devices
    return (
      <div
        className={`kc-mascot-2d-fallback ${className}`}
        style={{ width: size, height: size }}
        onClick={onMascotClick}
        role="button"
        tabIndex={0}
        aria-label="KC Mascot"
      >
        <svg viewBox="0 0 200 200" className="w-full h-full">
          <circle cx="100" cy="100" r="70" fill="#0A0D14" stroke="#00F0FF" strokeWidth="3" />
          <circle cx="100" cy="100" r="85" fill="none" stroke="#D97706" strokeWidth="2" strokeDasharray="8 6" className="animate-spin" />
          <circle cx="100" cy="95" r="22" fill="#00F0FF" />
          <circle cx="100" cy="95" r="12" fill="#0A0D14" />
        </svg>
      </div>
    );
  }

  return (
    <div
      ref={mountRef}
      className={`kc-mascot-3d-container cursor-pointer transition-transform duration-300 hover:scale-105 ${className}`}
      onClick={onMascotClick}
      role="button"
      tabIndex={0}
      aria-label="KC 3D Mascot — KC My Boy"
      style={{ width: size, height: size }}
    />
  );
};

export default KCMascot3D;
