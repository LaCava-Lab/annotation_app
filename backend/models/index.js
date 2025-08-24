const { Sequelize } = require('sequelize');
require('dotenv').config();

const isTest = process.env.NODE_ENV === 'test';

const sequelize = new Sequelize(isTest ? process.env.TEST_DB_URL : process.env.DB_URL, {
  dialect: 'postgres',
  protocol: 'postgres',
  logging: false,
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

db.Paper.hasMany(db.SessionState, { foreignKey: 'PMID' });
db.SessionState.belongsTo(db.Paper, { foreignKey: 'PMID' });

db.User.hasMany(db.SessionState, { foreignKey: 'userID' });
db.SessionState.belongsTo(db.User, { foreignKey: 'userID' });

db.SessionState.hasMany(db.Experiment, { foreignKey: 'SessionID' });
db.Experiment.belongsTo(db.SessionState, { foreignKey: 'SessionID' });

db.Experiment.hasMany(db.Solution, { foreignKey: 'ExperimentID' });
db.Solution.belongsTo(db.Experiment, { foreignKey: 'ExperimentID' });

db.Experiment.hasMany(db.Bait, { foreignKey: 'ExperimentID' });
db.Bait.belongsTo(db.Experiment, { foreignKey: 'ExperimentID' });

db.Solution.hasMany(db.Chemistry, { foreignKey: 'SolutionID' });
db.Chemistry.belongsTo(db.Solution, { foreignKey: 'SolutionID' });

db.Bait.hasMany(db.Interactor, { foreignKey: 'BaitID' });
db.Interactor.belongsTo(db.Bait, { foreignKey: 'BaitID' });

db.Experiment.hasMany(db.Interactor, { foreignKey: 'ExperimentID' });
db.Interactor.belongsTo(db.Experiment, { foreignKey: 'ExperimentID' });

module.exports = db;
