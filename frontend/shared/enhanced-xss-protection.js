/**
 * 強化版XSS保護ユーティリティ
 * 医療情報システムに適したセキュリティレベル
 */

class XSSProtection {
    /**
     * より包括的な危険コンテンツチェック
     */
    static containsDangerousContent(str) {
        if (typeof str !== 'string') return false;
        
        // より包括的なXSSパターン
        const dangerousPatterns = [
            /<script[^>]*>/i,
            /<iframe[^>]*>/i,
            /javascript:/i,
            /data:text\/html/i,
            /vbscript:/i,
            /on\w+\s*=/i,
            /<object[^>]*>/i,
            /<embed[^>]*>/i,
            /<applet[^>]*>/i,
            /<meta[^>]*>/i,
            /<link[^>]*>/i,
            /<style[^>]*>/i,
            /expression\s*\(/i,
            /import\s+/i
        ];
        
        // URLエンコードされた攻撃パターンも検出
        try {
            const decoded = decodeURIComponent(str);
            const doubleDecoded = decodeURIComponent(decoded);
            
            return dangerousPatterns.some(pattern => 
                pattern.test(str) || 
                pattern.test(decoded) || 
                pattern.test(doubleDecoded)
            );
        } catch (e) {
            // デコードエラーは危険と判断
            return true;
        }
    }
    
    /**
     * HTMLエンティティエスケープ
     */
    static escapeHtml(str) {
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '/': '&#x2F;'
        };
        
        return str.replace(/[&<>"'\/]/g, char => escapeMap[char]);
    }
    
    /**
     * 属性値の安全な設定
     */
    static setSafeAttribute(element, attribute, value) {
        if (this.containsDangerousContent(value)) {
            console.warn(`[Security] Blocked dangerous content in ${attribute}: ${value}`);
            return false;
        }
        
        // イベントハンドラ属性をブロック
        if (attribute.toLowerCase().startsWith('on')) {
            console.warn(`[Security] Blocked event handler attribute: ${attribute}`);
            return false;
        }
        
        element.setAttribute(attribute, this.escapeHtml(value));
        return true;
    }
    
    /**
     * 安全なテキスト設定
     */
    static setSafeText(element, text) {
        if (this.containsDangerousContent(text)) {
            console.warn('[Security] Blocked dangerous content in text');
            element.textContent = '[危険なコンテンツが検出されました]';
            return false;
        }
        
        element.textContent = text;
        return true;
    }
}

// グローバルに公開
window.XSSProtection = XSSProtection;