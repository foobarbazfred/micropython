import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.151/build/three.module.js';

// Three.js のセットアップ
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 立方体の作成
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 ,  wireframe: true });
window.cube = new THREE.Mesh(geometry, material);
scene.add(cube);
camera.position.z = 5;

// アニメーション
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
