const express = require('express');
const router = express.Router();
const { Paper } = require('../models');

const DEMO_EMAIL = 'demo@demo.com';
const DEMO_PMIDS = ['37795087', '29309035', '22589133', '20021644', '20054825'];

router.get('/', async (req, res) => {
  try {
    const isDemo = req.user?.UserEmail === DEMO_EMAIL;
    console.log(req.user.UserEmail)
    const papers = await Paper.findAll({
      where: isDemo ? { PMID: DEMO_PMIDS } : {},
    });

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
