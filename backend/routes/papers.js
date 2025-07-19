const express = require('express');
const router = express.Router();
const { Paper } = require('../models');
const { Op } = require('sequelize');

const DEMO_EMAIL = 'demo@demo.com';
const DEMO_PMIDS = ['35100360', '38096902', '29309035', '37924094', '36542723'];

router.get('/', async (req, res) => {
  try {
    const isDemo = req.user?.UserEmail === DEMO_EMAIL;
    console.log(req.user.UserEmail);

    const condition = isDemo
      ? { PMID: { [Op.in]: DEMO_PMIDS } }
      : {};

    const papers = await Paper.findAll({ where: condition });

    res.json(papers);
  } catch (err) {
    console.error('Error fetching papers:', err);
    res.status(500).json({ error: 'Server error', details: err.message });
  }
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
