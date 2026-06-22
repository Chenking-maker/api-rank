// ============================================
// API Rank Backend - Cloudflare Workers Entry
// 分享佣金系统后端 API
// ============================================

import { signJWT, verifyJWT, generateShareCode, hashIP, corsHeaders, jsonResponse, errorResponse, getClientIP } from './utils.js';

export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const path = url.pathname;
        const method = request.method;

        // 处理 CORS 预检请求
        if (method === 'OPTIONS') {
            return new Response(null, { status: 204, headers: corsHeaders() });
        }

        try {
            // 路由分发
            if (path === '/api/auth/register' && method === 'POST') {
                return await handleRegister(request, env);
            }
            if (path === '/api/user/profile' && method === 'GET') {
                return await handleGetProfile(request, env);
            }
            if (path === '/api/share/generate' && method === 'POST') {
                return await handleGenerateShareLink(request, env);
            }
            if (path === '/api/finder/remaining' && method === 'GET') {
                return await handleGetRemaining(request, env);
            }
            if (path === '/api/finder/use' && method === 'POST') {
                return await handleUseFinder(request, env);
            }

            // 404
            return errorResponse('Not Found', 404);
        } catch (err) {
            console.error('Unhandled error:', err);
            return errorResponse('Internal Server Error', 500);
        }
    }
};

// ============================================
// 中间件：验证 JWT 并提取用户 ID
// ============================================
async function authenticate(request, env) {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return null;
    }
    const token = authHeader.slice(7);
    const payload = await verifyJWT(token, env.JWT_SECRET);
    return payload ? payload.user_id : null;
}

// ============================================
// POST /api/auth/register
// 匿名注册/登录
// Body: { user_id: string, ref?: string }
// ============================================
async function handleRegister(request, env) {
    const body = await request.json();
    const userId = body.user_id;

    if (!userId || typeof userId !== 'string' || userId.length < 10) {
        return errorResponse('Invalid user_id');
    }

    const ip = getClientIP(request);
    const ipHash = await hashIP(ip);
    const ref = body.ref || null;
    const today = getToday();

    // 检查用户是否已存在
    const existing = await env.DB.prepare('SELECT id FROM users WHERE id = ?').bind(userId).first();

    if (!existing) {
        // 新用户注册
        await env.DB.prepare(
            'INSERT INTO users (id, ip_hash) VALUES (?, ?)'
        ).bind(userId, ipHash).run();

        // 初始化今日限额
        await env.DB.prepare(
            'INSERT OR IGNORE INTO daily_limits (user_id, date, uses, bonus_uses) VALUES (?, ?, 0, 0)'
        ).bind(userId, today).run();

        // 处理推荐关系
        if (ref && ref.length >= 6) {
            await processReferral(env, userId, ref);
        }
    } else {
        // 老用户更新活跃时间
        await env.DB.prepare(
            "UPDATE users SET last_active = datetime('now') WHERE id = ?"
        ).bind(userId).run();

        // 确保今日限额记录存在
        await env.DB.prepare(
            'INSERT OR IGNORE INTO daily_limits (user_id, date, uses, bonus_uses) VALUES (?, ?, 0, 0)'
        ).bind(userId, today).run();
    }

    // 签发 JWT
    const token = await signJWT({ user_id: userId }, env.JWT_SECRET);

    // 获取用户信息
    const user = await env.DB.prepare(
        'SELECT total_finder_uses, total_referrals, total_bonus_uses FROM users WHERE id = ?'
    ).bind(userId).first();

    return jsonResponse({
        token,
        user_id: userId,
        is_new: !existing,
        stats: {
            total_finder_uses: user?.total_finder_uses || 0,
            total_referrals: user?.total_referrals || 0,
            total_bonus_uses: user?.total_bonus_uses || 0,
        }
    });
}

// ============================================
// 处理推荐关系
// ============================================
async function processReferral(env, newUserId, shareCode) {
    // 查找分享码对应的推荐人
    const referrer = await env.DB.prepare(
        'SELECT id FROM users WHERE id = (SELECT user_id FROM finder_usage WHERE source = ? LIMIT 1)'
    ).bind('share_' + shareCode).first();

    // 通过 referrals 表查找（share_code 字段）
    // 先查谁拥有这个分享码
    const shareOwner = await env.DB.prepare(
        'SELECT referrer_id FROM referrals WHERE share_code = ? LIMIT 1'
    ).bind(shareCode).first();

    const referrerId = shareOwner?.referrer_id;

    if (!referrerId || referrerId === newUserId) return;

    // 检查是否已被推荐过
    const alreadyReferred = await env.DB.prepare(
        'SELECT id FROM referrals WHERE referred_id = ?'
    ).bind(newUserId).first();

    if (alreadyReferred) return;

    // 创建推荐记录
    const bonusUses = parseInt(env.REFERRAL_BONUS_USES) || 1;
    await env.DB.prepare(
        'INSERT INTO referrals (referrer_id, referred_id, share_code, bonus_granted) VALUES (?, ?, ?, 0)'
    ).bind(referrerId, newUserId, shareCode).run();

    // 给推荐人发放奖励
    const today = getToday();

    // 更新推荐人统计
    await env.DB.prepare(
        'UPDATE users SET total_referrals = total_referrals + 1, total_bonus_uses = total_bonus_uses + ? WHERE id = ?'
    ).bind(bonusUses, referrerId).run();

    // 更新推荐人今日奖励次数
    await env.DB.prepare(
        'UPDATE daily_limits SET bonus_uses = bonus_uses + ? WHERE user_id = ? AND date = ?'
    ).bind(bonusUses, referrerId, today).run();

    // 如果今日记录不存在则创建
    const dailyExists = await env.DB.prepare(
        'SELECT id FROM daily_limits WHERE user_id = ? AND date = ?'
    ).bind(referrerId, today).first();
    if (!dailyExists) {
        await env.DB.prepare(
            'INSERT INTO daily_limits (user_id, date, uses, bonus_uses) VALUES (?, ?, 0, ?)'
        ).bind(referrerId, today, bonusUses).run();
    }

    // 记录奖励
    await env.DB.prepare(
        'INSERT INTO share_rewards (referrer_id, referred_id, bonus_uses) VALUES (?, ?, ?)'
    ).bind(referrerId, newUserId, bonusUses).run();

    // 标记推荐记录已发放
    await env.DB.prepare(
        'UPDATE referrals SET bonus_granted = 1 WHERE referrer_id = ? AND referred_id = ?'
    ).bind(referrerId, newUserId).run();
}

// ============================================
// GET /api/user/profile
// 获取用户信息 + 佣金统计
// Header: Authorization: Bearer <token>
// ============================================
async function handleGetProfile(request, env) {
    const userId = await authenticate(request, env);
    if (!userId) return errorResponse('Unauthorized', 401);

    const today = getToday();
    const maxDaily = parseInt(env.MAX_DAILY_FINDER_USES) || 3;

    // 获取用户基本信息
    const user = await env.DB.prepare(
        'SELECT total_finder_uses, total_referrals, total_bonus_uses FROM users WHERE id = ?'
    ).bind(userId).first();

    // 获取今日限额
    const daily = await env.DB.prepare(
        'SELECT uses, bonus_uses FROM daily_limits WHERE user_id = ? AND date = ?'
    ).bind(userId, today).first();

    const usedToday = daily?.uses || 0;
    const bonusToday = daily?.bonus_uses || 0;
    const remainingFree = Math.max(0, maxDaily - usedToday);
    const remainingTotal = remainingFree + bonusToday;

    // 获取最近推荐记录
    const recentReferrals = await env.DB.prepare(
        `SELECT sr.created_at, sr.bonus_uses
         FROM share_rewards sr
         WHERE sr.referrer_id = ?
         ORDER BY sr.created_at DESC
         LIMIT 10`
    ).bind(userId).all();

    // 获取用户的分享码（取最新一条推荐记录的 share_code）
    const lastReferral = await env.DB.prepare(
        'SELECT share_code FROM referrals WHERE referrer_id = ? ORDER BY created_at DESC LIMIT 1'
    ).bind(userId).first();

    return jsonResponse({
        user_id: userId,
        stats: {
            total_finder_uses: user?.total_finder_uses || 0,
            total_referrals: user?.total_referrals || 0,
            total_bonus_uses: user?.total_bonus_uses || 0,
        },
        today: {
            used: usedToday,
            bonus: bonusToday,
            remaining_free: remainingFree,
            remaining_total: remainingTotal,
            max_daily: maxDaily,
        },
        share_code: lastReferral?.share_code || null,
        recent_referrals: recentReferrals.results || [],
    });
}

// ============================================
// POST /api/share/generate
// 生成分享链接
// Header: Authorization: Bearer <token>
// ============================================
async function handleGenerateShareLink(request, env) {
    const userId = await authenticate(request, env);
    if (!userId) return errorResponse('Unauthorized', 401);

    // 生成唯一短码
    let shareCode;
    let exists;
    let attempts = 0;

    do {
        shareCode = generateShareCode();
        exists = await env.DB.prepare(
            'SELECT id FROM referrals WHERE share_code = ?'
        ).bind(shareCode).first();
        attempts++;
    } while (exists && attempts < 10);

    if (attempts >= 10) {
        return errorResponse('Failed to generate unique share code', 500);
    }

    // 记录分享码（创建一条自引用记录来"占用"这个码）
    // 实际推荐关系在被推荐人注册时建立
    await env.DB.prepare(
        'INSERT INTO referrals (referrer_id, referred_id, share_code, bonus_granted) VALUES (?, ?, ?, 1)'
    ).bind(userId, userId, shareCode).run();

    const baseUrl = env.BASE_URL || 'https://api-rank-backend.370542303.workers.dev';
    const shareUrl = `${baseUrl}?ref=${shareCode}`;

    return jsonResponse({
        share_code: shareCode,
        share_url: shareUrl,
    });
}

// ============================================
// GET /api/finder/remaining
// 查询剩余查找次数
// Header: Authorization: Bearer <token>
// ============================================
async function handleGetRemaining(request, env) {
    const userId = await authenticate(request, env);
    if (!userId) return errorResponse('Unauthorized', 401);

    const today = getToday();
    const maxDaily = parseInt(env.MAX_DAILY_FINDER_USES) || 3;

    const daily = await env.DB.prepare(
        'SELECT uses, bonus_uses FROM daily_limits WHERE user_id = ? AND date = ?'
    ).bind(userId, today).first();

    const usedToday = daily?.uses || 0;
    const bonusToday = daily?.bonus_uses || 0;
    const remainingFree = Math.max(0, maxDaily - usedToday);
    const remainingTotal = remainingFree + bonusToday;

    return jsonResponse({
        remaining_free: remainingFree,
        remaining_bonus: bonusToday,
        remaining_total: remainingTotal,
        used_today: usedToday,
        max_daily: maxDaily,
    });
}

// ============================================
// POST /api/finder/use
// 消耗查找次数
// Header: Authorization: Bearer <token>
// ============================================
async function handleUseFinder(request, env) {
    const userId = await authenticate(request, env);
    if (!userId) return errorResponse('Unauthorized', 401);

    const today = getToday();
    const maxDaily = parseInt(env.MAX_DAILY_FINDER_USES) || 3;

    // 获取或创建今日限额记录
    let daily = await env.DB.prepare(
        'SELECT uses, bonus_uses FROM daily_limits WHERE user_id = ? AND date = ?'
    ).bind(userId, today).first();

    if (!daily) {
        await env.DB.prepare(
            'INSERT OR IGNORE INTO daily_limits (user_id, date, uses, bonus_uses) VALUES (?, ?, 0, 0)'
        ).bind(userId, today).run();
        daily = { uses: 0, bonus_uses: 0 };
    }

    const remainingFree = Math.max(0, maxDaily - daily.uses);
    const remainingTotal = remainingFree + daily.bonus_uses;

    if (remainingTotal <= 0) {
        return errorResponse('No remaining uses today', 429);
    }

    // 判断使用免费次数还是奖励次数
    let source = 'free';
    if (remainingFree > 0) {
        await env.DB.prepare(
            'UPDATE daily_limits SET uses = uses + 1 WHERE user_id = ? AND date = ?'
        ).bind(userId, today).run();
    } else {
        source = 'bonus';
        await env.DB.prepare(
            'UPDATE daily_limits SET bonus_uses = bonus_uses - 1 WHERE user_id = ? AND date = ?'
        ).bind(userId, today).run();
    }

    // 记录使用
    await env.DB.prepare(
        'INSERT INTO finder_usage (user_id, source) VALUES (?, ?)'
    ).bind(userId, source).run();

    // 更新用户总计
    await env.DB.prepare(
        'UPDATE users SET total_finder_uses = total_finder_uses + 1 WHERE id = ?'
    ).bind(userId).run();

    // 返回更新后的剩余次数
    const updatedDaily = await env.DB.prepare(
        'SELECT uses, bonus_uses FROM daily_limits WHERE user_id = ? AND date = ?'
    ).bind(userId, today).first();

    const newRemainingFree = Math.max(0, maxDaily - (updatedDaily?.uses || 0));
    const newRemainingTotal = newRemainingFree + (updatedDaily?.bonus_uses || 0);

    return jsonResponse({
        success: true,
        source: source,
        remaining_free: newRemainingFree,
        remaining_bonus: updatedDaily?.bonus_uses || 0,
        remaining_total: newRemainingTotal,
    });
}

// ============================================
// 工具函数
// ============================================
function getToday() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}
