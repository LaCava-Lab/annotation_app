module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Interactor', {
    InteractorID: { type: DataTypes.STRING, primaryKey: true },
    BaitID: {
      type: DataTypes.STRING,
      allowNull: false,
      references: { model: 'baits', key: 'BaitID' },
      onDelete: 'CASCADE'
    },

    ExperimentID: {
      type: DataTypes.STRING,
      allowNull: true,
      references: { model: 'experiments', key: 'ExperimentID' },
      onDelete: 'SET NULL'
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
    type: DataTypes.STRING
  }, { tableName: 'interactors', timestamps: false });
};
