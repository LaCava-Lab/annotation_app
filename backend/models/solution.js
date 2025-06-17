module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Solution', {
    SolutionID: { type: DataTypes.STRING, primaryKey: true },
    ExperimentID: DataTypes.STRING,
    name: DataTypes.STRING,
    name_section: DataTypes.STRING,
    name_start: DataTypes.INTEGER,
    name_end: DataTypes.INTEGER,
    name_alt: DataTypes.STRING,
    type: DataTypes.STRING,
    temp: DataTypes.STRING,
    time: DataTypes.STRING,
    ph: DataTypes.INTEGER
  }, { tableName: 'solutions', timestamps: false });
};
