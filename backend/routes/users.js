const express = require('express');
const router = express.Router();
const { User } = require('../models');

router.get('/', async (req, res) => {
  const users = await User.findAll();
  res.json(users);
});


// Get user by email
router.get('/me', async (req, res) => {
  const email = req.query.email;
  if (!email) return res.status(400).json({ error: "Email required" });
  const user = await User.findOne({ where: { UserEmail: email } });
  if (!user) return res.status(404).json({ error: "User not found" });
  res.json(user);
});
// Set current paper in progress
router.post('/set_current_pmid', async (req, res) => {
  const { email, pmid } = req.body;
  if (!email) return res.status(400).json({ error: "Email required" });
  try {
    const user = await User.findOne({ where: { UserEmail: email } });
    if (!user) return res.status(404).json({ error: "User not found" });
    user.CurrentPMID = pmid; // This will set to null if pmid is null
    await user.save();
    // Return updated user
    const updatedUser = await User.findOne({ where: { UserEmail: email } });
    res.json(updatedUser);
  } catch (err) {
    console.error("Error in /set_current_pmid:", err);
    res.status(500).json({ error: "Database error" });
  }
});

router.post('/add_completed', async (req, res) => {
  const { email, pmid } = req.body;
  console.log("add_completed called with:", email, pmid);
  if (!email || !pmid) return res.status(400).json({ error: "Email and pmid required" });
  try {
    // Fetch the latest user from DB right before updating
    const user = await User.findOne({ where: { UserEmail: email } });
    if (!user) return res.status(404).json({ error: 'User not found' });

    // Fetch the latest CompletedPMIDs from DB again to avoid race condition
    const freshUser = await User.findOne({ where: { UserEmail: email } });
    let completed = freshUser.CompletedPMIDs || [];
    const pmidStr = String(pmid);
    if (!completed.includes(pmidStr)) completed.push(pmidStr);
    user.CompletedPMIDs = completed;

    console.log("Before save, CompletedPMIDs:", user.CompletedPMIDs);
    await user.save();

    // Fetch from DB after save
    const updatedUser = await User.findOne({ where: { UserEmail: email } });
    console.log("After save, CompletedPMIDs in DB:", updatedUser.CompletedPMIDs);
    res.json(updatedUser);
  } catch (err) {
    console.error("Error in /add_completed:", err);
    res.status(500).json({ error: "Database error" });
  }
});

// Add abandoned paper
router.post('/add_abandoned', async (req, res) => {
  const { email, pmid } = req.body;
  if (!email || !pmid) return res.status(400).json({ error: "Email and pmid required" });
  try {
    // Fetch the latest user from DB right before updating
    const user = await User.findOne({ where: { UserEmail: email } });
    if (!user) return res.status(404).json({ error: "User not found" });

    // Fetch the latest AbandonedPMIDs from DB again to avoid race condition
    const freshUser = await User.findOne({ where: { UserEmail: email } });
    let abandoned = freshUser.AbandonedPMIDs || [];
    const pmidStr = String(pmid); // Ensure pmid is a string
    if (!abandoned.includes(pmidStr)) abandoned.push(pmidStr);
    user.AbandonedPMIDs = abandoned;
    await user.save();

    // Return updated user
    const updatedUser = await User.findOne({ where: { UserEmail: email } });
    res.json(updatedUser);
  } catch (err) {
    console.error("Error in /add_abandoned:", err);
    res.status(500).json({ error: "Database error" });
  }
});

module.exports = router;
