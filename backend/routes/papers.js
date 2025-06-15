const express = require('express');
const router = express.Router();
const { Paper } = require('../models');

router.get('/', async (req, res) => {
  const papers = await Paper.findAll();
  res.json(papers);
});

router.get('/:pmid', async (req, res) => {
  const { pmid } = req.params;
  try {
    const paper = await Paper.findOne({ where: { PMID: pmid } });
    if (!paper) return res.status(404).json({ error: "Paper not found" });
    res.json(paper);
  } catch (err) {
    res.status(500).json({ error: "Database error" });
  }
});

module.exports = router;
