module.exports = (sequelize, DataTypes) => {
  return sequelize.define('User', {
    userID: {
      type: DataTypes.STRING,
      primaryKey: true
    },
    email: {
      type: DataTypes.STRING
    },
    noPapers: {
      type: DataTypes.STRING
    },
    papersCompleted: {
      type: DataTypes.INTEGER
    },
    paperInProgress: {
      type: DataTypes.STRING
    },
    otherInfo: {
      type: DataTypes.TEXT
    },
    loginTimestamps: {
      type: DataTypes.TEXT
    }
  }, {
    tableName: 'users',
    timestamps: false
  });
};
