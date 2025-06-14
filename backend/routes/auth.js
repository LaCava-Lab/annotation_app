const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { User } = require('../models');
const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'supersecret';

function createToken(userKey) {
  return jwt.sign({ userKey }, JWT_SECRET, { expiresIn: '1d' });
}

async function generateUserKey() {
  const lastUser = await User.findOne({
    order: [['UserKey', 'DESC']]
  });

  if (!lastUser || !lastUser.UserKey) return 'U0000';

  const lastNumber = parseInt(lastUser.UserKey.slice(1), 10);
  const nextNumber = (lastNumber + 1).toString().padStart(4, '0');
  return `U${nextNumber}`;
}

router.post('/signup', async (req, res) => {
  const { UserEmail, UserPIN } = req.body;
  if (!UserEmail || !UserPIN) return res.status(400).json({ error: 'Missing fields' });

  try {
    const existing = await User.findOne({ where: { UserEmail } });
    if (existing) return res.status(400).json({ error: 'Email already registered' });

    const hashedPin = await bcrypt.hash(UserPIN.toString(), 10);
    const newUserKey = await generateUserKey();

    await User.create({
      UserEmail,
      UserPIN: hashedPin,
      UserKey: newUserKey,
      AbandonLimit: false,
      AbandonedPMIDs: [],
      CompletedPMIDs: [],
      AbandonedSessionID: [],
      ClosedSessionID: []
    });

    res.status(201).json({ message: 'User created', userKey: newUserKey });
  } catch (err) {
    console.error('Signup error:', err); 
    res.status(500).json({ error: err.message });
  }
});

router.post('/login', async (req, res) => {
  const { UserEmail, UserPIN } = req.body;
  const user = await User.findOne({ where: { UserEmail } });
  if (!user) return res.status(401).json({ error: 'Invalid email or PIN' });

  const match = await bcrypt.compare(UserPIN.toString(), user.UserPIN);
  if (!match) return res.status(401).json({ error: 'Invalid email or PIN' });

  const token = createToken(user.UserKey);
  res.cookie('token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000
  });

  // Send userKey and token in the response
  res.json({ message: 'Logged in', userKey: user.UserKey, token });
});

router.post('/logout', (req, res) => {
  res.clearCookie('token', {
    httpOnly: true,
    sameSite: 'strict',
    secure: process.env.NODE_ENV === 'production'
  });
  res.json({ message: 'Logged out' });
});

module.exports = router;
