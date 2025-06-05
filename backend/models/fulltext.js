module.exports = (sequelize, DataTypes) => {
  return sequelize.define('FullText', {
    EntryID: { type: DataTypes.STRING, primaryKey: true },
    PMID: DataTypes.STRING,
    Section: DataTypes.STRING,
    Type: DataTypes.TEXT,
    TextValue: DataTypes.TEXT
  }, {
    tableName: 'fulltexts',
    timestamps: false
  });
};
