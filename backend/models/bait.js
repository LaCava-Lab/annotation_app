module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Bait', {
    BaitID: { type: DataTypes.STRING, primaryKey: true },
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
    species_name: DataTypes.STRING,
    species_name_section: DataTypes.STRING,
    species_name_start: DataTypes.INTEGER,
    species_name_end: DataTypes.INTEGER,
    species_name_alt: DataTypes.STRING,
    isControl: DataTypes.STRING,
    bait_type: DataTypes.STRING
  }, { tableName: 'baits', timestamps: false });
};
