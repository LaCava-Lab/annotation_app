process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const fs = require('fs');
const path = require('path');
const csvParser = require('csv-parser');
const { FullText } = require('../models'); // adjust path if needed
const db = require('../models'); // ensure Sequelize is initialized

const importCSV = async (filePath) => {
    const records = [];

    return new Promise((resolve, reject) => {
        fs.createReadStream(filePath, { encoding: 'utf8' })
            .pipe(csvParser())
            .on('data', (row) => {
                const rawPMID = row.EntryID?.split('_')[0];
                records.push({
                    EntryID: row.EntryID,
                    PMCID: row.filename,
                    PMID: rawPMID,
                    Section: row.section_type,
                    Type: row.subtitle,
                    TextValue: row.text
                });
            })

            .on('end', async () => {
                try {
                    await FullText.bulkCreate(records, { ignoreDuplicates: true });
                    console.log(`Imported ${records.length} records into FullText`);
                    resolve();
                } catch (err) {
                    console.error('Import failed:', err);
                    reject(err);
                }
            })
            .on('error', (err) => {
                console.error('CSV read error:', err);
                reject(err);
            });
    });
};

const args = process.argv.slice(2);
if (args.length === 0) {
    console.error('Usage: node importFullText.js path/to/file.csv');
    process.exit(1);
}

const filePath = path.resolve(args[0]);
if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
}

db.sequelize.sync().then(() => {
    importCSV(filePath).finally(() => {
        db.sequelize.close();
    });
});
