const { Sequelize } = require('sequelize');
require('dotenv').config();

const sequelize = new Sequelize(process.env.DB_URL, {
  dialect: 'postgres',
  protocol: 'postgres',
  dialectOptions: {
    ssl: { require: true, rejectUnauthorized: false }
  }
});

const db = {};
db.sequelize = sequelize;
db.Sequelize = Sequelize;
db.User = require('./user')(sequelize, Sequelize);
db.Paper = require('./paper')(sequelize, Sequelize);
db.FullText = require('./fulltext')(sequelize, Sequelize);
db.SessionState = require('./sessionState')(sequelize, Sequelize);
db.Experiment = require('./experiment')(sequelize, Sequelize);
db.Solution = require('./solution')(sequelize, Sequelize);
db.Bait = require('./bait')(sequelize, Sequelize);
db.Interactor = require('./interactor')(sequelize, Sequelize);
db.Chemistry = require('./chemistry')(sequelize, Sequelize);
module.exports = db;
