const app = require('./app');
const db = require('./models');
const port = process.env.PORT || 3000;
db.sequelize.sync({}).then(() => {
  app.listen(port, () => {
    console.log(`Server running on port ${port}`);
  });
});
