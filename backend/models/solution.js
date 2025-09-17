module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Solution', {
    SolutionID: { type: DataTypes.STRING, primaryKey: true },
    ExperimentID: {
      type: DataTypes.STRING,
      allowNull: false,
      references: { model: 'experiments', key: 'ExperimentID' },
      onDelete: 'CASCADE'
    },
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
