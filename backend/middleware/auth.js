const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'supersecret';
const THREE_DAYS_IN_MILI_SECONDS = 3 * 24 * 60 * 60 * 1000;
const SEVEN_DAYS_IN_MILI_SECONDS = 7 * 24 * 60 * 60 * 1000;
function authenticateToken(req, res, next) {
    const token = req.cookies.token;

    if (!token) {
        return res.status(401).json({ error: 'Unauthorized: No token provided' });
    }

    try {
        const decoded = jwt.decode(token);

        if (!decoded || !decoded.exp) {
            return res.status(403).json({ error: 'Invalid token' });
        }

        const now = Math.floor(Date.now() / 1000); 
        const timeLeft = decoded.exp - now;

        const verified = jwt.verify(token, JWT_SECRET);
        req.user = verified;

        if (timeLeft < THREE_DAYS_IN_MILI_SECONDS) {
            const newToken = jwt.sign(
                { UserEmail: verified.UserEmail, UserKey: verified.UserKey },
                JWT_SECRET,
                { expiresIn: SEVEN_DAYS_IN_MILI_SECONDS }
            );

            res.cookie('token', newToken, {
                httpOnly: true,
                maxAge: SEVEN_DAYS_IN_MILI_SECONDS, 
                secure: process.env.NODE_ENV === 'production',
                sameSite: 'Lax'
            });
        }

        next();
    } catch (err) {
        return res.status(403).json({ error: 'Invalid or expired token' });
    }
}

module.exports = authenticateToken;