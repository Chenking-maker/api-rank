/* 全站顶部提醒横幅 —— 由各页面 <script src="assets/notice.js"> 自动注入 */
(function () {
    if (window.__siteNoticeLoaded) return;
    window.__siteNoticeLoaded = true;

    var CSS = [
        '#siteNoticeBanner{position:relative;z-index:1002;background:#4A90D9;color:#fff;',
        'font-weight:600;font-size:13.5px;line-height:1.5;padding:9px 16px;text-align:center;',
        'letter-spacing:.2px;box-shadow:0 2px 10px rgba(74,144,217,.35);',
        'animation:siteNoticeIn .4s ease both}',
        '@keyframes siteNoticeIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}',
        '#siteNoticeBanner .snb-in{max-width:1200px;margin:0 auto;display:flex;align-items:center;',
        'justify-content:center;gap:8px;flex-wrap:wrap}',
        '#siteNoticeBanner .snb-ico{font-size:15px;line-height:1}',
        '#siteNoticeBanner .snb-kbd{background:rgba(255,255,255,.22);padding:1px 8px;border-radius:6px;',
        'font-weight:700;font-family:"JetBrains Mono",Consolas,monospace}',
        '@media(max-width:768px){#siteNoticeBanner{font-size:12px;padding:8px 12px;line-height:1.45}}'
    ].join('');

    function inject() {
        var style = document.createElement('style');
        style.id = 'siteNoticeStyle';
        style.appendChild(document.createTextNode(CSS));
        (document.head || document.documentElement).appendChild(style);

        var bar = document.createElement('div');
        bar.id = 'siteNoticeBanner';
        bar.innerHTML =
            '<div class="snb-in">' +
                '<span class="snb-ico">⚠️</span>' +
                '<span>最近频发中转站换域名、原网址打不开（多数并非跑路），' +
                '本站持续更新各站最新可用网址 —— 建议收藏（<span class="snb-kbd">Ctrl+D</span>）</span>' +
            '</div>';

        var body = document.body;
        if (!body) return;
        if (body.firstChild) body.insertBefore(bar, body.firstChild);
        else body.appendChild(bar);

        // 兼容 fixed 定位导航栏（如首页）：把导航下移到横幅之下，滚动时平滑归位
        // 注意：本脚本可能被放在导航 HTML 之前，需等 DOM 就绪后再查找 .navbar
        var adjustNav = function () {
            var nav = document.querySelector('.navbar');
            if (!nav) return;
            var pos = '';
            try { pos = window.getComputedStyle(nav).position; } catch (e) {}
            if (pos === 'fixed') {
                var h = bar.offsetHeight || 36;
                nav.style.transition = 'none';
                nav.style.top = h + 'px';
                var onScroll = function () {
                    var y = window.scrollY || window.pageYOffset || 0;
                    nav.style.top = Math.max(0, h - y) + 'px';
                };
                window.addEventListener('scroll', onScroll, { passive: true });
                onScroll();
            }
        };
        if (document.querySelector('.navbar')) adjustNav();
        else document.addEventListener('DOMContentLoaded', adjustNav);
    }

    if (document.body) {
        inject();
    } else {
        document.addEventListener('DOMContentLoaded', inject);
    }
})();
