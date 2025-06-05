module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Paper', {
  PMID: { type: DataTypes.STRING, primaryKey: true },
  DOI_URL: DataTypes.TEXT,
  Title: DataTypes.TEXT,
  Authors: DataTypes.ARRAY(DataTypes.STRING),
  Year: DataTypes.INTEGER,
  Journal: DataTypes.STRING,
  Volume: DataTypes.STRING,
  Issue: DataTypes.STRING,
  Pages: DataTypes.STRING,
  Abstract: DataTypes.TEXT,
  UsersCompleted: DataTypes.ARRAY(DataTypes.STRING),
  UsersCurrent: DataTypes.ARRAY(DataTypes.STRING)
}, { tableName: 'papers', timestamps: false });
};
