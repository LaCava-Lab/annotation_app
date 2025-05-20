module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Paper', {
    PMID: {
      type: DataTypes.STRING,
      primaryKey: true
    },
    DOI: {
      type: DataTypes.STRING
    },
    Title: {
      type: DataTypes.TEXT
    },
    Authors: {
      type: DataTypes.TEXT
    },
    Abstract: {
      type: DataTypes.TEXT
    },
    status_1: {
      type: DataTypes.STRING
    },
    user_1: {
      type: DataTypes.STRING
    },
    status_2: {
      type: DataTypes.STRING
    },
    user_2: {
      type: DataTypes.STRING
    }
  }, {
    tableName: 'papers',
    timestamps: false
  });
};
