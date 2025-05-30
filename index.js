const express = require('express');
const app = express();
const bodyParser = require("body-parser");
const PORT = process.env.PORT || 7860;
const path = require('path');
__path = process.cwd();

require('events').EventEmitter.defaultMaxListeners = 500;

// Debug: Catch uncaught errors
process.on('uncaughtException', err => {
  console.error("Uncaught Exception:", err);
});
process.on('unhandledRejection', err => {
  console.error("Unhandled Rejection:", err);
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

let server, code;

try {
  server = require('./qr');
  code = require('./pair');
  app.use('/server', server);
  app.use('/code', code);
} catch (e) {
  console.error("Error loading routes:", e);
}

app.use('/pair', (req, res) => {
  res.sendFile(path.join(__path, 'pair.html'));
});
app.use('/qr', (req, res) => {
  res.sendFile(path.join(__path, 'qr.html'));
});
app.use('/', (req, res) => {
  res.sendFile(path.join(__path, 'main.html'));
});

app.listen(PORT, () => {
  console.log(`
Don't Forget To Give Star!

Server running on http://localhost:` + PORT);
});

module.exports = app;
