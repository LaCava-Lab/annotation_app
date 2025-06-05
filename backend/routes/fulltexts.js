const express = require('express');
const router = express.Router();
const { FullText } = require('../models');

router.get('/', async (req, res) => {
  const { filename } = req.query;
  if (!filename) return res.status(400).json({ error: 'filename is required' });

  try {
    const results = await FullText.findAll({
      where: { PMID: filename }
    });
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: 'Server error', details: err.message });
  }
});

module.exports = router;
