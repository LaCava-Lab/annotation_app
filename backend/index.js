process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const express = require('express');
const app = express();
const db = require('./models');
require('dotenv').config();
const port = process.env.PORT || 3000;
const authenticateToken = require('./middleware/auth');
const userRoutes = require('./routes/users');
const paperRoutes = require('./routes/papers');
const authRoutes = require('./routes/auth');
const cookieParser = require('cookie-parser');

app.use(express.json());
app.use(cookieParser());
app.use('/users', userRoutes);
app.use('/papers', authenticateToken, paperRoutes);
app.use('/auth', authRoutes);
db.sequelize.sync().then(() => {
  app.listen(port, () => {
    console.log('Server running on port 3000');
  });
});
