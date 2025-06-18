const express = require('express');
const router = express.Router();
const { User } = require('../models');

// Get all users
router.get('/', async (req, res) => {
  const users = await User.findAll();
  res.json(users);
});

// Get user by userKey
router.get('/me', async (req, res) => {
  const userKey = req.query.userKey;
  if (!userKey) return res.status(400).json({ error: "userKey required" });
  const user = await User.findOne({ where: { UserKey: userKey } });
  if (!user) return res.status(404).json({ error: "User not found" });
  res.json(user);
});

// Set current paper in progress
router.post('/set_current_pmid', async (req, res) => {
  const { userKey, pmid } = req.body;
  if (!userKey) return res.status(400).json({ error: "userKey required" });
  try {
    const user = await User.findOne({ where: { UserKey: userKey } });
    if (!user) return res.status(404).json({ error: "User not found" });
    user.CurrentPMID = pmid; // This will set to null if pmid is null
    await user.save();
    // Return updated user
    const updatedUser = await User.findOne({ where: { UserKey: userKey } });
    res.json(updatedUser);
  } catch (err) {
    console.error("Error in /set_current_pmid:", err);
    res.status(500).json({ error: "Database error" });
  }
});

// Helper for updating PMIDs array fields
async function addToUserPMIDArrayField(userKey, pmid, fieldName) {
  if (!userKey || !pmid) throw { status: 400, message: "userKey and pmid required" };
  // Fetch the latest user from DB right before updating
  const user = await User.findOne({ where: { UserKey: userKey } });
  if (!user) throw { status: 404, message: "User not found" };

  // Fetch the latest array from DB again to avoid race condition
  const freshUser = await User.findOne({ where: { UserKey: userKey } });
  let arr = freshUser[fieldName] || [];
  const pmidStr = String(pmid);
  if (!arr.includes(pmidStr)) arr.push(pmidStr);
  user[fieldName] = arr;
  await user.save();

  // Return updated user
  return await User.findOne({ where: { UserKey: userKey } });
}

// Add completed paper
router.post('/add_completed', async (req, res) => {
  const { userKey, pmid } = req.body;
  try {
    const updatedUser = await addToUserPMIDArrayField(userKey, pmid, "CompletedPMIDs");
    res.json(updatedUser);
  } catch (err) {
    console.error("Error in /add_completed:", err);
    res.status(err.status || 500).json({ error: err.message || "Database error" });
  }
});

// Add abandoned paper
router.post('/add_abandoned', async (req, res) => {
  const { userKey, pmid } = req.body;
  try {
    const updatedUser = await addToUserPMIDArrayField(userKey, pmid, "AbandonedPMIDs");
    res.json(updatedUser);
  } catch (err) {
    console.error("Error in /add_abandoned:", err);
    res.status(err.status || 500).json({ error: err.message || "Database error" });
  }
});


module.exports = router;