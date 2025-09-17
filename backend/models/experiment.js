module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Experiment', {
    ExperimentID: { type: DataTypes.STRING, primaryKey: true },
    SessionID: {
      type: DataTypes.STRING,
      allowNull: false,
      references: { model: 'sessionstate', key: 'SessionID' },
      onDelete: 'CASCADE'
    },
    name: DataTypes.STRING,
    name_section: DataTypes.STRING,
    name_start: DataTypes.INTEGER,
    name_end: DataTypes.INTEGER,
    name_alt: DataTypes.STRING,
    type: DataTypes.STRING
  }, { tableName: 'experiments', timestamps: false });
};
