module.exports = (sequelize, DataTypes) => {
  return sequelize.define('SessionState', {
    SessionID: { type: DataTypes.STRING, primaryKey: true },
    userID: {
      type: DataTypes.STRING,
      allowNull: false,
      references: { model: 'users', key: 'UserKey' },
      onDelete: 'CASCADE'
    },

    PMID: {
      type: DataTypes.STRING,
      allowNull: false,
      references: { model: 'papers', key: 'PMID' },
      onDelete: 'CASCADE'
    },
    SessionStatus: DataTypes.STRING,
    json_state: DataTypes.TEXT,
    q1: DataTypes.STRING,
    q1a: DataTypes.STRING,
    q1b: DataTypes.STRING,
    q1c: DataTypes.STRING,
    q2: DataTypes.STRING,
    q3: DataTypes.STRING
  }, { tableName: 'sessionstate', timestamps: false });
};
