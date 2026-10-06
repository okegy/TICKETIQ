import {
  AfterViewInit,
  Component,
  ElementRef,
  Input,
  NgZone,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import * as THREE from 'three';

/**
 * Angular translation of the shadcn "CubeWave" scene (original: React Three Fiber).
 * A grid of instanced cubes riding a radial wave from the center outward.
 * Crests take the primary color, troughs the accent color — both read from the
 * app's CSS custom properties so the scene always matches the design system.
 * One InstancedMesh → one draw call for the entire grid.
 */
@Component({
  selector: 'app-cube-wave',
  standalone: true,
  template: `<div #container class="cube-wave-container"></div>`,
  styles: [
    `
      :host {
        display: block;
        width: 100%;
        height: 100%;
        min-height: 0;
      }
      .cube-wave-container {
        width: 100%;
        height: 100%;
        min-height: 0;
        overflow: hidden;
      }
    `,
  ],
})
export class CubeWaveComponent implements AfterViewInit, OnChanges, OnDestroy {
  @ViewChild('container', { static: true }) container!: ElementRef<HTMLDivElement>;

  /** Cubes per side (total = grid²). */
  @Input() grid = 12;
  /** Spacing between cube centers. */
  @Input() gap = 0.75;
  /** Wave speed multiplier. */
  @Input() speed = 1;
  /** CSS variable holding the crest color (default: --cw-primary). */
  @Input() primaryVar = '--primary';
  /** CSS variable holding the trough color (default: --cw-accent). */
  @Input() accentVar = '--accent';

  private renderer?: THREE.WebGLRenderer;
  private scene?: THREE.Scene;
  private camera?: THREE.PerspectiveCamera;
  private mesh?: THREE.InstancedMesh;
  private material?: THREE.MeshStandardMaterial;
  private geometry?: THREE.BoxGeometry;
  private resizeObserver?: ResizeObserver;
  private dummy = new THREE.Object3D();
  private tmpColor = new THREE.Color();
  private primaryColor = new THREE.Color('#6366f1');
  private accentColor = new THREE.Color('#22d3ee');

  ngAfterViewInit(): void {
    this.initScene();
    this.resizeObserver = new ResizeObserver(() => this.updateSize());
    this.resizeObserver.observe(this.container.nativeElement);
    this.updateSize();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!this.scene) return;
    if (changes['grid'] || changes['gap']) {
      this.rebuildMesh();
    }
    if (changes['primaryVar'] || changes['accentVar']) {
      this.readThemeColors();
    }
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
    this.renderer?.setAnimationLoop(null);
    this.geometry?.dispose();
    this.material?.dispose();
    this.renderer?.dispose();
    if (this.renderer?.domElement.parentElement === this.container.nativeElement) {
      this.container.nativeElement.removeChild(this.renderer.domElement);
    }
  }

  private initScene(): void {
    const el = this.container.nativeElement;

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(el.clientWidth || 1, el.clientHeight || 1);
    el.appendChild(this.renderer.domElement);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
    this.camera.position.set(8, 7, 8);
    this.camera.lookAt(0, 0, 0);

    // Studio-style lighting (matches the original environment="studio").
    const hemi = new THREE.HemisphereLight(0xbfd4ff, 0x0b1020, 0.9);
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(6, 10, 4);
    const rim = new THREE.DirectionalLight(0x9db4ff, 1.1);
    rim.position.set(-6, 4, -6);
    this.scene.add(hemi, key, rim);

    this.readThemeColors();
    this.rebuildMesh();

    // Respect reduced-motion: render a single static frame instead of a loop.
    const reducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (reducedMotion) {
      this.animate(0);
      this.renderer.render(this.scene, this.camera);
    } else {
      const clock = new THREE.Clock();
      this.renderer.setAnimationLoop(() => {
        this.animate(clock.getElapsedTime() * this.speed);
        this.renderer?.render(this.scene!, this.camera!);
      });
    }
  }

  private rebuildMesh(): void {
    if (!this.scene) return;

    if (this.mesh) {
      this.scene.remove(this.mesh);
      this.geometry?.dispose();
      this.mesh.dispose();
    }

    const count = this.grid * this.grid;
    this.geometry = new THREE.BoxGeometry(0.62, 0.62, 0.62);
    this.material = new THREE.MeshStandardMaterial({ roughness: 0.3, metalness: 0.35 });
    this.mesh = new THREE.InstancedMesh(this.geometry, this.material, count);
    this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this.scene.add(this.mesh);
  }

  private readThemeColors(): void {
    const styles = getComputedStyle(document.documentElement);
    const primary = styles.getPropertyValue(this.primaryVar).trim();
    const accent = styles.getPropertyValue(this.accentVar).trim();
    if (primary) this.primaryColor.set(primary);
    if (accent) this.accentColor.set(accent);
  }

  private animate(t: number): void {
    const mesh = this.mesh;
    if (!mesh) return;

    const half = (this.grid - 1) / 2;
    let i = 0;
    for (let x = 0; x < this.grid; x++) {
      for (let z = 0; z < this.grid; z++) {
        const dx = x - half;
        const dz = z - half;
        const d = Math.sqrt(dx * dx + dz * dz);
        const y = Math.sin(d * 0.9 - t * 2.1) * 0.45;
        this.dummy.position.set(dx * this.gap, y, dz * this.gap);
        this.dummy.updateMatrix();
        mesh.setMatrixAt(i, this.dummy.matrix);

        // Crest → primary, trough → accent.
        const k = (y + 0.45) / 0.9;
        this.tmpColor.copy(this.accentColor).lerp(this.primaryColor, k);
        mesh.setColorAt(i, this.tmpColor);
        i++;
      }
    }
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  }

  private updateSize(): void {
    const el = this.container.nativeElement;
    const w = el.clientWidth;
    const h = el.clientHeight;
    if (!this.renderer || !this.camera || w === 0 || h === 0) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }
}
