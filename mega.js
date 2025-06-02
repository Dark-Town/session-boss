const fs = require('fs');
const util = require('util');
const { Storage } = require('megajs');

const upload = async (filePath, fileName) => {
    const storage = await new Storage({
        email: 'thelastcroneb@gmail.com',
        password: 'Tcroneb/2025'
    }).ready;

    const up = storage.upload(fileName, fs.createReadStream(filePath));

    await util.promisify(up.complete.bind(up))();

    const file = storage.files.find(f => f.name === fileName);
    return file.link(); // Returns public link
};

module.exports = { upload };
