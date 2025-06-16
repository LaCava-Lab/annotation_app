const express = require("express")
const router = express.Router()
const {SessionState} = require("../models")

router.get('/:id', async (req, res) => {
  try {
    const session = await SessionState.findByPk(req.params.id);
    if (!session) return res.status(404).json({ error: "Not found" });
    res.json(session);
  } catch (err) {
    res.status(500).json({ error: "Server error", details: err.message });
  }
});
router.post('/', async (req, res) => {
  try {
    const result = await SessionState.create(req.body);
    res.status(201).json(result);
  } catch (err) {
    res.status(400).json({ error: 'Insert error', details: err.message });
  }
});

module.exports = router;