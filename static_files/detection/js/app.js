import { Application } from '@splinetool/runtime';

// Get the canvas element
const canvas = document.getElementById('canvas3d');

// Initialize Spline application
const app = new Application(canvas);

// Load the Spline scene
app.load('https://prod.spline.design/9G2hh6MXELEyyEYG/scene.splinecode');

// Optional: Adjust camera settings if the model appears too large or too small
app.on('load', () => {
    // Adjust camera distance, zoom, or any other properties if necessary
    const camera = app.scene.getCamera();
    camera.position.set(0, 1, 2);  // Example: Position camera for better fit
    camera.zoom = 0.5; // You can adjust the zoom level here to fit the scene
});

// Optionally: Make sure the canvas resizes when the window is resized
window.addEventListener('resize', () => {
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;
    app.resize(width, height); // Adjust the size of the Spline canvas to match container
});
