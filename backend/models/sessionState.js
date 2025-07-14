module.exports = (sequelize, DataTypes) => {
  return sequelize.define('SessionState', {
    SessionID: { type: DataTypes.STRING, primaryKey: true },
    userID: DataTypes.STRING,
    PMID: DataTypes.STRING,
    SessionStatus: DataTypes.STRING,
    json_state: DataTypes.STRING, // should be a json binary
    q1: DataTypes.STRING,
    q1a: DataTypes.STRING,
    q1b: DataTypes.STRING,
    q1c: DataTypes.STRING,
    q2: DataTypes.STRING,
    q3: DataTypes.STRING
  }, { tableName: 'sessionstate', timestamps: false });
};
