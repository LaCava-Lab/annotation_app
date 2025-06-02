const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { User } = require('../models');
const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'supersecret';

function createToken(userID) {
  return jwt.sign({ userID }, JWT_SECRET, { expiresIn: '1d' });
}

router.post('/signup', async (req, res) => {
  const { email, password, userID } = req.body;
  if (!email || !password || !userID) return res.status(400).json({ error: 'Missing fields' });

  const existing = await User.findOne({ where: { email } });
  if (existing) return res.status(400).json({ error: 'Email already registered' });

  const hash = await bcrypt.hash(password, 10);
  await User.create({ email, password: hash, userID });

  res.status(201).json({ message: 'User created' });
});

router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ where: { email } });
  if (!user) return res.status(401).json({ error: 'Invalid email or password' });

  const match = await bcrypt.compare(password, user.password);
  if (!match) return res.status(401).json({ error: 'Invalid email or password' });

  const token = createToken(user.userID);
  res.cookie('token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000 * 7
  });

  res.json({ message: 'Logged in' });
});

module.exports = router;
