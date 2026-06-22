// ============================================
// API Rank Backend - Utility Functions
// 工具函数：JWT、短码生成、IP哈希、CORS
// 使用 Web Crypto API（Cloudflare Workers 环境）
// ============================================

/**
 * Base64URL 编码（用于 JWT）
 */
function base64UrlEncode(arrayBuffer) {
    const bytes = new Uint8Array(arrayBuffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}

/**
 * Base64URL 解码
 */
function base64UrlDecode(str) {
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    while (str.length % 4) {
        str += '=';
    }
    return Uint8Array.from(atob(str), c => c.charCodeAt(0));
}

/**
 * 签发 JWT Token
 * @param {object} payload - JWT 载荷 { user_id, exp }
 * @param {string} secret  - HMAC 密钥
 * @param {number} expiresIn - 有效期（秒），默认 30 天
 * @returns {Promise<string>} JWT Token
 */
export async function signJWT(payload, secret, expiresIn = 30 * 24 * 3600) {
    const header = { alg: 'HS256', typ: 'JWT' };
    const now = Math.floor(Date.now() / 1000);

    const headerB64 = base64UrlEncode(new TextEncoder().encode(JSON.stringify(header)));
    const payloadB64 = base64UrlEncode(
        new TextEncoder().encode(JSON.stringify({ ...payload, iat: now, exp: now + expiresIn }))
    );

    const signingInput = `${headerB64}.${payloadB64}`;
    const key = await crypto.subtle.importKey(
        'raw',
        new TextEncoder().encode(secret),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );

    const signature = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(signingInput));
    const signatureB64 = base64UrlEncode(signature);

    return `${signingInput}.${signatureB64}`;
}

/**
 * 验证 JWT Token
 * @param {string} token - JWT Token
 * @param {string} secret - HMAC 密钥
 * @returns {Promise<object|null>} 解码后的载荷，验证失败返回 null
 */
export async function verifyJWT(token, secret) {
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;

        const [headerB64, payloadB64, signatureB64] = parts;
        const signingInput = `${headerB64}.${payloadB64}`;

        const key = await crypto.subtle.importKey(
            'raw',
            new TextEncoder().encode(secret),
            { name: 'HMAC', hash: 'SHA-256' },
            false,
            ['verify']
        );

        const signature = base64UrlDecode(signatureB64);
        const valid = await crypto.subtle.verify(
            'HMAC',
            key,
            signature,
            new TextEncoder().encode(signingInput)
        );

        if (!valid) return null;

        const payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(payloadB64)));
        if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return null;

        return payload;
    } catch (e) {
        return null;
    }
}

/**
 * 生成 8 位分享短码
 * 使用大写字母 + 数字，排除易混淆字符（0/O, 1/I/L）
 * @returns {string} 8 位短码
 */
export function generateShareCode() {
    const chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
    const array = new Uint8Array(8);
    crypto.getRandomValues(array);
    return Array.from(array, b => chars[b % chars.length]).join('');
}

/**
 * IP 哈希函数（SHA-256，用于防滥用，不存储原始 IP）
 * @param {string} ip - 客户端 IP 地址
 * @returns {Promise<string>} SHA-256 哈希前 16 位
 */
export async function hashIP(ip) {
    const data = new TextEncoder().encode(ip + '_api-rank-salt');
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = new Uint8Array(hashBuffer);
    return Array.from(hashArray.slice(0, 8), b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * CORS 响应头
 * @param {Response} response - 原始响应
 * @param {string} origin - 允许的来源
 * @returns {Response} 带 CORS 头的响应
 */
export function corsHeaders(origin = '*') {
    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400',
    };
}

/**
 * 创建带 CORS 头的 JSON 响应
 * @param {object} data - 响应数据
 * @param {number} status - HTTP 状态码
 * @param {string} origin - 允许的来源
 * @returns {Response}
 */
export function jsonResponse(data, status = 200, origin = '*') {
    return new Response(JSON.stringify(data), {
        status,
        headers: {
            'Content-Type': 'application/json',
            ...corsHeaders(origin),
        },
    });
}

/**
 * 创建错误响应
 * @param {string} message - 错误信息
 * @param {number} status - HTTP 状态码
 * @param {string} origin - 允许的来源
 * @returns {Response}
 */
export function errorResponse(message, status = 400, origin = '*') {
    return jsonResponse({ error: message }, status, origin);
}

/**
 * 从请求中提取客户端 IP
 * @param {Request} request - 请求对象
 * @returns {string} IP 地址
 */
export function getClientIP(request) {
    return request.headers.get('CF-Connecting-IP') ||
           request.headers.get('X-Forwarded-For')?.split(',')[0]?.trim() ||
           request.headers.get('X-Real-IP') ||
           'unknown';
}
