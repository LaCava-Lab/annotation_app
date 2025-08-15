process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const express = require('express');
const app = express();
require('dotenv').config();
const path = require('path');
const morgan = require('morgan');
const chalk = require('chalk');
const authenticateToken = require('./middleware/auth');
const userRoutes = require('./routes/users');
const paperRoutes = require('./routes/papers');
const authRoutes = require('./routes/auth');
const fulltextRoutes = require('./routes/fulltexts');
const sessionRoutes = require('./routes/sessions');
const experimentRoutes = require('./routes/experiments');
const solutionRoutes = require('./routes/solutions');
const baitRoutes = require('./routes/baits');
const interactorRoutes = require('./routes/interactors');
const chemistryRoutes = require('./routes/chemistrys');
const cookieParser = require('cookie-parser');

app.use(express.json());
app.use(cookieParser());
app.use(morgan((tokens, req, res) => {
  let log = [
    chalk.cyan(tokens.method(req, res)),                
    chalk.yellow(tokens.url(req, res)),                 
    chalk.green(tokens.status(req, res)),               
    chalk.magenta(tokens['response-time'](req, res) + ' ms')
  ].join(' ');

  if (req.body && Object.keys(req.body).length > 0) {
    log += '\n' + chalk.white(`Body: ${JSON.stringify(req.body)}`);
  }

  return log;
}));
app.use('/users', userRoutes);
app.use('/papers', authenticateToken, paperRoutes);
app.use('/auth', authRoutes);
app.use('/fulltext', authenticateToken, fulltextRoutes);
app.use('/sessions', authenticateToken, sessionRoutes);
app.use('/experiments', authenticateToken, experimentRoutes);
app.use('/solutions', authenticateToken, solutionRoutes);
app.use('/baits', authenticateToken, baitRoutes);
app.use('/interactors', authenticateToken, interactorRoutes);
app.use('/chemistrys', authenticateToken, chemistryRoutes);
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'api-docs.html'));
});
module.exports = app;