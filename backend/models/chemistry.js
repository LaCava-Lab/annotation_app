module.exports = (sequelize, DataTypes) => {
  return sequelize.define('Chemistry', {
    ChemistryID: { type: DataTypes.STRING, primaryKey: true },
    SolutionID: {
      type: DataTypes.STRING,
      allowNull: false,
      references: { model: 'solutions', key: 'SolutionID' },
      onDelete: 'CASCADE'
    },

    name: DataTypes.STRING,
    name_section: DataTypes.STRING,
    name_start: DataTypes.INTEGER,
    name_end: DataTypes.INTEGER,
    name_alt: DataTypes.STRING,

    concentration_name: DataTypes.STRING,
    concentration_name_section: DataTypes.STRING,
    concentration_name_start: DataTypes.INTEGER,
    concentration_name_end: DataTypes.INTEGER,
    concentration_name_alt: DataTypes.STRING,

    unit_name: DataTypes.STRING,
    unit_name_section: DataTypes.STRING,
    unit_name_start: DataTypes.INTEGER,
    unit_name_end: DataTypes.INTEGER,
    unit_name_alt: DataTypes.STRING,
    
    type: DataTypes.STRING
  }, { tableName: 'chemistry', timestamps: false });
};
