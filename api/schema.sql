-- ============================================
-- API Rank Backend - D1 Database Schema
-- 分享佣金系统数据库建表脚本
-- ============================================

-- 用户表：匿名用户，以 UUID 作为唯一标识
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,          -- 用户 UUID（前端 crypto.randomUUID 生成）
    ip_hash     TEXT,                      -- IP 哈希（防滥用）
    total_finder_uses INTEGER DEFAULT 0,    -- 累计查找次数
    total_referrals   INTEGER DEFAULT 0,    -- 累计推荐成功数
    total_bonus_uses  INTEGER DEFAULT 0,    -- 累计奖励次数
    created_at  TEXT DEFAULT (datetime('now')),
    last_active TEXT DEFAULT (datetime('now'))
);

-- 推荐关系表：记录谁推荐了谁
CREATE TABLE IF NOT EXISTS referrals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id TEXT NOT NULL,              -- 推荐人 ID
    referred_id TEXT NOT NULL,              -- 被推荐人 ID
    share_code  TEXT NOT NULL,              -- 使用的分享码
    bonus_granted INTEGER DEFAULT 0,       -- 是否已发放奖励（0=否，1=是）
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (referrer_id) REFERENCES users(id),
    FOREIGN KEY (referred_id) REFERENCES users(id),
    UNIQUE(referred_id)                     -- 每个用户只能被推荐一次
);

-- 每日限额表：控制每日免费查找次数
CREATE TABLE IF NOT EXISTS daily_limits (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    date        TEXT NOT NULL,              -- 日期 YYYY-MM-DD
    uses        INTEGER DEFAULT 0,          -- 当日已用次数
    bonus_uses INTEGER DEFAULT 0,          -- 当日奖励次数
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, date)                  -- 每用户每天一条记录
);

-- 查找使用记录表
CREATE TABLE IF NOT EXISTS finder_usage (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    used_at     TEXT DEFAULT (datetime('now')),
    source      TEXT DEFAULT 'free',        -- 来源：free / bonus
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 分享奖励记录表
CREATE TABLE IF NOT EXISTS share_rewards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id TEXT NOT NULL,
    referred_id TEXT NOT NULL,
    bonus_uses  INTEGER DEFAULT 1,          -- 奖励的次数
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (referrer_id) REFERENCES users(id),
    FOREIGN KEY (referred_id) REFERENCES users(id)
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_id);
CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON daily_limits(user_id, date);
CREATE INDEX IF NOT EXISTS idx_finder_usage_user ON finder_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_share_rewards_referrer ON share_rewards(referrer_id);
