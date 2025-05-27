const fs = require('fs');
const csv = require('csv-parser');
const { Paper } = require('../models');
const path = require('path');

async function seedPapers() {
  const results = [];
  fs.createReadStream(path.join(__dirname, '../data/papers_table.csv'))
    .pipe(csv())
    .on('data', (data) => results.push(data))
    .on('end', async () => {
      await Paper.bulkCreate(results);
      console.log('Papers seeded.');
    });
}

seedPapers();
