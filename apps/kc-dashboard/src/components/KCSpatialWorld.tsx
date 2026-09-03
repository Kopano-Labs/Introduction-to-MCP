import React, { useEffect, useRef, useState, useCallback } from "react";
import * as THREE from "three";
import { SpringDamper3D } from "../math/SpringSystem";

export type WorldDomain = "general" | "work" | "football" | "cars4mars" | "learning" | "uyscuti";
export type MascotMood = "idle" | "listening" | "thinking" | "celebrating";

interface KCSpatialWorldProps {
  domain?: WorldDomain;
  mood?: MascotMood;
  interactive?: boolean;
  className?: string;
  onSelectDomain?: (domain: WorldDomain) => void;
  onMascotClick?: () => void;
}

export const KCSpatialWorld: React.FC<KCSpatialWorldProps> = ({
  domain = "general",
  mood = "idle",
  interactive = true,
  className = "",
  onSelectDomain,
  onMascotClick,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hasWebGL, setHasWebGL] = useState(true);
  const [fps, setFps] = useState(60);

  // Physics & Kinematics Refs
  const springRef = useRef<SpringDamper3D>(new SpringDamper3D(4.0, 0.72));
  const rotSpringRef = useRef<SpringDamper3D>(new SpringDamper3D(3.2, 0.8));
  const pointerRef = useRef({ x: 0, y: 0, prevX: 0, prevY: 0, vx: 0, vy: 0 });
  const ripplesRef = useRef<Array<{ x: number; y: number; radius: number; intensity: number; maxRadius: number }>>([]);

  const handlePointerMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (!mountRef.current) return;
    const rect = mountRef.current.getBoundingClientRect();
    const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1);

    const p = pointerRef.current;
    p.vx = (nx - p.prevX) / 0.016;
    p.vy = (ny - p.prevY) / 0.016;
    p.prevX = nx;
    p.prevY = ny;
    p.x = THREE.MathUtils.clamp(nx, -1.2, 1.2);
    p.y = THREE.MathUtils.clamp(ny, -1.2, 1.2);

    // Spring targets: subtle parallax lean and head-tilt
    springRef.current.setTarget(p.x * 0.4, p.y * 0.35, 0);
    rotSpringRef.current.setTarget(p.y * 0.45 - p.vy * 0.02, p.x * 0.55 + p.vx * 0.02, -p.x * 0.15);
  }, []);

  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (!mountRef.current) return;
    const rect = mountRef.current.getBoundingClientRect();
    const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1);

    // Trigger context membrane ripple wave
    ripplesRef.current.push({
      x: nx * 3.0,
      y: ny * 2.0,
      radius: 0.1,
      intensity: 1.0,
      maxRadius: 6.0,
    });

    // Apply kinetic impulse to KC
    springRef.current.applyImpulse((Math.random() - 0.5) * 0.8, 0.6, -0.8);
    rotSpringRef.current.applyImpulse((Math.random() - 0.5) * 1.5, (Math.random() - 0.5) * 1.5, 0);

    if (onMascotClick) onMascotClick();
  }, [onMascotClick]);

  useEffect(() => {
    // 1. WebGL Support Test
    const canvasTest = document.createElement("canvas");
    const gl = canvasTest.getContext("webgl2") || canvasTest.getContext("webgl");
    if (!gl) {
      setHasWebGL(false);
      return;
    }

    const currentMount = mountRef.current;
    if (!currentMount) return;

    // 2. Scene, Camera, and Atmosphere
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x060913, 0.09);

    const camera = new THREE.PerspectiveCamera(45, currentMount.clientWidth / currentMount.clientHeight, 0.1, 100);
    camera.position.set(0, 0.5, 6.5);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    currentMount.appendChild(renderer.domElement);

    // 3. Dynamic Multi-Point Lighting Rig
    const ambientLight = new THREE.AmbientLight(0x0a1128, 2.5);
    scene.add(ambientLight);

    const keyCyanLight = new THREE.PointLight(0x00f0ff, 6, 25);
    keyCyanLight.position.set(4, 5, 5);
    scene.add(keyCyanLight);

    const rimGoldLight = new THREE.PointLight(0xd97706, 5, 25);
    rimGoldLight.position.set(-4, -3, 3);
    scene.add(rimGoldLight);

    const domainLight = new THREE.PointLight(0x38bdf8, 4, 30);
    domainLight.position.set(0, -2, -2);
    scene.add(domainLight);

    // 4. THE CONTEXT MEMBRANE (Deformable Dynamic Surface Grid)
    const membraneWidth = 14;
    const membraneHeight = 14;
    const membraneSegments = 60;
    const membraneGeo = new THREE.PlaneGeometry(membraneWidth, membraneHeight, membraneSegments, membraneSegments);
    const membraneMat = new THREE.MeshStandardMaterial({
      color: 0x050914,
      emissive: 0x0284c7,
      emissiveIntensity: 0.18,
      wireframe: true,
      transparent: true,
      opacity: 0.45,
      metalness: 0.8,
      roughness: 0.2,
    });
    const membrane = new THREE.Mesh(membraneGeo, membraneMat);
    membrane.rotation.x = -Math.PI / 2.3;
    membrane.position.y = -2.2;
    scene.add(membrane);

    const membraneOriginalPositions = membraneGeo.attributes.position.clone();

    // 5. KC MASTER ENTITY (Ichor Quantum Core + Gyroscopic Gimbals)
    const kcRoot = new THREE.Group();
    scene.add(kcRoot);

    // A. Icosahedral Obsidian Core
    const coreGeo = new THREE.IcosahedronGeometry(1.0, 4);
    const coreMat = new THREE.MeshPhysicalMaterial({
      color: 0x030712,
      emissive: 0x001724,
      emissiveIntensity: 0.3,
      metalness: 0.95,
      roughness: 0.1,
      clearcoat: 1.0,
      clearcoatRoughness: 0.05,
      reflectivity: 1.0,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    kcRoot.add(coreMesh);

    // Sub-surface Wireframe Cage
    const cageGeo = new THREE.IcosahedronGeometry(1.05, 2);
    const cageMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.22,
    });
    const cageMesh = new THREE.Mesh(cageGeo, cageMat);
    kcRoot.add(cageMesh);

    // B. Luminescent Gaze Eye Aperture
    const eyeGroup = new THREE.Group();
    eyeGroup.position.set(0, 0, 0.92);
    kcRoot.add(eyeGroup);

    const bezelGeo = new THREE.TorusGeometry(0.36, 0.04, 16, 48);
    const bezelMat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      emissive: 0xd97706,
      emissiveIntensity: 0.5,
      metalness: 0.9,
    });
    const bezelMesh = new THREE.Mesh(bezelGeo, bezelMat);
    eyeGroup.add(bezelMesh);

    const irisGeo = new THREE.CircleGeometry(0.3, 32);
    const irisMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.95,
    });
    const irisMesh = new THREE.Mesh(irisGeo, irisMat);
    eyeGroup.add(irisMesh);

    const pupilGeo = new THREE.CircleGeometry(0.12, 32);
    const pupilMat = new THREE.MeshBasicMaterial({ color: 0x020617 });
    const pupilMesh = new THREE.Mesh(pupilGeo, pupilMat);
    pupilMesh.position.z = 0.01;
    eyeGroup.add(pupilMesh);

    const eyeGlowLight = new THREE.PointLight(0x00f0ff, 3, 4);
    eyeGlowLight.position.set(0, 0, 0.15);
    eyeGroup.add(eyeGlowLight);

    // C. Gyroscopic Gimbal Blades
    const ring1Geo = new THREE.TorusGeometry(1.42, 0.032, 16, 64);
    const ring1Mat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      emissive: 0xd97706,
      emissiveIntensity: 0.9,
      metalness: 0.85,
    });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    kcRoot.add(ring1);

    const ring2Geo = new THREE.TorusGeometry(1.75, 0.024, 16, 64);
    const ring2Mat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x00f0ff,
      emissiveIntensity: 1.1,
      metalness: 0.9,
    });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = Math.PI / 3;
    ring2.rotation.y = Math.PI / 6;
    kcRoot.add(ring2);

    const ring3Geo = new THREE.TorusGeometry(2.1, 0.018, 16, 64);
    const ring3Mat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 0.7,
      transparent: true,
      opacity: 0.7,
    });
    const ring3 = new THREE.Mesh(ring3Geo, ring3Mat);
    ring3.rotation.x = -Math.PI / 4;
    kcRoot.add(ring3);

    // Satellites
    const satGroup = new THREE.Group();
    kcRoot.add(satGroup);
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
      satGroup.add(sat);
      satellites.push(sat);
    }

    // D. Quantum Particle Nebula
    const pCount = 140;
    const pGeo = new THREE.BufferGeometry();
    const pPos = new Float32Array(pCount * 3);
    for (let i = 0; i < pCount; i++) {
      const ang = (i / pCount) * Math.PI * 2;
      const rad = 2.4 + (Math.random() - 0.5) * 1.5;
      pPos[i * 3] = Math.cos(ang) * rad;
      pPos[i * 3 + 1] = Math.sin(ang) * rad * 0.7 + (Math.random() - 0.5) * 0.9;
      pPos[i * 3 + 2] = (Math.random() - 0.5) * 2.0;
    }
    pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
    const pMat = new THREE.PointsMaterial({
      color: 0x00f0ff,
      size: 0.05,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
    });
    const particles = new THREE.Points(pGeo, pMat);
    kcRoot.add(particles);

    // ==========================================
    // 6. INTENT-DRIVEN SPATIAL WORLD FORMATIONS
    // ==========================================
    const worldGroup = new THREE.Group();
    scene.add(worldGroup);

    // Formation A: Work / KasiLink Gateway Nodes (Gold / Sapphire)
    const workGroup = new THREE.Group();
    for (let i = 0; i < 4; i++) {
      const nodeGeo = new THREE.CylinderGeometry(0.1, 0.1, 1.8, 16);
      const nodeMat = new THREE.MeshStandardMaterial({
        color: 0xd97706,
        emissive: 0xb45309,
        emissiveIntensity: 0.8,
        metalness: 0.8,
      });
      const node = new THREE.Mesh(nodeGeo, nodeMat);
      const ang = (i / 4) * Math.PI * 2;
      node.position.set(Math.cos(ang) * 4.0, -1.0, Math.sin(ang) * 2.5 - 2);
      workGroup.add(node);
    }
    worldGroup.add(workGroup);

    // Formation B: Football / FiveS Arena Pitch Arcs (Emerald / Cyan)
    const footballGroup = new THREE.Group();
    const pitchArcGeo = new THREE.TorusGeometry(3.6, 0.04, 16, 64, Math.PI);
    const pitchArcMat = new THREE.MeshStandardMaterial({
      color: 0x10b981,
      emissive: 0x059669,
      emissiveIntensity: 1.0,
    });
    const pitchArc = new THREE.Mesh(pitchArcGeo, pitchArcMat);
    pitchArc.rotation.x = Math.PI / 2;
    pitchArc.position.set(0, -1.8, -1.5);
    footballGroup.add(pitchArc);
    worldGroup.add(footballGroup);

    // Formation C: Cars4Mars / DFR-01 Rover Telematics Frame (Copper / Crimson)
    const roverGroup = new THREE.Group();
    const hexGeo = new THREE.RingGeometry(2.8, 2.9, 6);
    const hexMat = new THREE.MeshStandardMaterial({
      color: 0xf97316,
      emissive: 0xe11d48,
      emissiveIntensity: 0.8,
      side: THREE.DoubleSide,
    });
    const hex = new THREE.Mesh(hexGeo, hexMat);
    hex.position.set(0, 0, -3.0);
    roverGroup.add(hex);
    worldGroup.add(roverGroup);

    // Formation D: UY Scuti Hypergiant Stellar Accretion Disc (Red / Cyan Corona)
    const scutiGroup = new THREE.Group();
    const scutiRingGeo = new THREE.TorusGeometry(3.8, 0.045, 16, 80);
    const scutiRingMat = new THREE.MeshStandardMaterial({
      color: 0xff2a4d,
      emissive: 0xff2a4d,
      emissiveIntensity: 1.4,
      metalness: 0.9,
    });
    const scutiRing = new THREE.Mesh(scutiRingGeo, scutiRingMat);
    scutiRing.rotation.x = Math.PI / 3;
    scutiGroup.add(scutiRing);

    const scutiInnerGeo = new THREE.RingGeometry(1.8, 2.2, 32);
    const scutiInnerMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35,
      blending: THREE.AdditiveBlending,
    });
    const scutiInner = new THREE.Mesh(scutiInnerGeo, scutiInnerMat);
    scutiInner.rotation.x = -Math.PI / 4;
    scutiGroup.add(scutiInner);
    worldGroup.add(scutiGroup);

    // Formation Visibility & Animation Weight
    const updateWorldFormations = (targetDomain: WorldDomain) => {
      workGroup.visible = targetDomain === "work" || targetDomain === "general";
      footballGroup.visible = targetDomain === "football" || targetDomain === "general";
      roverGroup.visible = targetDomain === "cars4mars" || targetDomain === "general";
      scutiGroup.visible = targetDomain === "uyscuti" || targetDomain === "general";

      if (targetDomain === "work") {
        domainLight.color.setHex(0xd97706);
        membraneMat.emissive.setHex(0xd97706);
      } else if (targetDomain === "football") {
        domainLight.color.setHex(0x10b981);
        membraneMat.emissive.setHex(0x059669);
      } else if (targetDomain === "cars4mars") {
        domainLight.color.setHex(0xf97316);
        membraneMat.emissive.setHex(0xe11d48);
      } else if (targetDomain === "learning") {
        domainLight.color.setHex(0x8b5cf6);
        membraneMat.emissive.setHex(0x6d28d9);
      } else if (targetDomain === "uyscuti") {
        domainLight.color.setHex(0xff2a4d);
        membraneMat.emissive.setHex(0xd90429);
      } else {
        domainLight.color.setHex(0x00f0ff);
        membraneMat.emissive.setHex(0x0284c7);
      }
    };

    updateWorldFormations(domain);

    // ==========================================
    // 7. 60FPS CINEMATIC KINEMATICS & DEFORMATION LOOP
    // ==========================================
    let animId: number;
    const clock = new THREE.Clock();
    let frameCounter = 0;
    let lastTime = performance.now();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      // FPS Monitor
      frameCounter++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(frameCounter);
        frameCounter = 0;
        lastTime = now;
      }

      // Physics Springs Update
      const pos = springRef.current.update(delta);
      const rot = rotSpringRef.current.update(delta);

      // A. Position & Head-Tilt Application
      const hoverSpeed = mood === "thinking" ? 3.2 : 1.2;
      const hoverAmp = mood === "celebrating" ? 0.25 : 0.12;
      kcRoot.position.set(pos[0], pos[1] + Math.sin(time * hoverSpeed) * hoverAmp, pos[2]);
      kcRoot.rotation.set(rot[0], rot[1], rot[2]);

      // Eye Pupil micro-saccades
      pupilMesh.position.x = pointerRef.current.x * 0.08 + Math.sin(time * 2.4) * 0.015;
      pupilMesh.position.y = pointerRef.current.y * 0.08 + Math.cos(time * 2.4) * 0.015;

      // B. Gyro Blades Rotation Dynamics
      const spinMult = mood === "thinking" ? 4.0 : (mood === "celebrating" ? 5.5 : (mood === "listening" ? 1.8 : 1.0));
      ring1.rotation.z = time * 0.6 * spinMult;
      ring1.rotation.x = Math.sin(time * 0.5) * 0.4;

      ring2.rotation.y = time * 0.85 * spinMult;
      ring2.rotation.z = Math.cos(time * 0.4) * 0.5;

      ring3.rotation.x = -time * 0.45 * spinMult;
      ring3.rotation.z = Math.sin(time * 0.6) * 0.35;

      cageMesh.rotation.y = -time * 0.25;
      cageMesh.rotation.x = time * 0.15;

      // C. Orbiting Satellites
      satellites.forEach((sat, idx) => {
        const satAngle = time * 1.2 * spinMult + (idx * Math.PI * 2) / 3;
        sat.position.set(Math.cos(satAngle) * 1.75, Math.sin(satAngle) * 1.0, Math.sin(satAngle * 2) * 0.35);
        sat.rotation.x = time * 2.0;
        sat.rotation.y = time * 3.0;
      });

      // D. Nebula Particle Swirl
      particles.rotation.y = time * 0.12 * spinMult;
      particles.rotation.z = -time * 0.08 * spinMult;

      // E. Luminescence Pulsing
      const pulseSpeed = mood === "celebrating" ? 10.0 : (mood === "thinking" ? 6.0 : 2.5);
      irisMat.opacity = 0.8 + Math.sin(time * pulseSpeed) * 0.2;
      eyeGlowLight.intensity = 2.5 + Math.sin(time * pulseSpeed) * 1.5;

      // F. Context Membrane Dynamic Wave Deformation
      const posAttr = membraneGeo.attributes.position;
      const origPos = membraneOriginalPositions;
      const ripples = ripplesRef.current;

      // Update ripples
      for (let r = ripples.length - 1; r >= 0; r--) {
        const rip = ripples[r];
        rip.radius += delta * 4.0;
        rip.intensity *= 0.94;
        if (rip.radius > rip.maxRadius || rip.intensity < 0.02) {
          ripples.splice(r, 1);
        }
      }

      for (let i = 0; i < posAttr.count; i++) {
        const vx = origPos.getX(i);
        const vy = origPos.getY(i);
        let vz = Math.sin(vx * 0.8 + time * 1.5) * Math.cos(vy * 0.8 + time * 1.2) * 0.18;

        // Apply ripples
        for (let r = 0; r < ripples.length; r++) {
          const rip = ripples[r];
          const dist = Math.hypot(vx - rip.x, vy - rip.y);
          const wave = Math.sin(dist * 3.0 - rip.radius * 2.0) * Math.exp(-Math.abs(dist - rip.radius));
          vz += wave * rip.intensity * 0.35;
        }

        posAttr.setZ(i, vz);
      }
      posAttr.needsUpdate = true;

      // G. World Formations Rotation
      workGroup.rotation.y = time * 0.1;
      footballGroup.rotation.z = Math.sin(time * 0.3) * 0.1;
      roverGroup.rotation.z = time * 0.15;
      scutiGroup.rotation.z = time * 0.25;

      renderer.render(scene, camera);
    };

    animate();

    // Resize Handler
    const handleResize = () => {
      if (!currentMount) return;
      camera.aspect = currentMount.clientWidth / currentMount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animId);
      if (currentMount && renderer.domElement && currentMount.contains(renderer.domElement)) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
      membraneGeo.dispose();
      membraneMat.dispose();
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
      pGeo.dispose();
      pMat.dispose();
      pitchArcGeo.dispose();
      pitchArcMat.dispose();
      hexGeo.dispose();
      hexMat.dispose();
      scutiRingGeo.dispose();
      scutiRingMat.dispose();
      scutiInnerGeo.dispose();
      scutiInnerMat.dispose();
    };
  }, [domain, mood]);

  if (!hasWebGL) {
    return (
      <div className={`kc-spatial-fallback flex items-center justify-center p-8 bg-slate-950 text-white rounded-2xl ${className}`}>
        <div className="text-center space-y-4 max-w-md">
          <div className="w-24 h-24 mx-auto rounded-full bg-cyan-500/20 border-2 border-cyan-400 flex items-center justify-center animate-pulse">
            <span className="text-3xl font-bold text-cyan-300">KC</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">KC My Boy — Spatial World</h2>
          <p className="text-sm text-slate-400">
            Running in high-speed accessible vector mode. All Kopano capabilities (Work, Football, Cars4Mars, Learning) are fully ready.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={mountRef}
      className={`kc-spatial-world-canvas relative w-full h-[540px] md:h-[640px] overflow-hidden rounded-3xl bg-slate-950 cursor-crosshair ${className}`}
      onPointerMove={interactive ? handlePointerMove : undefined}
      onClick={handleCanvasClick}
      role="region"
      aria-label="Kopano Labs Spatial World — KC Motion Engine"
    >
      {/* HUD Telemetry Overlay */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 pointer-events-none">
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping mr-1.5" />
          KC MOTION ENGINE · {fps} FPS
        </span>
        <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono text-amber-300 bg-amber-500/10 border border-amber-500/30 backdrop-blur-md">
          DOMAIN: {domain.toUpperCase()}
        </span>
      </div>

      <div className="absolute bottom-4 right-4 z-10 hidden sm:flex items-center gap-2 text-[11px] font-mono text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 backdrop-blur-md pointer-events-none">
        <span>SPRING DAMPER: ACTIVE</span>
        <span>·</span>
        <span>MEMBRANE: 3600 NODES</span>
      </div>
    </div>
  );
};

export default KCSpatialWorld;
