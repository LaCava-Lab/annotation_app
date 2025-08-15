const request = require('supertest');
const app = require('../app');
const db = require('../models');
const assert = require('node:assert/strict');
const { test, after, beforeEach, describe } = require('node:test');

let authCookie;
let userKey;

beforeEach(async () => {
  await db.sequelize.sync({ force: true });
  // Register and login user, store cookie and userKey for use in tests
  await request(app).post('/auth/signup').send({
    UserEmail: 'test@example.com',
    UserPIN: 1234
  });

  const loginRes = await request(app).post('/auth/login').send({
    UserEmail: 'test@example.com',
    UserPIN: 1234
  });

  // For JWT in cookie (httpOnly), extract cookie header
  authCookie = loginRes.headers['set-cookie'] && loginRes.headers['set-cookie'][0];
  userKey = loginRes.body.userKey || loginRes.body.UserKey || 'U0000';
});

after(async () => {
  await db.sequelize.close();
});

describe('Auth Routes', () => {
  test('POST /auth/signup should register user', async () => {
    const response = await request(app).post('/auth/signup').send({
      UserEmail: 'another@example.com',
      UserPIN: 5678
    });

    assert.strictEqual(response.statusCode, 201);
    assert.strictEqual(response.body.UserEmail, 'another@example.com');
  });

  test('POST /auth/login should return a token', async () => {
    const response = await request(app).post('/auth/login').send({
      UserEmail: 'test@example.com',
      UserPIN: 1234
    });

    assert.strictEqual(response.statusCode, 200);
    assert.ok(response.body.token, 'Token should be present in response');
  });

  test('POST /auth/logout should succeed', async () => {
    const response = await request(app)
      .post('/auth/logout')
      .set('Cookie', authCookie);
    assert.strictEqual(response.statusCode, 200);
    assert.ok(response.body.message);
  });
});

describe('User Routes', () => {
  test('GET /users should return users', async () => {
    const res = await request(app).get('/users').set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(Array.isArray(res.body));
  });

  test('GET /users/me?userKey=...', async () => {
    const res = await request(app)
      .get(`/users/me?userKey=${userKey}`)
      .set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(res.body.UserKey === userKey || res.body.userKey === userKey);
  });

  test('POST /users/set_current_pmid', async () => {
    const res = await request(app)
      .post('/users/set_current_pmid')
      .set('Cookie', authCookie)
      .send({ userKey, pmid: '123456' });
    assert.strictEqual(res.statusCode, 200);
    assert.ok(res.body.CurrentPMID === '123456' || res.body.currentPMID === '123456');
  });

  test('POST /users/add_completed', async () => {
    const res = await request(app)
      .post('/users/add_completed')
      .set('Cookie', authCookie)
      .send({ userKey, pmid: '123456' });
    assert.strictEqual(res.statusCode, 200);
    assert.ok(
      (res.body.CompletedPMIDs || res.body.completedPMIDs || []).includes('123456')
    );
  });

  test('POST /users/add_abandoned', async () => {
    const res = await request(app)
      .post('/users/add_abandoned')
      .set('Cookie', authCookie)
      .send({ userKey, pmid: '123456' });
    assert.strictEqual(res.statusCode, 200);
    assert.ok(
      (res.body.AbandonedPMIDs || res.body.abandonedPMIDs || []).includes('123456')
    );
  });

  test('POST /users/set_abandon_limit', async () => {
    const res = await request(app)
      .post('/users/set_abandon_limit')
      .set('Cookie', authCookie)
      .send({ userKey });
    assert.strictEqual(res.statusCode, 200);
    assert.ok(res.body.AbandonLimit !== undefined || res.body.abandonLimit !== undefined);
  });
});

describe('Paper Routes', () => {
  test('GET /papers should return papers', async () => {
    const res = await request(app).get('/papers').set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(Array.isArray(res.body));
  });

  test('GET /papers/:pmid should return a paper or 404', async () => {
    const res = await request(app).get('/papers/10190907').set('Cookie', authCookie);
    assert.ok([200, 404].includes(res.statusCode));
  });
});

describe('FullText Routes', () => {
  test('GET /fulltext?filename=... should return fulltext or 404', async () => {
    const res = await request(app)
      .get('/fulltext?filename=38096902')
      .set('Cookie', authCookie);
    assert.ok([200, 404].includes(res.statusCode));
  });
});

describe('Session State Routes', () => {

  test('GET /sessions/by_user_pmid?userKey=...&pmid=...', async () => {
    const res = await request(app)
      .get('/sessions/by_user_pmid?userKey=U0000&pmid=10190907')
      .set('Cookie', authCookie);
    assert.ok([200, 404].includes(res.statusCode));
  });

  test('GET /sessions/:id should return a session or 404', async () => {
    const res = await request(app)
      .get('/sessions/session123')
      .set('Cookie', authCookie);
    assert.ok([200, 404].includes(res.statusCode));
  });
});

describe('Experiment Routes', () => {
  test('GET /experiments should return experiments', async () => {
    const res = await request(app).get('/experiments').set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(Array.isArray(res.body));
  });

});

describe('Solution Routes', () => {
  test('GET /solutions should return solutions', async () => {
    const res = await request(app).get('/solutions').set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(Array.isArray(res.body));
  });


});

describe('Bait Routes', () => {
  test('GET /baits should return baits', async () => {
    const res = await request(app).get('/baits').set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(Array.isArray(res.body));
  });


});

describe('Interactor Routes', () => {
  test('GET /interactors should return interactors', async () => {
    const res = await request(app).get('/interactors').set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(Array.isArray(res.body));
  });

});

describe('Chemistry Routes', () => {
  test('GET /chemistrys should return chemistry records', async () => {
    const res = await request(app).get('/chemistrys').set('Cookie', authCookie);
    assert.strictEqual(res.statusCode, 200);
    assert.ok(Array.isArray(res.body));
  });

});