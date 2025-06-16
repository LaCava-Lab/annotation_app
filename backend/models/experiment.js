module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Experiment', {
    ExperimentID: { type: DataTypes.STRING, primaryKey: true },
    SessionID: DataTypes.STRING,
    name: DataTypes.STRING,
    name_section: DataTypes.STRING,
    name_start: DataTypes.INTEGER,
    name_end: DataTypes.INTEGER,
    name_alt: DataTypes.STRING,
    type: DataTypes.STRING
  }, { tableName: 'experiments', timestamps: false });
};
