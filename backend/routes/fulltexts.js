const express = require('express');
const router = express.Router();
const { FullText } = require('../models');
const { Op } = require('sequelize');

router.get('/', async (req, res) => {
  const { filename } = req.query;
  if (!filename) return res.status(400).json({ error: 'filename is required' });

  try {
    // Find all entries where EntryID starts with the PMID (filename)
    const results = await FullText.findAll({
      where: {
        EntryID: {
          [Op.like]: `${filename}_%`
        }
      }
    });
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: 'Server error', details: err.message });
  }
});

module.exports = router;