module.exports = (sequelize, DataTypes) => {
  return sequelize.define('SessionState', {
    SessionID: { type: DataTypes.STRING, primaryKey: true },
    userID: DataTypes.STRING,
    PMID: DataTypes.STRING,
    SessionStatus: DataTypes.STRING,
    json_state: DataTypes.STRING // should be a json binary
  }, { tableName: 'sessionstate', timestamps: false });
};
