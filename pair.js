const express = require('express');
const fs = require('fs');
const { makeid } = require('./gen-id');
const { upload } = require('./mega');
const { default: makeWASocket, useMultiFileAuthState, delay, makeCacheableSignalKeyStore, Browsers } = require('baileys');
const pino = require('pino');
const archiver = require('archiver');

const router = express.Router();

function zipDirectory(sourceDir, outPath) {
    const archive = archiver('zip', { zlib: { level: 9 } });
    const stream = fs.createWriteStream(outPath);

    return new Promise((resolve, reject) => {
        archive
            .directory(sourceDir, false)
            .on('error', err => reject(err))
            .pipe(stream);

        stream.on('close', () => resolve());
        archive.finalize();
    });
}

router.get('/code', async (req, res) => {
    try {
        const id = makeid();
        const number = req.query.number?.replace(/[^0-9]/g, '');

        if (!number) return res.status(400).send("Missing number");

        const { state } = await useMultiFileAuthState('./temp/' + id);
        const sock = makeWASocket({
            auth: {
                creds: state.creds,
                keys: makeCacheableSignalKeyStore(state.keys, pino({ level: "fatal" }).child({ level: "fatal" }))
            },
            browser: Browsers.macOS('Safari'),
            printQRInTerminal: false,
            logger: pino({ level: "fatal" }).child({ level: "fatal" }),
        });

        await delay(2000);
        const code = await sock.requestPairingCode(number);

        const zipPath = `./temp/${id}.zip`;
        await zipDirectory(`./temp/${id}`, zipPath);

        const megaUrl = await upload(zipPath, `${id}.zip`);

        res.send(`✅ Pairing Code: ${code}\n🔗 Mega Link: ${megaUrl}`);
    } catch (e) {
        console.error("❌ Error in /pair/code:", e);
        res.status(500).send("Server error: " + e.message);
    }
});

module.exports = router;
