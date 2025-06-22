const request = require('supertest');
const app = require('../app');
const db = require('../models');
const assert = require('node:assert/strict');
const { test, after, beforeEach, describe } = require('node:test');

beforeEach(async () => {
  await db.sequelize.sync({ force: true }); // Clean test DB
});

after(async () => {
  await db.sequelize.close();
});

describe('Auth Routes', () => {
  test('POST /auth/signup should register user', async () => {
    const response = await request(app).post('/auth/signup').send({
      UserEmail: 'test@example.com',
      UserPIN: 1234
    });

    assert.strictEqual(response.statusCode, 201);
    console.log(response.body);
    assert.strictEqual(response.body.UserEmail, 'test@example.com');
  });

  test('POST /auth/login should return a token', async () => {
    await request(app).post('/auth/signup').send({
      UserEmail: 'test@example.com',
      UserPIN: 1234
    });

    const response = await request(app).post('/auth/login').send({
      UserEmail: 'test@example.com',
      UserPIN: 1234
    });

    assert.strictEqual(response.statusCode, 200);
    assert.ok(response.body.token, 'Token should be present in response');
  });
});
