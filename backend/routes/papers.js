const express = require('express');
const router = express.Router();
const { Paper } = require('../models');

router.get('/', async (req, res) => {
  const papers = await Paper.findAll();
  res.json(papers);
});

module.exports = router;
