module.exports = (sequelize, DataTypes) => {
  return sequelize.define('FullText', {
    EntryID: { type: DataTypes.STRING, primaryKey: true },
    PMID: {
      type: DataTypes.STRING,
      allowNull: false,
      references: { model: 'papers', key: 'PMID' },
      onDelete: 'CASCADE'
    },
    PMCID: DataTypes.STRING,
    Section: DataTypes.STRING,
    Type: DataTypes.TEXT,
    TextValue: DataTypes.TEXT
  }, {
    tableName: 'fulltexts',
    timestamps: false
  });
};
