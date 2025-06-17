const express = require('express');
const router = express.Router();
const {Interactor} = require('../models');

router.get('/', async (req, res) => {
  try {
    const result = await Interactor.findAll();
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'Server error', details: err.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const result = await Interactor.bulkCreate(req.body);
    res.status(201).json(result);
  } catch (err) {
    res.status(400).json({ error: 'Bulk insert error', details: err.message });
  }
});

module.exports = router;