module.exports = (sequelize, DataTypes) => {
  return sequelize.define('User', {
  UserKey: { type: DataTypes.STRING, primaryKey: true },
  UserPIN: DataTypes.STRING,
  UserEmail: DataTypes.STRING,
  AbandonLimit: DataTypes.BOOLEAN,
  CurrentPMID: DataTypes.STRING,
  AbandonedPMIDs: DataTypes.ARRAY(DataTypes.STRING),
  CompletedPMIDs: DataTypes.ARRAY(DataTypes.STRING),
  OpenSessionID: DataTypes.STRING,
  AbandonedSessionID: DataTypes.ARRAY(DataTypes.STRING),
  ClosedSessionID: DataTypes.ARRAY(DataTypes.STRING),
  password: DataTypes.STRING
}, { tableName: 'users', timestamps: false });
};
