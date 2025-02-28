// Import dependencies
const express = require('express');

// Create an Express app
const app = express();

// Middleware (e.g., parse JSON requests)
app.use(express.json());

// Set the port for the application
const PORT = process.env.PORT || 8080;

// Define routes
app.get('/', (req, res) => {
    res.send('Welcome to Voxalyze! Unlocking the Power of Customer Relations Intelligence.');
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
