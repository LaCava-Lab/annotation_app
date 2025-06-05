process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const { Paper, sequelize } = require('../models'); // Adjust path if needed

async function importPapersCSV(filePath) {
  const records = [];

  return new Promise((resolve, reject) => {
    fs.createReadStream(path.resolve(filePath))
      .pipe(csv())
      .on('data', (row) => {
        records.push({
          PMID: row.PMID,
          DOI_URL: row.DOI,
          Title: row.Title,
          Authors: row.Authors ? row.Authors.split(',').map(a => a.trim()) : [],
          Year: parseInt(row.Year) || null,
          Journal: row.Journal,
          Volume: row.Volume || null,
          Issue: row.Issue || null,
          Pages: row.Pages || null,
          Abstract: row.Abstract || null,
          UsersCompleted: [],
          UsersCurrent: []
        });
      })
      .on('end', async () => {
        try {
          await Paper.bulkCreate(records, { ignoreDuplicates: true });
          console.log(`Imported ${records.length} papers from ${filePath}`);
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
}

// CLI usage
const args = process.argv.slice(2);
if (!args[0]) {
  console.error('Usage: node utils/importPapers.js path/to/Papers.csv');
  process.exit(1);
}

const file = args[0];

sequelize.sync().then(() => {
  importPapersCSV(file).finally(() => sequelize.close());
});
