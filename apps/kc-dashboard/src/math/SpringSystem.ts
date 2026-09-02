/**
 * Second-Order Dynamic Spring-Damper Physics Engine
 * Models physical mass, spring recoil, and damping overshoot:
 * f(t) + 2*zeta*omega_n*x_dot + omega_n^2*x = omega_n^2*x_target
 */
export class SpringDamper3D {
  private position: [number, number, number] = [0, 0, 0];
  private velocity: [number, number, number] = [0, 0, 0];
  private target: [number, number, number] = [0, 0, 0];

  constructor(
    public frequency: number = 3.5, // Natural frequency (rad/s)
    public damping: number = 0.75   // Damping ratio (0.7-0.8 = snappy with realistic micro-overshoot)
  ) {}

  public setPosition(x: number, y: number, z: number): void {
    this.position = [x, y, z];
    this.target = [x, y, z];
    this.velocity = [0, 0, 0];
  }

  public setTarget(x: number, y: number, z: number): void {
    this.target = [x, y, z];
  }

  public applyImpulse(fx: number, fy: number, fz: number): void {
    this.velocity[0] += fx;
    this.velocity[1] += fy;
    this.velocity[2] += fz;
  }

  public update(dt: number): [number, number, number] {
    const clampedDt = Math.min(dt, 0.05); // Prevent instability on frame drops
    for (let i = 0; i < 3; i++) {
      const f = 1.0 + 2.0 * clampedDt * this.damping * this.frequency;
      const oo = this.frequency * this.frequency;
      const v = this.velocity[i];
      const p = this.position[i];
      const t = this.target[i];
      const det = f + clampedDt * clampedDt * oo;

      this.position[i] = (f * p + clampedDt * v + clampedDt * clampedDt * oo * t) / det;
      this.velocity[i] = (v + clampedDt * oo * (t - p)) / det;
    }
    return [this.position[0], this.position[1], this.position[2]];
  }

  public getPosition(): [number, number, number] {
    return [this.position[0], this.position[1], this.position[2]];
  }

  public getVelocity(): [number, number, number] {
    return [this.velocity[0], this.velocity[1], this.velocity[2]];
  }
}
