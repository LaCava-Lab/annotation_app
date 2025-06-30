const express = require("express")
const router = express.Router()
const { SessionState } = require("../models")

// Fetch session state by userKey and pmid (latest open session)
router.get('/by_user_pmid', async (req, res) => {
  const { userKey, pmid } = req.query;
  if (!userKey || !pmid) {
    return res.status(400).json({ error: "userKey and pmid are required" });
  }
  try {
    const session = await SessionState.findOne({
      where: { userID: userKey, PMID: pmid, SessionStatus: "open" }
    });
    if (session) {
      res.json({ json_state: session.json_state });
    } else {
      res.status(404).json({ error: "Session not found" });
    }
  } catch (err) {
    res.status(500).json({ error: "Database error" });
  }
});

// Get session by SessionID
router.get('/:id', async (req, res) => {
  try {
    const session = await SessionState.findByPk(req.params.id);
    if (!session) return res.status(404).json({ error: "Not found" });
    res.json(session);
  } catch (err) {
    res.status(500).json({ error: "Server error", details: err.message });
  }
});

// Create new session
router.post('/', async (req, res) => {
  try {
    const result = await SessionState.create(req.body);
    res.status(201).json(result);
  } catch (err) {
    res.status(400).json({ error: 'Insert error', details: err.message });
  }
});

// Save or update session state for a user and pmid
router.post('/save', async (req, res) => {
  const { userKey, pmid, json_state, q1, q1a, q1b, q1c, q2, q3 } = req.body;
  if (!userKey || !pmid || !json_state) {
    return res.status(400).json({ error: "userKey, pmid, and json_state are required" });
  }

  try {
    // Find an open session for this user and pmid
    let session = await SessionState.findOne({ where: { userID: userKey, PMID: pmid, SessionStatus: "open" } });
    
    if (session) {
      // Update only the json_state, preserving the question answers
      session.json_state = json_state;
      await session.save();
      res.json({ success: true, updated: true });
    } else {
      // Create new session state with all fields
      await SessionState.create({
        SessionID: `${userKey}_${pmid}_${Date.now()}`,
        userID: userKey,
        PMID: pmid,
        SessionStatus: "open",
        json_state: json_state,
        q1: q1 || null,
        q1a: q1a || null,
        q1b: q1b || null,
        q1c: q1c || null,
        q2: q2 || null,
        q3: q3 || null
      });
      res.json({ success: true, created: true });
    }
  } catch (err) {
    console.error("Error saving session state:", err);
    res.status(500).json({ error: "Database error" });
  }
});


module.exports = router;